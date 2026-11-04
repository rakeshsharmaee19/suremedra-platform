import logging

from celery import shared_task

from .models import Invoice
from .services import attach_pdf_and_email

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, max_retries=3)
def render_and_send_invoice(self, invoice_id: int):
    invoice = Invoice.objects.select_related("enquiry").get(pk=invoice_id)
    logger.info("Rendering invoice %s (attempt %s)", invoice.number, self.request.retries + 1)
    attach_pdf_and_email(invoice)
