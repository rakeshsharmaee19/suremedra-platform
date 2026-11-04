import logging

from django import forms
from django.contrib import admin, messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils import timezone

from billing.models import Invoice
from billing.services import InvoiceError, calculate_lines, create_invoice

from .models import Enquiry, EnquiryItem, Notification

logger = logging.getLogger(__name__)


class EnquiryItemInline(admin.TabularInline):
    model = EnquiryItem
    extra = 0
    can_delete = False
    fields = (
        "formulation", "requested_quantity", "requested_unit", "availability",
        "available_quantity", "medicine", "unit_price", "gst_rate", "notes",
    )
    readonly_fields = ("formulation", "requested_quantity", "requested_unit")
    autocomplete_fields = ("medicine",)

    def has_add_permission(self, request, obj=None):
        return False


class InvoiceOptionsForm(forms.Form):
    doc_type = forms.ChoiceField(choices=Invoice.DocType.choices, initial=Invoice.DocType.PROFORMA, label="Document type")
    tax_treatment = forms.ChoiceField(choices=Invoice.TaxTreatment.choices, initial=Invoice.TaxTreatment.GST, label="Tax treatment")
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Notes for the buyer")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("reference", "buyer_name", "buyer_company", "buyer_country", "status", "item_count", "created_at")
    list_filter = ("status", "buyer_country")
    search_fields = ("reference", "buyer_name", "buyer_company", "buyer_email")
    date_hierarchy = "created_at"
    inlines = [EnquiryItemInline]
    actions = ["mark_in_review"]
    change_form_template = "admin/enquiries/enquiry/change_form.html"
    fieldsets = (
        ("Enquiry", {"fields": ("reference", "status", "assigned_to", "created_at")}),
        ("Buyer", {"fields": ("buyer_name", "buyer_company", "buyer_email", "buyer_phone", "buyer_country", "buyer_address")}),
        ("Message and notes", {"fields": ("message", "internal_notes")}),
    )
    readonly_fields = ("reference", "created_at", "buyer_name", "buyer_company", "buyer_email", "buyer_phone", "buyer_country", "message")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_items=Count("items"))

    @admin.display(description="Items", ordering="_items")
    def item_count(self, obj):
        return obj._items

    def has_add_permission(self, request):
        return False  # enquiries come from the public website

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def change_view(self, request, object_id, form_url="", extra_context=None):
        # Opening an enquiry marks this user's notifications for it as read.
        marked = Notification.objects.filter(
            user=request.user, enquiry_id=object_id, read_at__isnull=True
        ).update(read_at=timezone.now())
        if marked:
            logger.info("Notifications marked read: enquiry=%s user=%s", object_id, request.user.get_username())
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Mark selected as In review")
    def mark_in_review(self, request, queryset):
        count = queryset.filter(status=Enquiry.Status.NEW).update(status=Enquiry.Status.IN_REVIEW)
        self.message_user(request, f"{count} enquiry(ies) marked as In review.", messages.SUCCESS)

    def get_urls(self):
        custom = [
            path("<int:pk>/generate-invoice/", self.admin_site.admin_view(self.generate_invoice_view),
                 name="enquiries_enquiry_generate_invoice"),
        ]
        return custom + super().get_urls()

    def generate_invoice_view(self, request, pk):
        enquiry = get_object_or_404(Enquiry, pk=pk)
        change_url = reverse("admin:enquiries_enquiry_change", args=[pk])
        if not request.user.has_perm("billing.add_invoice"):
            messages.error(request, "You do not have permission to generate invoices.")
            return redirect(change_url)

        form = InvoiceOptionsForm(request.POST or None)
        preview, error = None, None
        tax_treatment = (form["tax_treatment"].value() or Invoice.TaxTreatment.GST)
        try:
            lines, subtotal, tax_total, total = calculate_lines(enquiry, tax_treatment)
            preview = {"lines": lines, "subtotal": subtotal, "tax_total": tax_total, "total": total}
        except InvoiceError as exc:
            error = str(exc)

        if request.method == "POST" and form.is_valid() and not error:
            try:
                invoice = create_invoice(
                    enquiry, request.user,
                    doc_type=form.cleaned_data["doc_type"],
                    tax_treatment=form.cleaned_data["tax_treatment"],
                    notes=form.cleaned_data["notes"],
                )
            except InvoiceError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"Invoice {invoice.number} issued. The PDF is being generated and emailed to the buyer.")
                return redirect(reverse("admin:billing_invoice_change", args=[invoice.pk]))

        context = {
            **self.admin_site.each_context(request),
            "title": f"Generate invoice for {enquiry.reference}",
            "opts": self.model._meta,
            "enquiry": enquiry,
            "form": form,
            "preview": preview,
            "error": error,
            "change_url": change_url,
        }
        return render(request, "admin/enquiries/enquiry/generate_invoice.html", context)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "read_at")
    list_filter = ("read_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(user=request.user)

    def has_add_permission(self, request):
        return False
