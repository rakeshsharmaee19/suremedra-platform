"""Outgoing email: queue a row in EmailLog, then deliver it from a background task.

Because the log row is written first, an email problem can never lose an enquiry or invoice,
and every failure is visible (and retryable) in the admin.
"""
import logging

from django.db import transaction

from .models import EmailLog
from .utils import mask_email

logger = logging.getLogger(__name__)


def queue_email(*, kind, to_email, subject, body_text, attachment_name="", attachment_filename="",
                related_enquiry_id=None, related_invoice_id=None) -> EmailLog:
    log = EmailLog.objects.create(
        kind=kind,
        to_email=to_email,
        subject=subject[:250],
        body_text=body_text,
        attachment_name=attachment_name,
        attachment_filename=attachment_filename,
        related_enquiry_id=related_enquiry_id,
        related_invoice_id=related_invoice_id,
    )
    logger.info("Email queued: id=%s kind=%s to=%s", log.pk, kind, mask_email(to_email))
    from .tasks import deliver_email

    # Only enqueue once the surrounding database transaction has committed.
    transaction.on_commit(lambda: deliver_email.delay(log.pk))
    return log
