"""POST /api/plan, GET /api/plan/<uuid>."""

from decimal import Decimal

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.catalog.models import Spot
from apps.planner.engine.budget import build_trip_options
from apps.planner.engine.candidates import AIRPORTS, candidate_spots
from apps.planner.engine.clustering import _activities, _entry_fee, _fee_type, build_loops
from apps.planner.engine.types import CostBreakdown, Loop, LoopStop, TripOption
from apps.planner.engine.types import TripRequest as EngineTripRequest
from apps.planner.engine.waypoints import leg_waypoints
from apps.planner.models import CostLine, Itinerary, ItineraryDay, ItineraryStop
from apps.planner.models import TripRequest as TripRequestModel
from apps.planner.pdf import render_itinerary_pdf
from apps.planner.serializers import (
    FeaturedTripSerializer,
    PlanRequestSerializer,
    PlanResponseSerializer,
    TierWaypointsSerializer,
)

COST_CATEGORIES = [
    "transport", "lodging", "entry", "fuel", "food", "activities", "buffer",
]


@api_view(["POST"])
def create_plan(request):
    request_serializer = PlanRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    engine_request = EngineTripRequest(
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

    try:
        candidates = candidate_spots(
            engine_request.origin_airport,
            engine_request.start_date,
            engine_request.max_drive_hours_per_day,
            engine_request.days,
        )
    except ValueError as exc:
        return Response({"error": {"detail": str(exc)}}, status=400)

    loops = build_loops(
        candidates,
        engine_request.origin_airport,
        engine_request.days,
        engine_request.max_drive_hours_per_day,
        engine_request.start_date,
    )
    options = build_trip_options(loops, engine_request)

    if not options:
        detail = (
            "No trips found within your budget and constraints — try a wider budget "
            "or fewer drive-hour limits."
        )
        return Response({"error": {"detail": detail}}, status=404)

    db_request = _persist(engine_request, options)

    return Response(
        PlanResponseSerializer(
            {"id": db_request.public_id, "request": db_request, "options": options}
        ).data,
        status=201,
    )


@api_view(["GET"])
def get_plan(request, plan_id):
    db_request, itineraries = _fetch_plan(plan_id)
    options = [_itinerary_to_option(itinerary) for itinerary in itineraries]

    return Response(
        PlanResponseSerializer(
            {"id": db_request.public_id, "request": db_request, "options": options}
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

    for option in options:
        itinerary = Itinerary.objects.create(
            trip_request=db_request,
            tier=option.tier,
            total_cost=option.cost.total,
            total_miles=option.loop.total_miles,
            total_days=option.loop.days,
        )
        for i, stop in enumerate(option.loop.stops, start=1):
            day = ItineraryDay.objects.create(itinerary=itinerary, day_number=i)
            spot = Spot.objects.get(slug=stop.slug)
            ItineraryStop.objects.create(day=day, spot=spot, nights=stop.nights)
        for category in COST_CATEGORIES:
            amount = getattr(option.cost, category)
            CostLine.objects.create(itinerary=itinerary, category=category, amount=amount)

    return db_request


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

    amounts = {line.category: line.amount for line in itinerary.cost_lines.all()}
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
    )

    return TripOption(tier=itinerary.tier, loop=loop, cost=cost)
