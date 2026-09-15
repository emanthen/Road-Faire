from rest_framework import serializers


class LeadSerializer(serializers.Serializer):
    email = serializers.EmailField()
    source = serializers.CharField(required=False, allow_blank=True, default="")
    # Honeypot: a hidden field real users never fill in. Any non-empty value here means
    # this is a bot, not a genuine signup.
    website = serializers.CharField(required=False, allow_blank=True, default="")
