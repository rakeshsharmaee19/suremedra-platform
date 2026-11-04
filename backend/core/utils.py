from django.conf import settings


def get_client_ip(request) -> str:
    """Best-effort client IP. Behind Caddy set NUM_PROXIES=1 so X-Forwarded-For is trusted."""
    num_proxies = settings.NUM_PROXIES
    if num_proxies:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if len(parts) >= num_proxies:
            return parts[-num_proxies]
    return request.META.get("REMOTE_ADDR", "")


def mask_email(email: str) -> str:
    """a***@example.com - keep personal data out of log files."""
    if not email or "@" not in email:
        return "***"
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"
