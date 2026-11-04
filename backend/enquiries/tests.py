from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.tests import make_medicine
from core.models import EmailLog
from enquiries.models import Enquiry, Notification

User = get_user_model()


@override_settings(ADMIN_NOTIFICATION_EMAILS=["extra@example.com"], EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EnquiryApiTests(TestCase):
    def setUp(self):
        cache.clear()  # reset the rate limiter between tests
        self.admin = User.objects.create_user("boss", "boss@example.com", "pw", is_staff=True, is_superuser=True)
        self.med = make_medicine("Crocin", "GSK", "Tablet", [("Paracetamol", "500", "mg")])
        self.slug = self.med.formulation.slug
        self.url = reverse("public-enquiry-create")

    def payload(self, **extra):
        data = {
            "name": "Amina", "company": "Lagos Pharma", "email": "amina@example.com", "country": "Nigeria",
            "message": "Need 5000 strips", "items": [{"formulation": self.slug, "quantity": 5000, "unit": "strips"}],
        }
        data.update(extra)
        return data

    def post(self, data):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(self.url, data, content_type="application/json")

    def test_enquiry_creates_notifications_and_emails(self):
        resp = self.post(self.payload())
        self.assertEqual(resp.status_code, 201)
        ref = resp.json()["reference"]
        self.assertRegex(ref, r"^ENQ-\d{4}-0001$")
        enquiry = Enquiry.objects.get(reference=ref)
        self.assertEqual(enquiry.items.count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.admin, enquiry=enquiry).count(), 1)
        recipients = sorted(m.to[0] for m in mail.outbox)
        self.assertEqual(recipients, ["amina@example.com", "boss@example.com", "extra@example.com"])
        self.assertEqual(EmailLog.objects.filter(status="sent").count(), 3)

    def test_reference_numbers_increase(self):
        self.post(self.payload())
        ref2 = self.post(self.payload(email="b@example.com")).json()["reference"]
        self.assertTrue(ref2.endswith("0002"))

    def test_honeypot_discards_silently(self):
        resp = self.post(self.payload(website="http://spam"))
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Enquiry.objects.count(), 0)

    def test_idempotency_key_prevents_duplicates(self):
        key = "6f2d6b0e-1c0a-4a39-9d34-5b2a7f1d9a11"
        first = self.post(self.payload(idempotency_key=key)).json()["reference"]
        second = self.post(self.payload(idempotency_key=key)).json()["reference"]
        self.assertEqual(first, second)
        self.assertEqual(Enquiry.objects.count(), 1)

    def test_validation(self):
        self.assertEqual(self.post(self.payload(items=[])).status_code, 400)
        self.assertEqual(self.post(self.payload(email="not-an-email")).status_code, 400)
        bad = self.payload(items=[{"formulation": "unknown", "quantity": 1}])
        self.assertEqual(self.post(bad).status_code, 400)
        dup = self.payload(items=[{"formulation": self.slug, "quantity": 1}, {"formulation": self.slug, "quantity": 2}])
        self.assertEqual(self.post(dup).status_code, 400)

    @override_settings(TURNSTILE_SECRET_KEY="secret")
    def test_captcha_required_when_configured(self):
        self.assertEqual(self.post(self.payload()).status_code, 400)
