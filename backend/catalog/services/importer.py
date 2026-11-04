"""Bulk import of medicines from CSV.

Columns: product_name, brand, type, pack_size, hsn_code, gst_rate, compositions, distributors,
         description, is_active
`compositions` looks like:   Paracetamol:500 mg; Caffeine:65 mg
`distributors` looks like:   Distributor A; Distributor B
"""
import csv
import io
import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.db import transaction

from catalog.models import (
    Brand, Composition, Distributor, Medicine, MedicineComposition, MedicineDistributor, MedicineType,
)

logger = logging.getLogger(__name__)

REQUIRED = ["product_name", "brand", "type", "compositions"]
COMPOSITION_RE = re.compile(r"^\s*(?P<name>[^:]+?)\s*(?::\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[^\s;]*(?:\s*/\s*\d*\s*\w+)?)?)?\s*$")


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    errors: list = field(default_factory=list)  # (line_number, message)

    @property
    def ok(self):
        return not self.errors


def _get_ci(model, name: str, **defaults):
    obj = model.objects.filter(name__iexact=name).first()
    if obj:
        return obj, False
    return model.objects.create(name=name, **defaults), True


def _parse_compositions(raw: str):
    parsed = []
    for chunk in [c for c in raw.split(";") if c.strip()]:
        m = COMPOSITION_RE.match(chunk)
        if not m:
            raise ValueError(f"Cannot read composition '{chunk.strip()}'. Use 'Name:500 mg'.")
        value = m.group("value")
        parsed.append((m.group("name").strip(), Decimal(value) if value else None, (m.group("unit") or "").strip()))
    if not parsed:
        raise ValueError("At least one composition is required")
    return parsed


def _import_row(row: dict) -> bool:
    """Create or update one medicine. Returns True if created."""
    name = row["product_name"].strip()
    brand, _ = _get_ci(Brand, row["brand"].strip())
    mtype, _ = _get_ci(MedicineType, row["type"].strip())
    pack = (row.get("pack_size") or "").strip()
    try:
        gst = Decimal((row.get("gst_rate") or "12").strip())
    except InvalidOperation:
        raise ValueError(f"Invalid gst_rate '{row.get('gst_rate')}'")

    medicine = Medicine.objects.filter(product_name__iexact=name, brand=brand, pack_size=pack).first()
    created = medicine is None
    fields = {
        "medicine_type": mtype,
        "hsn_code": (row.get("hsn_code") or "").strip(),
        "gst_rate": gst,
        "description": (row.get("description") or "").strip(),
        "is_active": (row.get("is_active") or "true").strip().lower() not in ("false", "0", "no"),
    }
    if created:
        medicine = Medicine.objects.create(product_name=name, brand=brand, pack_size=pack, **fields)
    else:
        for k, v in fields.items():
            setattr(medicine, k, v)
        medicine.save()

    # Replace compositions (signals re-derive the public formulation).
    medicine.compositions.all().delete()
    for comp_name, value, unit in _parse_compositions(row["compositions"]):
        comp, _ = _get_ci(Composition, comp_name)
        MedicineComposition.objects.create(
            medicine=medicine, composition=comp, strength_value=value, strength_unit=unit or ("mg" if value else "")
        )

    for dist_name in [d.strip() for d in (row.get("distributors") or "").split(";") if d.strip()]:
        dist, _ = _get_ci(Distributor, dist_name)
        MedicineDistributor.objects.get_or_create(medicine=medicine, distributor=dist)
    return created


def import_medicines_csv(file_obj, dry_run: bool = False) -> ImportResult:
    text = file_obj.read()
    if isinstance(text, bytes):
        text = text.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    result = ImportResult()

    missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
    if missing:
        result.errors.append((1, f"Missing column(s): {', '.join(missing)}"))
        logger.warning("Import rejected: missing columns %s", missing)
        return result

    for line_no, row in enumerate(reader, start=2):
        if not any((v or "").strip() for v in row.values()):
            continue
        empty = [c for c in REQUIRED if not (row.get(c) or "").strip()]
        if empty:
            result.errors.append((line_no, f"Missing value for: {', '.join(empty)}"))
            continue
        try:
            with transaction.atomic():
                created = _import_row(row)
                if dry_run:
                    transaction.set_rollback(True)
            result.created += int(created)
            result.updated += int(not created)
        except Exception as exc:  # row-level failure must not stop the whole import
            logger.warning("Import row %s failed: %s", line_no, exc)
            result.errors.append((line_no, str(exc)))

    logger.info(
        "Medicine import finished: created=%s updated=%s errors=%s dry_run=%s",
        result.created, result.updated, len(result.errors), dry_run,
    )
    return result
