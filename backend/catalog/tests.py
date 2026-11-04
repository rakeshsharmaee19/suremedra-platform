import io
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalog.models import Brand, Composition, Distributor, Formulation, Medicine, MedicineComposition, MedicineType
from catalog.services.importer import import_medicines_csv


def make_medicine(name, brand, type_, comps, active=True, pack=""):
    b, _ = Brand.objects.get_or_create(name=brand)
    t, _ = MedicineType.objects.get_or_create(name=type_)
    m = Medicine.objects.create(product_name=name, brand=b, medicine_type=t, pack_size=pack, is_active=active)
    for cname, value, unit in comps:
        c, _ = Composition.objects.get_or_create(name=cname)
        MedicineComposition.objects.create(medicine=m, composition=c, strength_value=Decimal(value), strength_unit=unit)
    m.refresh_from_db()
    return m


class FormulationTests(TestCase):
    def test_two_brands_share_one_public_formulation(self):
        a = make_medicine("Crocin", "GSK", "Tablet", [("Paracetamol", "500", "mg")])
        b = make_medicine("Calpol", "Other", "Tablet", [("Paracetamol", "500", "mg")])
        self.assertEqual(a.formulation_id, b.formulation_id)
        self.assertEqual(Formulation.objects.count(), 1)
        self.assertEqual(a.formulation.display_name, "Paracetamol 500 mg Tablet")

    def test_different_strength_or_type_is_a_different_formulation(self):
        make_medicine("A", "B1", "Tablet", [("Paracetamol", "500", "mg")])
        make_medicine("B", "B2", "Tablet", [("Paracetamol", "650", "mg")])
        make_medicine("C", "B3", "Syrup", [("Paracetamol", "500", "mg")])
        self.assertEqual(Formulation.objects.count(), 3)

    def test_orphan_formulation_is_removed(self):
        m = make_medicine("A", "B1", "Tablet", [("Paracetamol", "500", "mg")])
        m.delete()
        self.assertEqual(Formulation.objects.count(), 0)


class PublicApiTests(TestCase):
    def setUp(self):
        make_medicine("Crocin", "SecretBrand", "Tablet", [("Paracetamol", "500", "mg")])
        make_medicine("Augmentin", "SecretBrand", "Tablet",
                      [("Amoxicillin", "500", "mg"), ("Clavulanic Acid", "125", "mg")])
        make_medicine("Hidden", "SecretBrand", "Syrup", [("Ibuprofen", "100", "mg")], active=False)
        d = Distributor.objects.create(name="SecretDistributor")
        Medicine.objects.first().distributors.add(d)

    def test_list_never_leaks_brand_or_distributor(self):
        body = self.client.get(reverse("public-formulation-list")).content.decode()
        self.assertNotIn("SecretBrand", body)
        self.assertNotIn("SecretDistributor", body)
        self.assertNotIn("brand", body.lower())

    def test_inactive_medicines_are_hidden(self):
        data = self.client.get(reverse("public-formulation-list")).json()
        names = [r["display_name"] for r in data["results"]]
        self.assertEqual(data["count"], 2)
        self.assertFalse(any("Ibuprofen" in n for n in names))

    def test_search_and_filter(self):
        url = reverse("public-formulation-list")
        self.assertEqual(self.client.get(url, {"q": "amoxi"}).json()["count"], 1)
        self.assertEqual(self.client.get(url, {"q": "clavulanic tablet"}).json()["count"], 1)
        self.assertEqual(self.client.get(url, {"type": "tablet"}).json()["count"], 2)
        self.assertEqual(self.client.get(url, {"composition": "paracetamol"}).json()["count"], 1)

    def test_detail_and_filters_and_suggest(self):
        slug = Formulation.objects.get(display_name__startswith="Paracetamol").slug
        self.assertEqual(self.client.get(reverse("public-formulation-detail", args=[slug])).status_code, 200)
        self.assertEqual(self.client.get(reverse("public-formulation-detail", args=["nope"])).status_code, 404)
        types = self.client.get(reverse("public-filters")).json()["types"]
        self.assertEqual([t["name"] for t in types], ["Tablet"])  # Syrup has no active medicines
        sug = self.client.get(reverse("public-compositions"), {"q": "para"}).json()
        self.assertEqual(sug[0]["name"], "Paracetamol")


class ImporterTests(TestCase):
    CSV = (
        "product_name,brand,type,pack_size,hsn_code,gst_rate,compositions,distributors,description,is_active\n"
        "Crocin,GSK,Tablet,15 tablets,3004,12,Paracetamol:500 mg,Dist A; Dist B,,true\n"
        "Bad Row,GSK,Tablet,,,,,,,\n"
        "Augmentin,GSK,Tablet,10,3004,12,Amoxicillin:500 mg; Clavulanic Acid:125 mg,,,true\n"
    )

    def test_import_creates_and_reports_errors(self):
        result = import_medicines_csv(io.BytesIO(self.CSV.encode()))
        self.assertEqual((result.created, result.updated), (2, 0))
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(Formulation.objects.count(), 2)
        self.assertEqual(Medicine.objects.get(product_name="Crocin").distributors.count(), 2)

    def test_dry_run_saves_nothing_and_reimport_updates(self):
        result = import_medicines_csv(io.BytesIO(self.CSV.encode()), dry_run=True)
        self.assertEqual(result.created, 2)
        self.assertEqual(Medicine.objects.count(), 0)
        import_medicines_csv(io.BytesIO(self.CSV.encode()))
        again = import_medicines_csv(io.BytesIO(self.CSV.encode()))
        self.assertEqual((again.created, again.updated), (0, 2))
