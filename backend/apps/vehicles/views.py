"""/api/vehicles/, /api/vehicles/size-check, /api/vehicles/true-cost."""

from decimal import Decimal

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.catalog.models import Spot
from apps.vehicles.compatibility import VehicleLimitInput, vehicle_fits
from apps.vehicles.models import VehicleSpec
from apps.vehicles.pricing import VehicleSpecInput, true_cost
from apps.vehicles.serializers import (
    FitResultSerializer,
    SizeCheckRequestSerializer,
    TrueCostRequestSerializer,
    VanCostBreakdownSerializer,
    VehicleSpecSerializer,
)


class VehicleSpecViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VehicleSpec.objects.select_related("vehicle_class").all()
    serializer_class = VehicleSpecSerializer


@api_view(["POST"])
def size_check(request):
    request_serializer = SizeCheckRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    if "vehicle_spec_id" in data:
        spec = VehicleSpec.objects.get(id=data["vehicle_spec_id"])
        length_ft, height_ft = spec.length_ft, spec.height_ft
    else:
        length_ft, height_ft = data["length_ft"], data["height_ft"]

    spot = Spot.objects.prefetch_related("vehicle_limits").get(slug=data["spot_slug"])

    limits = [
        VehicleLimitInput(
            max_length_ft=limit.max_length_ft,
            max_height_ft=limit.max_height_ft,
            effective_from=limit.effective_from,
        )
        for limit in spot.vehicle_limits.all()
    ]

    result = vehicle_fits(length_ft, height_ft, limits, data["travel_date"])
    return Response(FitResultSerializer(result).data)


@api_view(["POST"])
def true_cost_view(request):
    request_serializer = TrueCostRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    spec = VehicleSpecInput(
        length_ft=Decimal("0"),  # not needed for pricing math, only for size_check
        height_ft=Decimal("0"),
        included_miles_per_night=data["included_miles_per_night"],
        overage_rate_per_mile=data["overage_rate_per_mile"],
        base_nightly_rate=data["base_nightly_rate"],
        prep_fee=data["prep_fee"],
        insurance_per_night=data["insurance_per_night"],
        one_way_fee=data["one_way_fee"],
        generator_rate_per_hour=data["generator_rate_per_hour"],
        hookup_premium_per_night=data["hookup_premium_per_night"],
    )
    breakdown = true_cost(
        spec,
        nights=data["nights"],
        planned_miles=data["planned_miles"],
        one_way=data["one_way"],
        generator_hours=data["generator_hours"],
        hookup_nights=data["hookup_nights"],
    )
    return Response(VanCostBreakdownSerializer(breakdown).data)
