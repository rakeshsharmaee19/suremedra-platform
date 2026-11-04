from rest_framework import serializers

from catalog.models import Composition, Formulation, MedicineType

# IMPORTANT: public serializers list their fields explicitly. Brand, distributor, price
# and any other admin-only data must never be added here.


class MedicineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineType
        fields = ("id", "name", "slug")


class FormulationListSerializer(serializers.ModelSerializer):
    medicine_type = MedicineTypeSerializer(read_only=True)
    compositions = serializers.SerializerMethodField()

    class Meta:
        model = Formulation
        fields = ("id", "slug", "display_name", "medicine_type", "compositions")

    def get_compositions(self, obj) -> list:
        return obj.components


class FormulationDetailSerializer(FormulationListSerializer):
    class Meta(FormulationListSerializer.Meta):
        fields = FormulationListSerializer.Meta.fields + ("description", "is_indexable")


class CompositionSuggestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ("name", "slug")
