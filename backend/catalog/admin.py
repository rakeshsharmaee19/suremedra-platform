import logging

from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Brand, Composition, Distributor, Formulation, Medicine, MedicineComposition,
    MedicineDistributor, MedicineType,
)
from .services.importer import import_medicines_csv

logger = logging.getLogger(__name__)


@admin.register(MedicineType)
class MedicineTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "sort_order")
    search_fields = ("name",)


@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    list_display = ("name", "aliases")
    search_fields = ("name", "aliases")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer")
    search_fields = ("name", "manufacturer")


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email", "gstin", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "gstin", "drug_license_no")


class MedicineCompositionInline(admin.TabularInline):
    model = MedicineComposition
    extra = 1
    autocomplete_fields = ("composition",)


class MedicineDistributorInline(admin.TabularInline):
    model = MedicineDistributor
    extra = 1
    autocomplete_fields = ("distributor",)


@admin.register(Medicine)
class MedicineAdmin(SimpleHistoryAdmin):
    list_display = ("product_name", "brand", "medicine_type", "pack_size", "formulation", "is_active")
    list_filter = ("medicine_type", "is_active", "brand")
    search_fields = ("product_name", "brand__name", "compositions__composition__name")
    autocomplete_fields = ("brand",)
    readonly_fields = ("formulation",)
    inlines = [MedicineCompositionInline, MedicineDistributorInline]
    list_select_related = ("brand", "medicine_type", "formulation")
    change_list_template = "admin/catalog/medicine/change_list.html"

    def get_urls(self):
        custom = [path("import/", self.admin_site.admin_view(self.import_view), name="catalog_medicine_import")]
        return custom + super().get_urls()

    def import_view(self, request):
        if not self.has_add_permission(request):
            messages.error(request, "You do not have permission to import medicines.")
            return redirect("admin:catalog_medicine_changelist")
        result = None
        if request.method == "POST" and request.FILES.get("csv_file"):
            dry_run = request.POST.get("dry_run") == "on"
            logger.info("CSV import started by %s (dry_run=%s)", request.user.get_username(), dry_run)
            result = import_medicines_csv(request.FILES["csv_file"], dry_run=dry_run)
            verb = "Validated (nothing saved)" if dry_run else "Imported"
            level = messages.SUCCESS if result.ok else messages.WARNING
            messages.add_message(request, level, f"{verb}: {result.created} new, {result.updated} updated, {len(result.errors)} error(s).")
        context = {
            **self.admin_site.each_context(request),
            "title": "Import medicines from CSV",
            "opts": self.model._meta,
            "result": result,
            "changelist_url": reverse("admin:catalog_medicine_changelist"),
        }
        return render(request, "admin/catalog/medicine/import.html", context)


@admin.register(Formulation)
class FormulationAdmin(admin.ModelAdmin):
    """Public listings. Auto-generated; staff only add SEO text and the indexable flag."""

    list_display = ("display_name", "medicine_type", "is_indexable", "has_description")
    list_filter = ("medicine_type", "is_indexable")
    search_fields = ("display_name",)
    fields = ("display_name", "medicine_type", "components", "description", "is_indexable")
    readonly_fields = ("display_name", "medicine_type", "components")

    @admin.display(boolean=True, description="Has description")
    def has_description(self, obj):
        return bool(obj.description.strip())

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
