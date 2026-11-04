import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        if settings.ADMIN_2FA:
            # Require a TOTP code for every Django Admin login.
            from django.contrib import admin
            from django_otp.admin import OTPAdminSite

            admin.site.__class__ = OTPAdminSite
            logger.info("Admin two-factor authentication is ENABLED")
        else:
            logger.warning("Admin two-factor authentication is DISABLED (set ADMIN_2FA=true in production)")
