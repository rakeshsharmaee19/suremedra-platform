from django.conf import settings
from django.db import models

from core.models import TimeStamped


class Enquiry(TimeStamped):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_REVIEW = "in_review", "In review"
        QUOTED = "quoted", "Quoted"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    reference = models.CharField(max_length=30, unique=True, editable=False)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW, db_index=True)

    buyer_name = models.CharField(max_length=150)
    buyer_company = models.CharField(max_length=200, blank=True)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=40, blank=True)
    buyer_country = models.CharField(max_length=100, blank=True)
    buyer_address = models.TextField(blank=True, help_text="Used on the invoice. Ask the buyer if not supplied.")
    message = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_enquiries"
    )
    internal_notes = models.TextField(blank=True)

    idempotency_key = models.UUIDField(null=True, blank=True, unique=True, editable=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True, editable=False)
    user_agent = models.CharField(max_length=300, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.reference} - {self.buyer_name}"


class EnquiryItem(models.Model):
    class Availability(models.TextChoices):
        PENDING = "pending", "Pending"
        AVAILABLE = "available", "Available"
        PARTIAL = "partial", "Partially available"
        UNAVAILABLE = "unavailable", "Unavailable"

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="items")
    formulation = models.ForeignKey("catalog.Formulation", on_delete=models.PROTECT, related_name="enquiry_items")
    requested_quantity = models.PositiveIntegerField()
    requested_unit = models.CharField(max_length=30, blank=True)

    # Filled in by the admin when answering the enquiry
    availability = models.CharField(max_length=12, choices=Availability.choices, default=Availability.PENDING)
    available_quantity = models.PositiveIntegerField(null=True, blank=True)
    medicine = models.ForeignKey(
        "catalog.Medicine", null=True, blank=True, on_delete=models.PROTECT, related_name="enquiry_items",
        help_text="The actual product (brand and distributor) you will supply.",
    )
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gst_rate = models.DecimalField(
        "GST %", max_digits=5, decimal_places=2, null=True, blank=True, help_text="Leave blank to use the medicine's rate."
    )
    notes = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f"{self.formulation} x {self.requested_quantity}"


class Notification(models.Model):
    """In-app notification shown in the admin for Admins and Super Admins."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    enquiry = models.ForeignKey(Enquiry, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    body = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
