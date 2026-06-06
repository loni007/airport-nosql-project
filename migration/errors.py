"""Explicit migration error types and malformed source-record checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class MigrationError(Exception):
    """Base class for migration-specific errors."""


class DatabaseConnectionError(MigrationError):
    """Raised when SQL Server or MongoDB cannot be reached."""


class MalformedSourceRecordError(MigrationError):
    """Raised when a source row violates migration-level expectations."""


@dataclass(frozen=True)
class MalformedRecord:
    entity: str
    sql_id: Any
    reason: str


def validate_flight_record(row: dict[str, Any]) -> None:
    """Validate source flight fields that are required for derived fields."""
    required_fields = [
        "flight_id",
        "flight_number",
        "airline_id",
        "origin_airport",
        "destination_airport",
        "scheduled_departure",
        "scheduled_arrival",
        "status",
    ]
    missing = [field for field in required_fields if row.get(field) is None]
    if missing:
        raise MalformedSourceRecordError(
            f"FLIGHT {row.get('flight_id', '<unknown>')} missing required fields: {', '.join(missing)}"
        )

    if row["origin_airport"] == row["destination_airport"]:
        raise MalformedSourceRecordError(
            f"FLIGHT {row['flight_id']} has same origin and destination airport"
        )

    departure = row["scheduled_departure"]
    arrival = row["scheduled_arrival"]
    if not isinstance(departure, datetime) or not isinstance(arrival, datetime):
        raise MalformedSourceRecordError(
            f"FLIGHT {row['flight_id']} has invalid datetime values"
        )

    if arrival <= departure:
        raise MalformedSourceRecordError(
            f"FLIGHT {row['flight_id']} arrival must be after departure"
        )


def validate_reservation_record(row: dict[str, Any]) -> None:
    """Validate source reservation fields before transformation."""
    required_fields = [
        "reserve_id",
        "client_id",
        "ticket_id",
        "reserved_at",
        "payment_status",
        "reservation_channel",
    ]
    missing = [field for field in required_fields if row.get(field) is None]
    if missing:
        raise MalformedSourceRecordError(
            f"RESERVE {row.get('reserve_id', '<unknown>')} missing required fields: {', '.join(missing)}"
        )

    if row["reservation_channel"] == "AGENCY" and row.get("agency_id") is None:
        raise MalformedSourceRecordError(
            f"RESERVE {row['reserve_id']} uses AGENCY channel without agency_id"
        )
