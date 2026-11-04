import logging

from django.contrib import admin, messages
from simple_history.admin import SimpleHistoryAdmin

from .models import Invoice, InvoiceLine
from .services import attach_pdf_and_email, void_invoice

logger = logging.getLogger(__name__)


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0
    can_delete = False
    readonly_fields = [f.name for f in InvoiceLine._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(SimpleHistoryAdmin):
    """Issued invoices are read-only. To correct one: void it, then issue a new one from the enquiry."""

    list_display = ("number", "doc_type", "buyer_name", "buyer_company", "total", "currency", "status", "issued_at")
    list_filter = ("status", "doc_type")
    search_fields = ("number", "buyer_name", "buyer_company", "buyer_email", "enquiry__reference")
    inlines = [InvoiceLineInline]
    actions = ["resend_email", "void_selected"]
    readonly_fields = [f.name for f in Invoice._meta.fields]

    def has_add_permission(self, request):
        return False  # created from an enquiry

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Re-generate PDF and email to buyer")
    def resend_email(self, request, queryset):
        for invoice in queryset.exclude(status=Invoice.Status.VOID):
            try:
                attach_pdf_and_email(invoice)
                logger.info("Invoice %s resent by %s", invoice.number, request.user.get_username())
            except Exception as exc:
                logger.exception("Resend failed for %s", invoice.number)
                self.message_user(request, f"{invoice.number}: could not generate PDF ({exc})", messages.ERROR)
        self.message_user(request, "Selected invoices queued for sending.", messages.SUCCESS)

    @admin.action(description="Void selected invoices")
    def void_selected(self, request, queryset):
        if not request.user.has_perm("billing.void_invoice"):
            self.message_user(request, "Only a Super Admin can void invoices.", messages.ERROR)
            return
        for invoice in queryset:
            void_invoice(invoice, request.user)
        self.message_user(request, "Selected invoices voided.", messages.WARNING)
