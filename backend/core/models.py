from django.db import models


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Counter(models.Model):
    """Gap-free counters (enquiry numbers, invoice numbers). See core.sequences."""

    key = models.CharField(max_length=80, unique=True)
    value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.key}={self.value}"


class EmailLog(TimeStamped):
    """Every outgoing email is recorded here, so failures are visible in the admin."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    kind = models.CharField(max_length=40)  # e.g. enquiry_admin_alert, enquiry_ack, invoice
    to_email = models.EmailField()
    subject = models.CharField(max_length=250)
    body_text = models.TextField()
    attachment_name = models.CharField(max_length=300, blank=True)  # path in default storage
    attachment_filename = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    error = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    related_enquiry_id = models.PositiveBigIntegerField(null=True, blank=True)
    related_invoice_id = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.kind} -> {self.to_email} [{self.status}]"
