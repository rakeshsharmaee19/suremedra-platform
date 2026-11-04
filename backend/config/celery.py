import logging
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("suremedra")
app.config_from_object("django.conf:settings", namespace="CELERY")
# Let Django's LOGGING config control log output instead of Celery's own setup.
app.conf.worker_hijack_root_logger = False
app.autodiscover_tasks()

logger = logging.getLogger("celery.app")
