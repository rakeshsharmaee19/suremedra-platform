import logging

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create the Admin and SuperAdmin groups with their permissions (safe to run repeatedly)."

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        super_group, _ = Group.objects.get_or_create(name="SuperAdmin")

        admin_perms = Permission.objects.filter(
            content_type__app_label="catalog"
        ) | Permission.objects.filter(
            content_type__app_label="enquiries", content_type__model__in=["enquiry", "enquiryitem", "notification"]
        ) | Permission.objects.filter(
            content_type__app_label="billing", content_type__model__in=["invoice", "invoiceline"],
            codename__regex=r"^(view|add|change)_",
        ) | Permission.objects.filter(
            content_type__app_label="core", content_type__model="emaillog", codename="view_emaillog"
        )
        # Admins cannot delete catalogue masters; deletion is a SuperAdmin job.
        admin_perms = admin_perms.exclude(codename__startswith="delete_")
        admin_group.permissions.set(admin_perms)

        super_perms = Permission.objects.exclude(content_type__app_label__in=["contenttypes", "sessions"])
        super_group.permissions.set(super_perms)

        logger.info("Roles configured: Admin=%s perms, SuperAdmin=%s perms", admin_perms.count(), super_perms.count())
        self.stdout.write(self.style.SUCCESS(
            f"Groups ready. Admin: {admin_perms.count()} permissions, SuperAdmin: {super_perms.count()} permissions.\n"
            "Add staff users to a group in the admin (and tick 'Staff status')."
        ))
