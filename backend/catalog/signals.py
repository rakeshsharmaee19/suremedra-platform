import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Medicine, MedicineComposition
from .services.formulation import cleanup_orphan_formulation, sync_formulation

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=MedicineComposition)
def composition_changed(sender, instance, **kwargs):
    try:
        medicine = Medicine.objects.get(pk=instance.medicine_id)
    except Medicine.DoesNotExist:
        return  # medicine itself is being deleted
    sync_formulation(medicine)


@receiver(post_save, sender=Medicine)
def medicine_saved(sender, instance, created, **kwargs):
    if not created:
        sync_formulation(instance)


@receiver(post_delete, sender=Medicine)
def medicine_deleted(sender, instance, **kwargs):
    if instance.formulation_id:
        cleanup_orphan_formulation(instance.formulation_id)
