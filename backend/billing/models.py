from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from core.models import TimeStamped


class Invoice(TimeStamped):
    class DocType(models.TextChoices):
        PROFORMA = "proforma", "Proforma invoice"
        TAX = "tax", "Tax invoice"

    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        SENT = "sent", "Sent to buyer"
        VOID = "void", "Void"

    class TaxTreatment(models.TextChoices):
        GST = "gst", "GST charged"
        EXPORT_ZERO = "export_zero", "Export (zero-rated, no GST charged)"

    number = models.CharField(max_length=40, unique=True, editable=False)
    doc_type = models.CharField(max_length=10, choices=DocType.choices, default=DocType.PROFORMA)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ISSUED, db_index=True)
    tax_treatment = models.CharField(max_length=12, choices=TaxTreatment.choices, default=TaxTreatment.GST)
    enquiry = models.ForeignKey("enquiries.Enquiry", on_delete=models.PROTECT, related_name="invoices")

    # Snapshot of the buyer at the time of issue (later edits to the enquiry do not change it)
    buyer_name = models.CharField(max_length=150)
    buyer_company = models.CharField(max_length=200, blank=True)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=40, blank=True)
    buyer_country = models.CharField(max_length=100, blank=True)
    buyer_address = models.TextField(blank=True)

    currency = models.CharField(max_length=3, default="INR")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    tax_total = models.DecimalField(max_digits=14, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True)

    pdf = models.FileField(upload_to="invoices/", blank=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="issued_invoices")
    issued_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["-issued_at"]
        permissions = [("void_invoice", "Can void an issued invoice")]

    def __str__(self):
        return self.number


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    medicine = models.ForeignKey("catalog.Medicine", null=True, on_delete=models.SET_NULL, related_name="invoice_lines")
    description = models.CharField(max_length=400)
    hsn_code = models.CharField(max_length=12, blank=True)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=30, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    line_subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.description} x {self.quantity}"
