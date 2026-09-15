from decimal import Decimal

from rest_framework import serializers

from apps.vehicles.models import VehicleSpec


class VehicleSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleSpec
        fields = [
            "id",
            "name",
            "vehicle_class",
            "length_ft",
            "height_ft",
            "mpg",
            "sleeps",
            "included_miles_per_night",
            "overage_rate_per_mile",
            "base_nightly_rate",
        ]


class SizeCheckRequestSerializer(serializers.Serializer):
    """Either vehicle_spec_id (a saved rig) or length_ft/height_ft (typed in by hand)."""

    vehicle_spec_id = serializers.IntegerField(required=False)
    length_ft = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    height_ft = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    spot_slug = serializers.CharField()
    travel_date = serializers.DateField()

    def validate(self, data):
        has_spec = "vehicle_spec_id" in data
        has_dims = "length_ft" in data and "height_ft" in data
        if has_spec == has_dims:
            raise serializers.ValidationError(
                "Provide either vehicle_spec_id or both length_ft and height_ft."
            )
        return data


class FitResultSerializer(serializers.Serializer):
    status = serializers.CharField()
    reasons = serializers.ListField(child=serializers.CharField())


class TrueCostRequestSerializer(serializers.Serializer):
    """Raw rental terms typed in by the renter — no fleet catalog assumed, since we
    don't have real per-operator rate data to seed one."""

    nights = serializers.IntegerField(min_value=1)
    planned_miles = serializers.DecimalField(
        max_digits=7, decimal_places=1, min_value=Decimal("0")
    )
    base_nightly_rate = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0")
    )
    included_miles_per_night = serializers.IntegerField(min_value=0, default=0)
    overage_rate_per_mile = serializers.DecimalField(
        max_digits=6, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )
    prep_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )
    insurance_per_night = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )
    one_way = serializers.BooleanField(default=False)
    one_way_fee = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )
    generator_hours = serializers.DecimalField(
        max_digits=6, decimal_places=1, min_value=Decimal("0"), default=Decimal("0")
    )
    generator_rate_per_hour = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )
    hookup_nights = serializers.IntegerField(min_value=0, default=0)
    hookup_premium_per_night = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0"), default=Decimal("0")
    )


class VanCostBreakdownSerializer(serializers.Serializer):
    base = serializers.DecimalField(max_digits=10, decimal_places=2)
    mileage_overage = serializers.DecimalField(max_digits=10, decimal_places=2)
    prep_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    insurance = serializers.DecimalField(max_digits=10, decimal_places=2)
    one_way_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    generator = serializers.DecimalField(max_digits=10, decimal_places=2)
    hookup_premium = serializers.DecimalField(max_digits=10, decimal_places=2)
    addons = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
