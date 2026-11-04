import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from core.emailing import queue_email
from core.sequences import next_number
from enquiries.models import Enquiry, EnquiryItem

from .models import Invoice, InvoiceLine

logger = logging.getLogger(__name__)

TWO = Decimal("0.01")
PREFIX = {Invoice.DocType.PROFORMA: "PI", Invoice.DocType.TAX: "INV"}


class InvoiceError(Exception):
    """Raised with a message that is safe to show to the admin user."""


def money(value) -> Decimal:
    return Decimal(value).quantize(TWO, rounding=ROUND_HALF_UP)


def financial_year(d: date) -> str:
    """Indian financial year (April to March), e.g. 2026-27."""
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def billable_items(enquiry: Enquiry):
    return [
        i for i in enquiry.items.select_related("medicine__brand", "formulation")
        if i.availability in (EnquiryItem.Availability.AVAILABLE, EnquiryItem.Availability.PARTIAL)
        and i.medicine_id and i.unit_price is not None
    ]


def calculate_lines(enquiry: Enquiry, tax_treatment: str):
    """Return (lines_data, subtotal, tax_total, total). Used for the preview and the real invoice."""
    items = billable_items(enquiry)
    if not items:
        raise InvoiceError(
            "No billable lines. Mark at least one item as Available or Partially available, "
            "choose the medicine you will supply, and enter a unit price."
        )
    lines, subtotal, tax_total = [], Decimal("0"), Decimal("0")
    for item in items:
        qty = item.available_quantity or item.requested_quantity
        if item.availability == EnquiryItem.Availability.PARTIAL and not item.available_quantity:
            raise InvoiceError(f"'{item.formulation.display_name}' is partially available: enter the available quantity.")
        rate = item.gst_rate if item.gst_rate is not None else item.medicine.gst_rate
        if tax_treatment == Invoice.TaxTreatment.EXPORT_ZERO:
            rate = Decimal("0")
        line_sub = money(item.unit_price * qty)
        tax = money(line_sub * rate / 100)
        lines.append({
            "medicine": item.medicine,
            "description": f"{item.medicine.product_name} ({item.medicine.brand.name}) - {item.formulation.display_name}"[:400],
            "hsn_code": item.medicine.hsn_code,
            "quantity": qty,
            "unit": item.requested_unit,
            "unit_price": money(item.unit_price),
            "gst_rate": rate,
            "line_subtotal": line_sub,
            "tax_amount": tax,
            "line_total": line_sub + tax,
        })
        subtotal += line_sub
        tax_total += tax
    return lines, subtotal, tax_total, subtotal + tax_total


def create_invoice(enquiry: Enquiry, user, *, doc_type=Invoice.DocType.PROFORMA,
                   tax_treatment=Invoice.TaxTreatment.GST, notes="") -> Invoice:
    lines, subtotal, tax_total, total = calculate_lines(enquiry, tax_treatment)
    now = timezone.now()
    fy = financial_year(timezone.localdate(now))

    with transaction.atomic():
        number = next_number(f"invoice:{doc_type}:{fy}")
        invoice = Invoice.objects.create(
            number=f"{PREFIX[doc_type]}/{fy}/{number:04d}",
            doc_type=doc_type,
            tax_treatment=tax_treatment,
            enquiry=enquiry,
            buyer_name=enquiry.buyer_name,
            buyer_company=enquiry.buyer_company,
            buyer_email=enquiry.buyer_email,
            buyer_phone=enquiry.buyer_phone,
            buyer_country=enquiry.buyer_country,
            buyer_address=enquiry.buyer_address,
            subtotal=subtotal,
            tax_total=tax_total,
            total=total,
            notes=notes,
            issued_by=user if getattr(user, "is_authenticated", False) else None,
            issued_at=now,
        )
        InvoiceLine.objects.bulk_create(InvoiceLine(invoice=invoice, **line) for line in lines)
        enquiry.status = Enquiry.Status.QUOTED
        enquiry.save(update_fields=["status", "updated_at"])
        transaction.on_commit(lambda: _enqueue_render(invoice.pk))

    logger.info(
        "Invoice issued: %s enquiry=%s total=%s %s by=%s",
        invoice.number, enquiry.reference, invoice.total, invoice.currency,
        getattr(user, "username", "system"),
    )
    return invoice


def _enqueue_render(invoice_id: int):
    from .tasks import render_and_send_invoice

    render_and_send_invoice.delay(invoice_id)


def render_invoice_pdf(invoice: Invoice) -> bytes:
    """Render the invoice HTML template to PDF with WeasyPrint."""
    try:
        from weasyprint import HTML
    except Exception:
        logger.exception("WeasyPrint is not available (missing system libraries?)")
        raise
    html = render_to_string("billing/invoice.html", {
        "invoice": invoice,
        "lines": invoice.lines.all(),
        "company": settings.COMPANY,
    })
    return HTML(string=html).write_pdf()


def attach_pdf_and_email(invoice: Invoice) -> None:
    """Generate the PDF, store it, and queue the email to the buyer."""
    pdf_bytes = render_invoice_pdf(invoice)
    filename = invoice.number.replace("/", "-") + ".pdf"
    invoice.pdf.save(filename, ContentFile(pdf_bytes), save=True)
    logger.info("Invoice PDF stored: %s (%s bytes)", invoice.number, len(pdf_bytes))

    label = invoice.get_doc_type_display()
    body = (
        f"Dear {invoice.buyer_name},\n\n"
        f"Please find attached {label.lower()} {invoice.number} for your enquiry {invoice.enquiry.reference}.\n"
        f"Total: {invoice.currency} {invoice.total}\n\n"
        f"Please reply to this email if you have any questions.\n\n"
        f"Regards,\n{settings.COMPANY['name']}\n"
    )
    queue_email(
        kind="invoice", to_email=invoice.buyer_email,
        subject=f"{label} {invoice.number} - {settings.COMPANY['name']}",
        body_text=body, attachment_name=invoice.pdf.name, attachment_filename=filename,
        related_enquiry_id=invoice.enquiry_id, related_invoice_id=invoice.pk,
    )


def mark_invoice_sent(invoice_id: int) -> None:
    updated = Invoice.objects.filter(pk=invoice_id, status=Invoice.Status.ISSUED).update(
        status=Invoice.Status.SENT, sent_at=timezone.now()
    )
    if updated:
        logger.info("Invoice %s marked as sent", invoice_id)


def void_invoice(invoice: Invoice, user) -> None:
    if invoice.status == Invoice.Status.VOID:
        return
    invoice.status = Invoice.Status.VOID
    invoice.save(update_fields=["status", "updated_at"])
    logger.warning("Invoice VOIDED: %s by=%s", invoice.number, getattr(user, "username", "?"))
