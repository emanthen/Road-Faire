from rest_framework import serializers

from apps.partners.models import Offer, Partner


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ["id", "category", "description", "price_note"]


class PartnerSerializer(serializers.ModelSerializer):
    offers = OfferSerializer(many=True, read_only=True)

    class Meta:
        model = Partner
        fields = [
            "name",
            "slug",
            "service_area",
            "contact_phone",
            "terms_note",
            "rating",
            "rating_count",
            "rating_source",
            "rating_url",
            "offers",
            "verified_at",
        ]
