import logging
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from core.emailing import queue_email
from core.sequences import next_number
from core.utils import mask_email

from .models import Enquiry, EnquiryItem, Notification

logger = logging.getLogger(__name__)


def get_notification_recipients():
    """Active users in the Admin / SuperAdmin groups (or superusers) with an email address."""
    User = get_user_model()
    return list(
        User.objects.filter(is_active=True, is_staff=True)
        .filter(Q(groups__name__in=["Admin", "SuperAdmin"]) | Q(is_superuser=True))
        .distinct()
    )


def _alert_emails(users):
    emails = {u.email.lower(): u.email for u in users if u.email}
    for extra in settings.ADMIN_NOTIFICATION_EMAILS:
        emails.setdefault(extra.lower(), extra)
    return list(emails.values())


def create_enquiry(*, buyer: dict, items: list, ip=None, user_agent="", idempotency_key=None) -> Enquiry:
    """Save an enquiry, notify admins (in-app + email) and acknowledge the buyer.

    Everything is written in one transaction. Emails are only handed to the background
    worker after the commit, so a mail problem can never lose the enquiry.
    """
    if idempotency_key:
        existing = Enquiry.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            logger.info("Duplicate enquiry submission ignored: %s", existing.reference)
            return existing

    with transaction.atomic():
        year = timezone.localdate().year
        number = next_number(f"enquiry:{year}")
        enquiry = Enquiry.objects.create(
            reference=f"ENQ-{year}-{number:04d}",
            buyer_name=buyer["name"],
            buyer_company=buyer.get("company", ""),
            buyer_email=buyer["email"],
            buyer_phone=buyer.get("phone", ""),
            buyer_country=buyer.get("country", ""),
            message=buyer.get("message", ""),
            idempotency_key=idempotency_key,
            ip_address=ip or None,
            user_agent=(user_agent or "")[:300],
        )
        EnquiryItem.objects.bulk_create(
            EnquiryItem(
                enquiry=enquiry,
                formulation=item["formulation"],
                requested_quantity=item["quantity"],
                requested_unit=item.get("unit", ""),
            )
            for item in items
        )
        _notify(enquiry)

    logger.info(
        "Enquiry created: %s items=%s country=%s buyer=%s",
        enquiry.reference, len(items), enquiry.buyer_country or "-", mask_email(enquiry.buyer_email),
    )
    return enquiry


def _notify(enquiry: Enquiry):
    recipients = get_notification_recipients()
    item_count = enquiry.items.count()
    title = f"New enquiry {enquiry.reference} from {enquiry.buyer_name}"
    body = f"{enquiry.buyer_company or 'No company'} ({enquiry.buyer_country or 'country not given'}), {item_count} item(s)"

    Notification.objects.bulk_create(
        Notification(user=user, enquiry=enquiry, title=title, body=body) for user in recipients
    )
    logger.info("In-app notifications created for %s user(s)", len(recipients))

    admin_link = f"{settings.ADMIN_URL.rstrip('/')}/admin/enquiries/enquiry/{enquiry.pk}/change/"
    lines = "\n".join(
        f"  - {i.formulation.display_name}: {i.requested_quantity} {i.requested_unit}".rstrip()
        for i in enquiry.items.select_related("formulation")
    )
    alert_body = (
        f"{title}\n\n"
        f"Buyer: {enquiry.buyer_name}\nCompany: {enquiry.buyer_company}\n"
        f"Email: {enquiry.buyer_email}\nPhone: {enquiry.buyer_phone}\nCountry: {enquiry.buyer_country}\n\n"
        f"Requested items:\n{lines}\n\nMessage:\n{enquiry.message or '-'}\n\n"
        f"Open in the admin: {admin_link}\n"
    )
    emails = _alert_emails(recipients)
    if not emails:
        logger.warning("No admin recipients configured; enquiry %s has no email alert", enquiry.reference)
    for email in emails:
        queue_email(
            kind="enquiry_admin_alert", to_email=email, subject=title, body_text=alert_body,
            related_enquiry_id=enquiry.pk,
        )

    ack = (
        f"Dear {enquiry.buyer_name},\n\n"
        f"Thank you for your enquiry. Your reference number is {enquiry.reference}.\n"
        f"We will check availability and reply to you shortly.\n\n"
        f"Regards,\n{settings.COMPANY['name']}\n"
    )
    queue_email(
        kind="enquiry_ack", to_email=enquiry.buyer_email,
        subject=f"We received your enquiry {enquiry.reference}", body_text=ack, related_enquiry_id=enquiry.pk,
    )
