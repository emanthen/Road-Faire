from rest_framework import serializers

from apps.content.models import FAQ, Page, SiteSettings


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["slug", "title", "body"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["question", "answer"]


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "site_name",
            "tagline",
            "logo_url",
            "twitter_url",
            "instagram_url",
            "contact_email",
        ]
