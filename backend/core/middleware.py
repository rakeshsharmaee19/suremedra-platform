import logging
import time
import uuid

from .logging import request_id_var
from .utils import get_client_ip

logger = logging.getLogger("core.request")


class RequestLoggingMiddleware:
    """Assigns a request id (honouring X-Request-ID from the proxy) and logs one line per request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception:
            logger.exception("Unhandled error: %s %s", request.method, request.get_full_path())
            raise
        else:
            elapsed_ms = (time.perf_counter() - started) * 1000
            user = getattr(request, "user", None)
            who = user.get_username() if user is not None and user.is_authenticated else "anonymous"
            level = logging.DEBUG if request.path in ("/api/health",) else logging.INFO
            if response.status_code >= 500:
                level = logging.ERROR
            elif response.status_code >= 400:
                level = logging.WARNING
            logger.log(
                level,
                "%s %s -> %s %.1fms ip=%s user=%s",
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
                get_client_ip(request),
                who,
            )
            response["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)
