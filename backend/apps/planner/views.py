"""POST /api/plan, GET /api/plan/<uuid>."""

import dataclasses
from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.catalog.models import Spot
from apps.fees.dataclasses import PassRecommendation
from apps.fees.repository import load_fee_schedule
from apps.planner.engine.budget import build_trip_options
from apps.planner.engine.candidates import AIRPORTS, candidate_spots
from apps.planner.engine.clustering import _activities, _entry_fee, _fee_type, build_loops
from apps.planner.engine.types import CostBreakdown, Loop, LoopStop, TripOption
from apps.planner.engine.types import TripRequest as EngineTripRequest
from apps.planner.engine.waypoints import leg_waypoints
from apps.planner.fuel import current_fuel_price_per_gallon
from apps.planner.models import CostLine, Itinerary, ItineraryDay, ItineraryStop
from apps.planner.models import TripRequest as TripRequestModel
from apps.planner.narrative import NarrativeInput, generate_narrative
from apps.planner.pdf import render_itinerary_pdf
from apps.planner.rates import load_rate_range
from apps.planner.serializers import (
    FeaturedTripSerializer,
    PlanRequestSerializer,
    PlanResponseSerializer,
    TierWaypointsSerializer,
)
from apps.vehicles.pricing import VanCostBreakdown
from apps.vehicles.repository import load_default_van_spec

COST_CATEGORIES = [
    "transport", "lodging", "entry", "fuel", "food", "activities", "buffer",
]


def _engine_request_from(data: dict) -> EngineTripRequest:
    return EngineTripRequest(
        origin_airport=data["origin_airport"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        adults=data["adults"],
        children=data["children"],
        budget_usd=data["budget_usd"],
        is_us_resident=data["is_us_resident"],
        vehicle_pref=data["vehicle_pref"],
        vibe_tags=data["vibe_tags"],
        max_drive_hours_per_day=data["max_drive_hours_per_day"],
    )


def _engine_request_from_model(db_request: TripRequestModel) -> EngineTripRequest:
    return EngineTripRequest(
        origin_airport=db_request.origin_airport,
        start_date=db_request.start_date,
        end_date=db_request.end_date,
        adults=db_request.adults,
        children=db_request.children,
        budget_usd=db_request.budget_usd,
        is_us_resident=db_request.is_us_resident,
        vehicle_pref=db_request.vehicle_pref,
        vibe_tags=db_request.vibe_tags,
        max_drive_hours_per_day=db_request.max_drive_hours_per_day,
    )


def generate_options(engine_request: EngineTripRequest) -> list[TripOption]:
    """The full STEP 1-5 pipeline for one request — candidates through costed,
    narrated TripOptions. Shared by the synchronous view and the async Celery task
    (apps.planner.tasks.generate_plan_async) so there's exactly one place this runs.
    Raises ValueError for an unknown origin airport; returns [] (not an error) when
    nothing fits the budget/drive-hour constraints."""

    candidates = candidate_spots(
        engine_request.origin_airport,
        engine_request.start_date,
        engine_request.max_drive_hours_per_day,
        engine_request.days,
    )

    loops = build_loops(
        candidates,
        engine_request.origin_airport,
        engine_request.days,
        engine_request.max_drive_hours_per_day,
        engine_request.start_date,
    )
    rates = load_fee_schedule(timezone.now().date())
    van_spec = load_default_van_spec()
    # Rate ranges are per-region — candidates are all within drive radius of one
    # origin, so the first candidate's state is a reasonable single region for the
    # whole ranking pass, resolved once here rather than per-loop inside the engine.
    region = candidates[0].state.abbreviation if candidates else ""
    month = engine_request.start_date.month
    rate_ranges = {
        category: load_rate_range(region, month, category)
        for category in ("campsite", "motel", "car")
    }
    fuel_price = current_fuel_price_per_gallon()
    options = build_trip_options(loops, engine_request, rates, van_spec, rate_ranges, fuel_price)
    return [_with_narrative(option) for option in options]


@api_view(["POST"])
def create_plan(request):
    request_serializer = PlanRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    engine_request = _engine_request_from(request_serializer.validated_data)

    try:
        options = generate_options(engine_request)
    except ValueError as exc:
        return Response({"error": {"detail": str(exc)}}, status=400)

    if not options:
        detail = (
            "No trips found within your budget and constraints — try a wider budget "
            "or fewer drive-hour limits."
        )
        return Response({"error": {"detail": detail}}, status=404)

    db_request = _persist(engine_request, options)

    return Response(
        PlanResponseSerializer(
            {
                "id": db_request.public_id,
                "status": db_request.status,
                "request": db_request,
                "options": options,
            }
        ).data,
        status=201,
    )


@api_view(["POST"])
def create_plan_async(request):
    """Same input contract as create_plan, but returns immediately with a PENDING row
    and enqueues apps.planner.tasks.generate_plan_async — for a request slow enough
    that the caller would rather poll GET /api/plan/<id> than hold a connection open."""
    request_serializer = PlanRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    db_request = TripRequestModel.objects.create(
        origin_airport=data["origin_airport"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        adults=data["adults"],
        children=data["children"],
        budget_usd=data["budget_usd"],
        is_us_resident=data["is_us_resident"],
        vehicle_pref=data["vehicle_pref"],
        vibe_tags=data["vibe_tags"],
        max_drive_hours_per_day=data["max_drive_hours_per_day"],
        status=TripRequestModel.Status.PENDING,
    )

    from apps.planner.tasks import generate_plan_async

    generate_plan_async.delay(db_request.id)

    return Response(
        {"id": db_request.public_id, "status": db_request.status}, status=202
    )


create_plan.cls.throttle_scope = "plan"
create_plan_async.cls.throttle_scope = "plan"


@api_view(["GET"])
def get_plan(request, plan_id):
    db_request, itineraries = _fetch_plan(plan_id)
    # PENDING/RUNNING/FAILED rows have no itineraries yet (or ever, if FAILED) — that's
    # not an error, it's exactly what a poller is asking about.
    options = [_itinerary_to_option(itinerary) for itinerary in itineraries]

    return Response(
        PlanResponseSerializer(
            {
                "id": db_request.public_id,
                "status": db_request.status,
                "request": db_request,
                "options": options,
            }
        ).data
    )


@api_view(["GET"])
def get_plan_waypoints(request, plan_id):
    """Nearest gas station + place to eat per leg, for every tier — a separate, lazy
    endpoint (not folded into get_plan) because it makes live Overpass calls per leg
    and shouldn't slow down or risk failing the core itinerary response."""
    db_request, itineraries = _fetch_plan(plan_id)
    origin_lat, origin_lon = AIRPORTS[db_request.origin_airport]

    results = []
    for itinerary in itineraries:
        stops = [
            (itinerary_stop.spot.name, itinerary_stop.spot.geom.y, itinerary_stop.spot.geom.x)
            for day in itinerary.days.all()
            for itinerary_stop in day.stops.all()
        ]
        points = [("Origin", origin_lat, origin_lon), *stops, ("Origin", origin_lat, origin_lon)]

        legs = []
        for (from_name, lat1, lon1), (to_name, lat2, lon2) in zip(points, points[1:], strict=False):
            waypoints = leg_waypoints(lat1, lon1, lat2, lon2)
            legs.append(
                {
                    "from_name": from_name,
                    "to_name": to_name,
                    "fuel": waypoints.fuel,
                    "restaurant": waypoints.restaurant,
                    "source_url": waypoints.source_url,
                }
            )
        results.append({"tier": itinerary.tier, "legs": legs})

    return Response(TierWaypointsSerializer(results, many=True).data)


@api_view(["GET"])
def list_featured_plans(request):
    trips = TripRequestModel.objects.filter(is_featured=True).prefetch_related(
        "itineraries__days__stops__spot"
    ).order_by("id")
    return Response(FeaturedTripSerializer(trips, many=True).data)


@api_view(["GET"])
def get_plan_pdf(request, plan_id):
    db_request, itineraries = _fetch_plan(plan_id)
    pdf_bytes = render_itinerary_pdf(db_request, list(itineraries))

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="roadfare-trip-{plan_id}.pdf"'
    return response


def _fetch_plan(plan_id):
    db_request = get_object_or_404(TripRequestModel, public_id=plan_id)
    itineraries = db_request.itineraries.prefetch_related(
        "days__stops__spot__cost", "days__stops__spot__activities", "cost_lines"
    ).order_by("id")
    return db_request, itineraries


def _with_narrative(option: TripOption) -> TripOption:
    narrative_input = NarrativeInput(
        tier=option.tier,
        destinations=[stop.name for stop in option.loop.stops],
        days=str(option.loop.days),
        total_miles=str(option.loop.total_miles),
        total_cost=f"${option.cost.total:,.2f}",
        pass_recommendation=option.cost.entry_recommendation.explanation,
    )
    return dataclasses.replace(option, narrative=generate_narrative(narrative_input))


@transaction.atomic
def _persist(engine_request: EngineTripRequest, options: list[TripOption]) -> TripRequestModel:
    db_request = TripRequestModel.objects.create(
        origin_airport=engine_request.origin_airport,
        start_date=engine_request.start_date,
        end_date=engine_request.end_date,
        adults=engine_request.adults,
        children=engine_request.children,
        budget_usd=engine_request.budget_usd,
        is_us_resident=engine_request.is_us_resident,
        vehicle_pref=engine_request.vehicle_pref,
        vibe_tags=engine_request.vibe_tags,
        max_drive_hours_per_day=engine_request.max_drive_hours_per_day,
    )
    persist_itineraries(db_request, options)
    return db_request


@transaction.atomic
def persist_itineraries(db_request: TripRequestModel, options: list[TripOption]) -> None:
    """Creates Itinerary/ItineraryDay/ItineraryStop/CostLine rows for an existing
    TripRequest row — split out from _persist() so apps.planner.tasks.
    generate_plan_async can reuse it on a row it didn't create (that one was created
    up front as PENDING, before generation even started)."""

    for option in options:
        itinerary = Itinerary.objects.create(
            trip_request=db_request,
            tier=option.tier,
            total_cost=option.cost.total,
            total_miles=option.loop.total_miles,
            total_days=option.loop.days,
            entry_annual_pass_total=option.cost.entry_annual_pass_total,
            entry_pass_cheaper=option.cost.entry_recommendation.cheaper,
            entry_pass_savings=option.cost.entry_recommendation.savings,
            entry_pass_explanation=option.cost.entry_recommendation.explanation,
            narrative=option.narrative,
        )
        for i, stop in enumerate(option.loop.stops, start=1):
            day = ItineraryDay.objects.create(itinerary=itinerary, day_number=i)
            spot = Spot.objects.get(slug=stop.slug)
            ItineraryStop.objects.create(day=day, spot=spot, nights=stop.nights)
        ranges = {"transport": option.cost.transport_range, "lodging": option.cost.lodging_range}
        for category in COST_CATEGORIES:
            amount = getattr(option.cost, category)
            line_range = ranges.get(category)
            CostLine.objects.create(
                itinerary=itinerary,
                category=category,
                amount=amount,
                is_estimate=category in option.cost.estimated_categories,
                range_low=line_range[0] if line_range else None,
                range_high=line_range[1] if line_range else None,
            )
        if option.cost.van_breakdown is not None:
            van = option.cost.van_breakdown
            # dict keys are Category members — annotated str because Django's TextChoices
            # attribute access types as tuple[str, str] to mypy without django-stubs.
            van_lines: dict[str, Decimal] = {
                str(CostLine.Category.VAN_BASE): van.base,
                str(CostLine.Category.VAN_MILEAGE_OVERAGE): van.mileage_overage,
                str(CostLine.Category.VAN_PREP_FEE): van.prep_fee,
                str(CostLine.Category.VAN_INSURANCE): van.insurance,
                str(CostLine.Category.VAN_ONE_WAY_FEE): van.one_way_fee,
                str(CostLine.Category.VAN_GENERATOR): van.generator,
                str(CostLine.Category.VAN_HOOKUP_PREMIUM): van.hookup_premium,
                str(CostLine.Category.VAN_ADDONS): van.addons,
            }
            for category, amount in van_lines.items():
                CostLine.objects.create(itinerary=itinerary, category=category, amount=amount)


def _itinerary_to_option(itinerary: Itinerary) -> TripOption:
    stops = [
        LoopStop(
            slug=itinerary_stop.spot.slug,
            name=itinerary_stop.spot.name,
            standard_fee=_entry_fee(itinerary_stop.spot),
            fee_type=_fee_type(itinerary_stop.spot),
            nights=itinerary_stop.nights,
            latitude=itinerary_stop.spot.geom.y,
            longitude=itinerary_stop.spot.geom.x,
            activities=_activities(itinerary_stop.spot),
            region=itinerary_stop.spot.state.abbreviation,
        )
        for day in itinerary.days.all()
        for itinerary_stop in day.stops.all()
    ]
    loop = Loop(
        stops=stops,
        total_miles=itinerary.total_miles,
        days=itinerary.total_days,
        month_score=0,  # not persisted — a re-fetched plan doesn't need a fresh score
    )

    lines_by_category = {line.category: line for line in itinerary.cost_lines.all()}
    amounts = {category: line.amount for category, line in lines_by_category.items()}
    estimated_categories = frozenset(
        category for category, line in lines_by_category.items() if line.is_estimate
    )

    def _range(category: str) -> tuple[Decimal, Decimal] | None:
        line = lines_by_category.get(category)
        if line is None or line.range_low is None or line.range_high is None:
            return None
        return (line.range_low, line.range_high)

    van_breakdown = None
    if CostLine.Category.VAN_BASE in amounts:
        van_breakdown = VanCostBreakdown(
            base=amounts.get(CostLine.Category.VAN_BASE, Decimal("0")),
            mileage_overage=amounts.get(CostLine.Category.VAN_MILEAGE_OVERAGE, Decimal("0")),
            prep_fee=amounts.get(CostLine.Category.VAN_PREP_FEE, Decimal("0")),
            insurance=amounts.get(CostLine.Category.VAN_INSURANCE, Decimal("0")),
            one_way_fee=amounts.get(CostLine.Category.VAN_ONE_WAY_FEE, Decimal("0")),
            generator=amounts.get(CostLine.Category.VAN_GENERATOR, Decimal("0")),
            hookup_premium=amounts.get(CostLine.Category.VAN_HOOKUP_PREMIUM, Decimal("0")),
            addons=amounts.get(CostLine.Category.VAN_ADDONS, Decimal("0")),
            total=amounts.get("transport", Decimal("0")),
        )

    cost = CostBreakdown(
        transport=amounts.get("transport", Decimal("0")),
        lodging=amounts.get("lodging", Decimal("0")),
        entry=amounts.get("entry", Decimal("0")),
        fuel=amounts.get("fuel", Decimal("0")),
        food=amounts.get("food", Decimal("0")),
        activities=amounts.get("activities", Decimal("0")),
        subtotal=itinerary.total_cost - amounts.get("buffer", Decimal("0")),
        buffer=amounts.get("buffer", Decimal("0")),
        total=itinerary.total_cost,
        entry_annual_pass_total=itinerary.entry_annual_pass_total,
        entry_recommendation=PassRecommendation(
            cheaper=itinerary.entry_pass_cheaper,
            savings=itinerary.entry_pass_savings,
            explanation=itinerary.entry_pass_explanation,
        ),
        van_breakdown=van_breakdown,
        estimated_categories=estimated_categories,
        lodging_range=_range("lodging"),
        transport_range=_range("transport"),
    )

    return TripOption(tier=itinerary.tier, loop=loop, cost=cost, narrative=itinerary.narrative)
