"""Classify transactions using configurable, deterministic merchant rules."""

from __future__ import annotations

import re
from collections.abc import Mapping

try:
    from .buckets import BUCKET_RULES, DEFAULT_BUCKET
except ImportError:  # Support running workflow.py directly from src.
    from buckets import BUCKET_RULES, DEFAULT_BUCKET


def classify_expense(merchant: str | None) -> str:
    """Return the configured bucket for a merchant, or ``Other`` if unknown."""
    normalized_merchant = re.sub(r"\s+", " ", (merchant or "").strip().lower())

    for bucket, keywords in BUCKET_RULES.items():
        if any(keyword in normalized_merchant for keyword in keywords):
            return bucket

    return DEFAULT_BUCKET


def classify_transaction(transaction: Mapping[str, object]) -> dict[str, object]:
    """Return a transaction copy enriched with its expense bucket."""
    enriched_transaction = dict(transaction)
    enriched_transaction["bucket"] = classify_expense(
        str(transaction.get("merchant") or "")
    )
    return enriched_transaction