import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    """Log API errors; DRF still builds the normal JSON error response."""
    response = drf_exception_handler(exc, context)
    view = context.get("view").__class__.__name__ if context.get("view") else "?"
    if response is None:
        logger.exception("Unhandled API exception in %s", view)
    elif response.status_code >= 500:
        logger.error("API error %s in %s: %s", response.status_code, view, exc)
    elif response.status_code == 429:
        logger.warning("Request throttled in %s", view)
    else:
        logger.info("API %s in %s: %s", response.status_code, view, exc)
    return response
