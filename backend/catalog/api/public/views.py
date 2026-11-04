import logging

from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Composition, Formulation, MedicineType
from catalog.services.search import search_compositions, search_formulations

from .serializers import (
    CompositionSuggestSerializer, FormulationDetailSerializer, FormulationListSerializer, MedicineTypeSerializer,
)

logger = logging.getLogger(__name__)

cache_short = method_decorator(cache_control(public=True, max_age=60, s_maxage=300), name="dispatch")


def public_formulations():
    """Only formulations that have at least one ACTIVE medicine are public."""
    return (
        Formulation.objects.filter(medicines__is_active=True)
        .select_related("medicine_type")
        .distinct()
    )


class CataloguePagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100


@cache_short
class FormulationListView(ListAPIView):
    """GET /api/v1/public/formulations/?q=&type=&composition=&page="""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = FormulationListSerializer
    pagination_class = CataloguePagination
    throttle_scope = None

    def get_queryset(self):
        qs = public_formulations()
        params = self.request.query_params
        if type_slug := params.get("type"):
            qs = qs.filter(medicine_type__slug=type_slug)
        for comp_slug in params.getlist("composition"):
            qs = qs.filter(compositions__slug=comp_slug)
        if q := params.get("q", "").strip():
            qs = search_formulations(qs, q[:100])
        else:
            qs = qs.order_by("display_name")
        return qs


@cache_short
class FormulationDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = FormulationDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return public_formulations()


@cache_short
class FilterOptionsView(APIView):
    """GET /api/v1/public/filters/  - medicine types with counts (for the filter sidebar)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses={200: dict})
    def get(self, request):
        types = (
            MedicineType.objects.annotate(
                count=Count("formulations", filter=Q(formulations__medicines__is_active=True), distinct=True)
            )
            .filter(count__gt=0)
        )
        data = [{**MedicineTypeSerializer(t).data, "count": t.count} for t in types]
        return Response({"types": data})


@cache_short
class CompositionSuggestView(ListAPIView):
    """GET /api/v1/public/compositions/?q=para  - autocomplete."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = CompositionSuggestSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Composition.objects.filter(formulations__medicines__is_active=True).distinct().order_by("name")
        q = self.request.query_params.get("q", "").strip()
        if not q:
            return qs[:0]
        return search_compositions(qs, q[:60])[:15]
