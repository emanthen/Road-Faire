"""DRF serializers for TripRequest / Itinerary."""

from decimal import Decimal

from rest_framework import serializers


class PlanRequestSerializer(serializers.Serializer):
    origin_airport = serializers.CharField(max_length=4)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    adults = serializers.IntegerField(min_value=1)
    children = serializers.IntegerField(min_value=0, default=0)
    budget_usd = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_us_resident = serializers.BooleanField()
    vehicle_pref = serializers.ChoiceField(choices=["car", "van"])
    vibe_tags = serializers.ListField(child=serializers.CharField(), default=list)
    max_drive_hours_per_day = serializers.DecimalField(max_digits=4, decimal_places=1)

    def validate(self, data):
        if data["end_date"] <= data["start_date"]:
            raise serializers.ValidationError("end_date must be after start_date.")
        return data


class LoopStopActivitySerializer(serializers.Serializer):
    name = serializers.CharField()
    kind = serializers.CharField()


class LoopStopSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    nights = serializers.IntegerField()
    standard_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    fee_type = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    activities = LoopStopActivitySerializer(many=True)


class LoopSerializer(serializers.Serializer):
    stops = LoopStopSerializer(many=True)
    total_miles = serializers.DecimalField(max_digits=8, decimal_places=1)
    days = serializers.IntegerField()
    month_score = serializers.IntegerField()


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


class EntryPassRecommendationSerializer(serializers.Serializer):
    cheaper = serializers.CharField()
    savings = serializers.DecimalField(max_digits=10, decimal_places=2)
    explanation = serializers.CharField()


class CostBreakdownSerializer(serializers.Serializer):
    transport = serializers.DecimalField(max_digits=10, decimal_places=2)
    lodging = serializers.DecimalField(max_digits=10, decimal_places=2)
    entry = serializers.DecimalField(max_digits=10, decimal_places=2)
    fuel = serializers.DecimalField(max_digits=10, decimal_places=2)
    food = serializers.DecimalField(max_digits=10, decimal_places=2)
    activities = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    buffer = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    entry_annual_pass_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    entry_recommendation = EntryPassRecommendationSerializer()
    estimated_categories = serializers.ListField(child=serializers.CharField())
    lodging_range = serializers.SerializerMethodField()
    transport_range = serializers.SerializerMethodField()

    def _range(self, value):
        if value is None:
            return None
        low, high = value
        cents = Decimal("0.01")
        return {"low": str(low.quantize(cents)), "high": str(high.quantize(cents))}

    def get_lodging_range(self, obj):
        return self._range(obj.lodging_range)

    def get_transport_range(self, obj):
        return self._range(obj.transport_range)
    van_breakdown = VanCostBreakdownSerializer(allow_null=True)


class TripOptionSerializer(serializers.Serializer):
    tier = serializers.CharField()
    loop = LoopSerializer()
    cost = CostBreakdownSerializer()


class TripSummarySerializer(serializers.Serializer):
    """The request's own inputs, echoed back — lets the results page show what was
    actually asked for (dates, party size, vehicle) instead of just the priced options."""

    origin_airport = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    adults = serializers.IntegerField()
    children = serializers.IntegerField()
    vehicle_pref = serializers.CharField()
    is_us_resident = serializers.BooleanField()


class PlanResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    request = TripSummarySerializer()
    options = TripOptionSerializer(many=True)


class WaypointSerializer(serializers.Serializer):
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_mi = serializers.FloatField()


class LegWaypointsSerializer(serializers.Serializer):
    from_name = serializers.CharField()
    to_name = serializers.CharField()
    fuel = WaypointSerializer(allow_null=True)
    restaurant = WaypointSerializer(allow_null=True)
    source_url = serializers.CharField()


class TierWaypointsSerializer(serializers.Serializer):
    tier = serializers.CharField()
    legs = LegWaypointsSerializer(many=True)


class FeaturedTripSerializer(serializers.Serializer):
    """A lightweight teaser for /trips — the LEAN tier's headline numbers, not the
    full nested itinerary (that's what GET /api/plan/<id> is for)."""

    id = serializers.UUIDField(source="public_id")
    origin_airport = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    destinations = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    from_total = serializers.SerializerMethodField()

    def _lean(self, obj):
        return next((i for i in obj.itineraries.all() if i.tier == "LEAN"), None)

    def get_destinations(self, obj):
        lean = self._lean(obj)
        if lean is None:
            return []
        return [
            stop.spot.name for day in lean.days.all() for stop in day.stops.all()
        ]

    def get_days(self, obj):
        lean = self._lean(obj)
        return lean.total_days if lean else 0

    def get_from_total(self, obj):
        lean = self._lean(obj)
        return str(lean.total_cost) if lean else None
