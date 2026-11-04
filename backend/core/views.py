import logging

from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health(request):
    """Used by Docker / uptime monitors. Returns 503 if the database is unreachable."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        logger.exception("Health check failed: database unreachable")
        return JsonResponse({"status": "error", "database": "down"}, status=503)
    return JsonResponse({"status": "ok", "database": "up"})
