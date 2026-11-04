"""Catalogue search. Uses trigram similarity on PostgreSQL, plain substring matching elsewhere."""
import logging
import re

from django.db import connection
from django.db.models import Q

logger = logging.getLogger(__name__)


def _tokens(q: str) -> list:
    return [t for t in re.split(r"\s+", q.strip().lower()) if t]


def search_formulations(qs, q: str):
    tokens = _tokens(q)
    if not tokens:
        return qs
    all_tokens = Q()
    for token in tokens:
        all_tokens &= Q(search_text__icontains=token)

    if connection.vendor == "postgresql":
        from django.contrib.postgres.search import TrigramSimilarity

        qs = qs.annotate(similarity=TrigramSimilarity("search_text", " ".join(tokens)))
        logger.debug("Search (trigram) q=%r", q)
        return qs.filter(all_tokens | Q(similarity__gt=0.25)).order_by("-similarity", "display_name")

    logger.debug("Search (substring) q=%r", q)
    return qs.filter(all_tokens)


def search_compositions(qs, q: str):
    tokens = _tokens(q)
    if not tokens:
        return qs
    cond = Q()
    for token in tokens:
        cond &= Q(name__icontains=token) | Q(aliases__icontains=token)
    return qs.filter(cond)
