"""Flat, writable ModelSerializers for the staff-only /api/admin/ dashboard API.

Deliberately not the same serializers as the public read-only API (apps.catalog,
apps.partners, apps.content) — those are nested/read-optimized for the site's public
pages. These are flat so DRF's default create/update just works, with each of Spot's
children (cost, reservation rules, vehicle limits, photos) managed as its own
resource rather than a nested-writable list.
"""

from django.contrib.gis.geos import Point
from rest_framework import serializers

from apps.catalog.models import (
    Photo,
    ReservationRule,
    Spot,
    SpotCost,
    State,
    VehicleLimit,
)
from apps.content.models import FAQ, Page, SiteSettings
from apps.partners.models import Offer, Partner


class SpotAdminSerializer(serializers.ModelSerializer):
    """Spot.geom is a GeoDjango PointField — not JSON-friendly, so it's replaced here
    with plain latitude/longitude floats on the way in and out."""

    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)

    class Meta:
        model = Spot
        fields = [
            "id", "name", "slug", "state", "type", "min_days", "vibe_tags",
            "nearest_airports", "blurb", "elevation_ft", "best_time_to_visit",
            "highlights", "meta_title", "meta_description", "contact_phone",
            "latitude", "longitude",
            "source_url", "verified_at", "is_manually_verified", "needs_verification",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["latitude"] = instance.geom.y
        data["longitude"] = instance.geom.x
        return data

    def create(self, validated_data: dict) -> Spot:
        latitude = validated_data.pop("latitude")
        longitude = validated_data.pop("longitude")
        validated_data["geom"] = Point(longitude, latitude)
        return super().create(validated_data)

    def update(self, instance: Spot, validated_data: dict) -> Spot:
        # A PATCH may omit latitude/longitude entirely — only rebuild geom when the
        # caller actually sent a new coordinate pair.
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        if latitude is not None and longitude is not None:
            validated_data["geom"] = Point(longitude, latitude)
        return super().update(instance, validated_data)


class StateAdminSerializer(serializers.ModelSerializer):
    """Read-only — just enough to populate the Spot form's state dropdown."""

    class Meta:
        model = State
        fields = ["id", "name", "abbreviation", "region"]


class SpotCostAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotCost
        fields = [
            "id", "spot", "entry_vehicle", "entry_person", "parking",
            "campsite_low", "campsite_high", "shuttle",
            "source_url", "verified_at", "is_manually_verified", "needs_verification",
        ]
        read_only_fields = ["id"]

    def validate_spot(self, value: Spot) -> Spot:
        existing = SpotCost.objects.filter(spot=value)
        if self.instance is not None:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("This spot already has a cost record.")
        return value


class ReservationRuleAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationRule
        fields = [
            "id", "spot", "kind", "season_start", "season_end", "window_start",
            "window_end", "booking_url", "processing_fee", "notes",
            "source_url", "verified_at", "is_manually_verified", "needs_verification",
        ]
        read_only_fields = ["id"]


class VehicleLimitAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLimit
        fields = [
            "id", "spot", "max_length_ft", "max_height_ft", "max_weight_lb",
            "effective_from", "applies_to_roads",
            "source_url", "verified_at", "is_manually_verified", "needs_verification",
        ]
        read_only_fields = ["id"]


class PhotoAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            "id", "spot", "source", "credit", "license", "s3_key", "alt_text",
            "caption", "is_primary", "sort_order",
        ]
        read_only_fields = ["id"]


class PartnerAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = [
            "id", "name", "slug", "service_area", "contact_phone", "terms_note",
            "rating", "rating_count", "rating_source", "rating_url",
            "source_url", "verified_at", "is_manually_verified", "needs_verification",
        ]
        read_only_fields = ["id"]


class OfferAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            "id", "partner", "category", "base_url", "tracking_params",
            "commission_note", "description", "price_note",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "id", "title", "slug", "body", "published",
            "meta_title", "meta_description", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FAQAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "order"]
        read_only_fields = ["id"]


class SiteSettingsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "id", "site_name", "tagline", "logo_url", "twitter_url",
            "instagram_url", "contact_email",
        ]
        read_only_fields = ["id"]
