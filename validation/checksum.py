"""
Phase 8 checksum helpers.

Copy to:
    validation/checksum.py
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable


def normalize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def stable_json(record: dict[str, Any]) -> str:
    normalized = {key: normalize_value(value) for key, value in sorted(record.items())}
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_hash(record: dict[str, Any]) -> str:
    return hashlib.sha256(stable_json(record).encode("utf-8")).hexdigest()


def collection_checksum(records: Iterable[dict[str, Any]], key_field: str) -> str:
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: item[key_field]):
        digest.update(record_hash(record).encode("ascii"))
    return digest.hexdigest()
