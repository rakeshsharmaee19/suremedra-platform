import logging

from django.db import transaction

from .models import Counter

logger = logging.getLogger(__name__)


def next_number(key: str) -> int:
    """Return the next number for `key` (1, 2, 3...). Safe under concurrency on PostgreSQL."""
    with transaction.atomic():
        counter, _ = Counter.objects.select_for_update().get_or_create(key=key)
        counter.value += 1
        counter.save(update_fields=["value"])
    logger.debug("Sequence %s advanced to %s", key, counter.value)
    return counter.value
