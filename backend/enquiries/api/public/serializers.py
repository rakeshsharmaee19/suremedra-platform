from rest_framework import serializers

from catalog.models import Formulation


class EnquiryItemInputSerializer(serializers.Serializer):
    formulation = serializers.SlugRelatedField(slug_field="slug", queryset=Formulation.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=10_000_000)
    unit = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")

    def validate_formulation(self, value):
        if not value.medicines.filter(is_active=True).exists():
            raise serializers.ValidationError("This product is not available for enquiry.")
        return value


class EnquiryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    company = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    country = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    message = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    items = EnquiryItemInputSerializer(many=True, allow_empty=False, max_length=50)
    idempotency_key = serializers.UUIDField(required=False, allow_null=True, default=None)
    turnstile_token = serializers.CharField(required=False, allow_blank=True, default="")
    website = serializers.CharField(required=False, allow_blank=True, default="")  # honeypot: humans leave this empty

    def validate_items(self, items):
        slugs = [i["formulation"].slug for i in items]
        if len(slugs) != len(set(slugs)):
            raise serializers.ValidationError("Each product can only appear once.")
        return items
