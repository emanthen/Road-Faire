from rest_framework import serializers


class ParkFeeInputSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    standard_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    fee_type = serializers.ChoiceField(choices=["vehicle", "person"], default="vehicle")


class FeeCalculateRequestSerializer(serializers.Serializer):
    parks = ParkFeeInputSerializer(many=True)
    adults = serializers.IntegerField(min_value=0)
    children = serializers.IntegerField(min_value=0, default=0)
    is_us_resident = serializers.BooleanField()


class EntryFeeLineSerializer(serializers.Serializer):
    park_name = serializers.CharField()
    standard_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    surcharge = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class PassRecommendationSerializer(serializers.Serializer):
    cheaper = serializers.CharField()
    savings = serializers.DecimalField(max_digits=10, decimal_places=2)
    explanation = serializers.CharField()


class EntryFeeBreakdownSerializer(serializers.Serializer):
    lines = EntryFeeLineSerializer(many=True)
    pay_as_you_go_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    annual_pass_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    recommendation = PassRecommendationSerializer()
