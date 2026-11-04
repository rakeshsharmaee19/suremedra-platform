import shutil
import tempfile
from datetime import date
from decimal import Decimal
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from billing.models import Invoice
from billing.services import InvoiceError, create_invoice, financial_year
from catalog.tests import make_medicine
from enquiries.models import Enquiry, EnquiryItem
from enquiries.services import create_enquiry

try:
    import weasyprint  # noqa: F401
    from weasyprint import HTML

    HTML(string="<p>x</p>").write_pdf()
    PDF_OK = True
except Exception:
    PDF_OK = False

User = get_user_model()
MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InvoiceTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_superuser("boss", "boss@example.com", "pw")
        self.med = make_medicine("Crocin", "GSK", "Tablet", [("Paracetamol", "500", "mg")])
        with self.captureOnCommitCallbacks(execute=True):
            self.enquiry = create_enquiry(
                buyer={"name": "Amina", "company": "Lagos Pharma", "email": "amina@example.com", "country": "Nigeria"},
                items=[{"formulation": self.med.formulation, "quantity": 100, "unit": "strips"}],
            )
        mail.outbox.clear()

    def answer(self, **fields):
        item = self.enquiry.items.get()
        defaults = dict(availability="available", medicine=self.med, unit_price=Decimal("10.00"))
        defaults.update(fields)
        for k, v in defaults.items():
            setattr(item, k, v)
        item.save()

    def test_financial_year(self):
        self.assertEqual(financial_year(date(2026, 3, 31)), "2025-26")
        self.assertEqual(financial_year(date(2026, 4, 1)), "2026-27")

    def test_invoice_needs_billable_lines(self):
        with self.assertRaises(InvoiceError):
            create_invoice(self.enquiry, self.user)

    def test_totals_numbering_and_status(self):
        self.answer()  # 100 x 10.00 = 1000, GST 12% = 120 (medicine default)
        inv = create_invoice(self.enquiry, self.user)
        self.assertEqual((inv.subtotal, inv.tax_total, inv.total), (Decimal("1000.00"), Decimal("120.00"), Decimal("1120.00")))
        self.assertRegex(inv.number, r"^PI/\d{4}-\d{2}/0001$")
        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, Enquiry.Status.QUOTED)
        self.answer(unit_price=Decimal("5"))
        self.assertTrue(create_invoice(self.enquiry, self.user).number.endswith("0002"))

    def test_export_is_zero_rated_and_partial_uses_available_qty(self):
        self.answer(availability="partial", available_quantity=40, gst_rate=Decimal("18"))
        inv = create_invoice(self.enquiry, self.user, tax_treatment=Invoice.TaxTreatment.EXPORT_ZERO)
        self.assertEqual((inv.subtotal, inv.tax_total, inv.total), (Decimal("400.00"), Decimal("0.00"), Decimal("400.00")))
        self.assertEqual(inv.lines.get().quantity, 40)

    def test_partial_requires_quantity(self):
        self.answer(availability="partial")
        with self.assertRaises(InvoiceError):
            create_invoice(self.enquiry, self.user)

    def test_unavailable_lines_excluded(self):
        self.answer(availability="unavailable")
        with self.assertRaises(InvoiceError):
            create_invoice(self.enquiry, self.user)

    @skipUnless(PDF_OK, "WeasyPrint system libraries not available")
    def test_pdf_is_rendered_and_emailed(self):
        self.answer()
        with self.captureOnCommitCallbacks(execute=True):
            inv = create_invoice(self.enquiry, self.user)
        inv.refresh_from_db()
        self.assertTrue(inv.pdf.name.endswith(".pdf"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["amina@example.com"])
        self.assertEqual(mail.outbox[0].attachments[0][2], "application/pdf")
        self.assertEqual(inv.status, Invoice.Status.SENT)


class AdminSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("boss", "boss@example.com", "pw")
        self.client.force_login(self.user)

    def test_admin_pages_load(self):
        for name in ("admin:index", "admin:catalog_medicine_changelist", "admin:catalog_medicine_add",
                     "admin:catalog_medicine_import", "admin:enquiries_enquiry_changelist",
                     "admin:billing_invoice_changelist", "admin:core_emaillog_changelist",
                     "admin:catalog_formulation_changelist"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_generate_invoice_page_and_health(self):
        med = make_medicine("Crocin", "GSK", "Tablet", [("Paracetamol", "500", "mg")])
        enq = create_enquiry(
            buyer={"name": "A", "email": "a@example.com"},
            items=[{"formulation": med.formulation, "quantity": 5, "unit": ""}],
        )
        self.assertEqual(self.client.get(reverse("admin:enquiries_enquiry_change", args=[enq.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:enquiries_enquiry_generate_invoice", args=[enq.pk])).status_code, 200)
        self.assertEqual(self.client.get("/api/health").json()["status"], "ok")
