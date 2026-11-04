import logging

from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import EmailLog
from .utils import mask_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_backoff_max=1800, max_retries=5)
def deliver_email(self, log_id: int):
    """Send one queued email. Retries with backoff; safe to run twice (skips already-sent rows)."""
    try:
        log = EmailLog.objects.get(pk=log_id)
    except EmailLog.DoesNotExist:
        logger.error("deliver_email: EmailLog %s does not exist", log_id)
        return
    if log.status == EmailLog.Status.SENT:
        logger.info("deliver_email: log %s already sent, skipping", log_id)
        return

    log.attempts += 1
    try:
        message = EmailMessage(
            subject=log.subject,
            body=log.body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[log.to_email],
        )
        if log.attachment_name:
            with default_storage.open(log.attachment_name, "rb") as fh:
                message.attach(log.attachment_filename or "attachment.pdf", fh.read(), "application/pdf")
        message.send(fail_silently=False)
    except Exception as exc:
        log.status = EmailLog.Status.FAILED
        log.error = f"{type(exc).__name__}: {exc}"[:2000]
        log.save(update_fields=["attempts", "status", "error", "updated_at"])
        logger.error(
            "Email delivery failed: id=%s kind=%s to=%s attempt=%s error=%s",
            log.pk, log.kind, mask_email(log.to_email), log.attempts, log.error,
        )
        raise  # triggers the Celery retry

    log.status = EmailLog.Status.SENT
    log.error = ""
    log.sent_at = timezone.now()
    log.save(update_fields=["attempts", "status", "error", "sent_at", "updated_at"])
    logger.info("Email sent: id=%s kind=%s to=%s", log.pk, log.kind, mask_email(log.to_email))

    if log.related_invoice_id:
        from billing.services import mark_invoice_sent

        mark_invoice_sent(log.related_invoice_id)
