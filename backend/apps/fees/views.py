"""POST /api/fees/calculate."""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.fees.dataclasses import ParkFeeInput
from apps.fees.engine import entry_fees
from apps.fees.serializers import EntryFeeBreakdownSerializer, FeeCalculateRequestSerializer


@api_view(["POST"])
def calculate(request):
    request_serializer = FeeCalculateRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    data = request_serializer.validated_data

    parks = [
        ParkFeeInput(
            slug=park["slug"],
            name=park["name"],
            standard_fee=park["standard_fee"],
            fee_type=park["fee_type"],
        )
        for park in data["parks"]
    ]

    breakdown = entry_fees(
        parks,
        adults_16plus=data["adults"],
        is_us_resident=data["is_us_resident"],
        children_under_16=data["children"],
    )

    return Response(EntryFeeBreakdownSerializer(breakdown).data)
