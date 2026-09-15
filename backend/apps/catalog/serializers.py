from rest_framework import serializers

from apps.catalog.models import (
    Activity,
    ClimateNormal,
    CrowdIndex,
    Photo,
    ReservationRule,
    Spot,
    SpotAmenity,
    SpotCost,
    VehicleLimit,
)


class SpotCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotCost
        fields = [
            "entry_vehicle",
            "entry_person",
            "parking",
            "campsite_low",
            "campsite_high",
            "shuttle",
            "source_url",
            "verified_at",
        ]


class ReservationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationRule
        fields = [
            "kind",
            "season_start",
            "season_end",
            "window_start",
            "window_end",
            "booking_url",
            "processing_fee",
            "notes",
            "source_url",
            "verified_at",
        ]


class VehicleLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLimit
        fields = [
            "max_length_ft",
            "max_height_ft",
            "max_weight_lb",
            "effective_from",
            "applies_to_roads",
            "source_url",
            "verified_at",
        ]


class ClimateNormalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateNormal
        fields = ["month", "high_f", "low_f", "precip_in", "snow_in"]


class CrowdIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdIndex
        fields = ["month", "score"]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["name", "kind", "distance_mi", "elevation_gain_ft", "permit_required"]


class SpotAmenitySerializer(serializers.ModelSerializer):
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = SpotAmenity
        fields = ["kind", "longitude", "latitude", "source_url", "verified_at"]

    def get_longitude(self, obj: SpotAmenity) -> float:
        return obj.geom.x

    def get_latitude(self, obj: SpotAmenity) -> float:
        return obj.geom.y


class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="s3_key")

    class Meta:
        model = Photo
        fields = ["url", "alt_text", "caption", "credit", "is_primary"]


class SpotListSerializer(serializers.ModelSerializer):
    state = serializers.CharField(source="state.abbreviation", read_only=True)

    class Meta:
        model = Spot
        fields = ["slug", "name", "type", "state", "min_days", "vibe_tags"]


class SpotDetailSerializer(serializers.ModelSerializer):
    cost = SpotCostSerializer(read_only=True)
    reservation_rules = ReservationRuleSerializer(many=True, read_only=True)
    vehicle_limits = VehicleLimitSerializer(many=True, read_only=True)
    climate_normals = ClimateNormalSerializer(many=True, read_only=True)
    crowd_indexes = CrowdIndexSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    amenities = SpotAmenitySerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    longitude = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()

    class Meta:
        model = Spot
        fields = [
            "slug",
            "name",
            "type",
            "state",
            "min_days",
            "vibe_tags",
            "nearest_airports",
            "blurb",
            "elevation_ft",
            "best_time_to_visit",
            "highlights",
            "meta_title",
            "meta_description",
            "contact_phone",
            "longitude",
            "latitude",
            "cost",
            "reservation_rules",
            "vehicle_limits",
            "amenities",
            "climate_normals",
            "crowd_indexes",
            "activities",
            "photos",
            "verified_at",
            "is_manually_verified",
        ]

    def get_longitude(self, obj: Spot) -> float:
        return obj.geom.x

    def get_latitude(self, obj: Spot) -> float:
        return obj.geom.y
