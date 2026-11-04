"""Derive the public Formulation for a Medicine from its compositions, strengths and type."""
import hashlib
import json
import logging

from django.utils.text import slugify

logger = logging.getLogger(__name__)


def _norm_value(value) -> str:
    return "" if value is None else format(value.normalize(), "f")


def build_signature(medicine_type_id: int, parts: list) -> str:
    payload = json.dumps([medicine_type_id, sorted(parts)], sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()


def sync_formulation(medicine):
    """Create/refresh the Formulation for `medicine` and link it. Returns the Formulation or None."""
    from catalog.models import Formulation, Medicine, unique_slug

    links = list(medicine.compositions.select_related("composition"))
    old_id = medicine.formulation_id

    if not links:
        logger.debug("Medicine %s has no compositions yet; no formulation", medicine.pk)
        if old_id:
            Medicine.objects.filter(pk=medicine.pk).update(formulation=None)
            medicine.formulation_id = None
            cleanup_orphan_formulation(old_id)
        return None

    links.sort(key=lambda l: l.composition.name.lower())
    parts = [[l.composition_id, _norm_value(l.strength_value), l.strength_unit.strip().lower()] for l in links]
    signature = build_signature(medicine.medicine_type_id, parts)

    components = [
        {"name": l.composition.name, "slug": l.composition.slug, "strength": l.strength_display} for l in links
    ]
    name_part = " + ".join(f"{c['name']} {c['strength']}".strip() for c in components)
    display_name = f"{name_part} {medicine.medicine_type.name}"
    aliases = " ".join(l.composition.aliases for l in links if l.composition.aliases)
    search_text = f"{display_name} {aliases}".lower()

    formulation = Formulation.objects.filter(signature=signature).first()
    created = formulation is None
    if created:
        formulation = Formulation(
            signature=signature,
            display_name=display_name,
            medicine_type=medicine.medicine_type,
            slug=unique_slug(Formulation, display_name, None, 220),
        )
    formulation.display_name = display_name
    formulation.components = components
    formulation.search_text = search_text
    formulation.save()
    formulation.compositions.set([l.composition for l in links])

    if old_id != formulation.pk:
        Medicine.objects.filter(pk=medicine.pk).update(formulation=formulation)
        medicine.formulation_id = formulation.pk
        if old_id:
            cleanup_orphan_formulation(old_id)

    if created:
        logger.info("Formulation created: %s (medicine=%s)", display_name, medicine.pk)
    return formulation


def cleanup_orphan_formulation(formulation_id: int):
    from catalog.models import Formulation

    formulation = Formulation.objects.filter(pk=formulation_id).first()
    if formulation and not formulation.medicines.exists():
        logger.info("Formulation removed (no medicines left): %s", formulation.display_name)
        formulation.delete()
