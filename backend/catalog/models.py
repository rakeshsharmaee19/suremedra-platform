from decimal import Decimal

from django.db import models
from django.db.models.functions import Lower
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

from core.models import TimeStamped


def unique_slug(model, value: str, instance=None, max_length: int = 200) -> str:
    base = (slugify(value) or "item")[: max_length - 6]
    slug, n = base, 2
    qs = model.objects.all()
    if instance is not None and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class MedicineType(TimeStamped):
    """Tablet, Capsule, Syrup, Injection ... (public)."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(MedicineType, self.name, self, 80)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Composition(TimeStamped):
    """An active ingredient, e.g. Paracetamol (public)."""

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    aliases = models.CharField(max_length=300, blank=True, help_text="Other names, comma separated. Used for search.")

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower("name"), name="uniq_composition_name_ci")]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Composition, self.name, self, 170)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(TimeStamped):
    """ADMIN ONLY. Never exposed through the public API."""

    name = models.CharField(max_length=150)
    manufacturer = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower("name"), name="uniq_brand_name_ci")]

    def __str__(self):
        return self.name


class Distributor(TimeStamped):
    """ADMIN ONLY. Never exposed through the public API."""

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    gstin = models.CharField("GSTIN", max_length=20, blank=True)
    drug_license_no = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(Lower("name"), name="uniq_distributor_name_ci")]

    def __str__(self):
        return self.name


class Formulation(TimeStamped):
    """
    The PUBLIC face of a medicine: compositions + strengths + type.

    Derived automatically from Medicine records (see catalog.services.formulation), so two
    brands with the same composition appear as one public listing. Admin only edits the
    SEO description and the indexable flag.
    """

    signature = models.CharField(max_length=40, unique=True, editable=False)
    display_name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=220, unique=True)
    medicine_type = models.ForeignKey(MedicineType, on_delete=models.PROTECT, related_name="formulations")
    compositions = models.ManyToManyField(Composition, related_name="formulations", blank=True)
    components = models.JSONField(default=list, blank=True, editable=False)  # [{name, slug, strength}]
    search_text = models.TextField(blank=True, editable=False)
    description = models.TextField(blank=True, help_text="Public text shown on the page. Helps SEO.")
    is_indexable = models.BooleanField(
        default=True, help_text="Untick to ask Google not to index this page (e.g. until it has a description)."
    )

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class Medicine(TimeStamped):
    """ADMIN ONLY record: a specific product (brand + pack) that Suremedra can supply."""

    product_name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="medicines")
    medicine_type = models.ForeignKey(MedicineType, on_delete=models.PROTECT, related_name="medicines")
    pack_size = models.CharField(max_length=80, blank=True, help_text="e.g. 10x10 tablets, 100 ml")
    hsn_code = models.CharField("HSN code", max_length=12, blank=True)
    gst_rate = models.DecimalField("GST %", max_digits=5, decimal_places=2, default=Decimal("12.00"))
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, help_text="Inactive medicines are hidden from the public site.")
    formulation = models.ForeignKey(
        Formulation, on_delete=models.SET_NULL, null=True, blank=True, editable=False, related_name="medicines"
    )
    distributors = models.ManyToManyField(Distributor, through="MedicineDistributor", related_name="medicines", blank=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["product_name"]
        constraints = [
            models.UniqueConstraint(Lower("product_name"), "brand", "pack_size", name="uniq_medicine_name_brand_pack")
        ]

    def __str__(self):
        return f"{self.product_name} ({self.brand})"


class MedicineComposition(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="compositions")
    composition = models.ForeignKey(Composition, on_delete=models.PROTECT, related_name="medicine_links")
    strength_value = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    strength_unit = models.CharField(max_length=20, blank=True, default="mg", help_text="mg, g, mcg, ml, IU, %, mg/5ml ...")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["medicine", "composition"], name="uniq_medicine_composition")]

    @property
    def strength_display(self) -> str:
        if self.strength_value is None:
            return ""
        value = format(self.strength_value.normalize(), "f")
        return f"{value} {self.strength_unit}".strip()

    def __str__(self):
        return f"{self.composition} {self.strength_display}".strip()


class MedicineDistributor(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    distributor = models.ForeignKey(Distributor, on_delete=models.PROTECT)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["medicine", "distributor"], name="uniq_medicine_distributor")]

    def __str__(self):
        return f"{self.medicine} via {self.distributor}"
