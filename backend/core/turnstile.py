import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile(token: str, remote_ip: str = "") -> bool:
    """Verify a Cloudflare Turnstile token. If no secret is configured the check is skipped."""
    secret = settings.TURNSTILE_SECRET_KEY
    if not secret:
        logger.debug("Turnstile not configured; skipping CAPTCHA check")
        return True
    if not token:
        logger.warning("Turnstile token missing")
        return False
    try:
        resp = requests.post(
            VERIFY_URL, data={"secret": secret, "response": token, "remoteip": remote_ip}, timeout=5
        )
        ok = bool(resp.json().get("success"))
    except Exception:
        logger.exception("Turnstile verification request failed")
        return False  # fail closed
    if not ok:
        logger.warning("Turnstile rejected a token")
    return ok
