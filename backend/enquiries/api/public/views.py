import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.turnstile import verify_turnstile
from core.utils import get_client_ip
from enquiries.services import create_enquiry

from .serializers import EnquiryCreateSerializer

logger = logging.getLogger(__name__)


class EnquiryCreateView(APIView):
    """POST /api/v1/public/enquiries/ - a buyer asks about availability of selected products."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "enquiry"

    @extend_schema(request=EnquiryCreateSerializer, responses={201: dict})
    def post(self, request):
        serializer = EnquiryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ip = get_client_ip(request)

        if data["website"]:
            # Honeypot filled in: almost certainly a bot. Pretend it worked, store nothing.
            logger.warning("Honeypot triggered from ip=%s; enquiry discarded", ip)
            return Response({"reference": "RECEIVED"}, status=status.HTTP_201_CREATED)

        if not verify_turnstile(data["turnstile_token"], ip):
            return Response({"detail": "CAPTCHA verification failed. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        enquiry = create_enquiry(
            buyer={k: data[k] for k in ("name", "company", "email", "phone", "country", "message")},
            items=[{"formulation": i["formulation"], "quantity": i["quantity"], "unit": i["unit"]} for i in data["items"]],
            ip=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            idempotency_key=data["idempotency_key"],
        )
        return Response({"reference": enquiry.reference}, status=status.HTTP_201_CREATED)
