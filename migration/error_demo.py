"""
Phase 7 explicit error scenario demo.

This script demonstrates the two required error scenarios without needing live
database services:
    1. malformed source records
    2. database connection failures

Run:
    python migration/error_demo.py
"""

from __future__ import annotations

from datetime import datetime

from config import MongoConfig, SqlServerConfig
from db import connect_mongo, connect_sql
from errors import (
    DatabaseConnectionError,
    MalformedSourceRecordError,
    validate_flight_record,
    validate_reservation_record,
)
from logger import get_logger


def demo_malformed_records() -> int:
    logger = get_logger("airport_migration.error_demo")
    skipped = 0

    malformed_flight = {
        "flight_id": 999999,
        "flight_number": "BAD001",
        "airline_id": 1,
        "origin_airport": "SKP",
        "destination_airport": "SKP",
        "scheduled_departure": datetime(2026, 6, 10, 8, 0, 0),
        "scheduled_arrival": datetime(2026, 6, 10, 7, 0, 0),
        "status": "SCHEDULED",
    }

    malformed_reservation = {
        "reserve_id": 999999,
        "client_id": 1,
        "ticket_id": 1,
        "agency_id": None,
        "reserved_at": datetime(2026, 6, 1, 12, 0, 0),
        "payment_status": "PAID",
        "reservation_channel": "AGENCY",
    }

    for validator, record_name, row in [
        (validate_flight_record, "flight", malformed_flight),
        (validate_reservation_record, "reservation", malformed_reservation),
    ]:
        try:
            validator(row)
        except MalformedSourceRecordError as exc:
            skipped += 1
            logger.warning("Malformed %s source record skipped: %s", record_name, exc)

    return skipped


def demo_connection_failures() -> int:
    logger = get_logger("airport_migration.error_demo")
    failures = 0

    bad_sql_config = SqlServerConfig(
        driver="ODBC Driver 17 for SQL Server",
        server="localhost,65000",
        database="AirportManagement",
        user="sa",
        password="wrong-password",
    )
    bad_mongo_config = MongoConfig(uri="mongodb://localhost:65001", database="airport_nosql")

    try:
        connection = connect_sql(bad_sql_config)
        connection.close()
    except Exception as exc:
        failures += 1
        wrapped = DatabaseConnectionError(f"SQL Server connection failure handled: {exc}")
        logger.error("%s", wrapped)

    try:
        client = connect_mongo(bad_mongo_config)
        client.close()
    except Exception as exc:
        failures += 1
        wrapped = DatabaseConnectionError(f"MongoDB connection failure handled: {exc}")
        logger.error("%s", wrapped)

    return failures


def main() -> None:
    logger = get_logger("airport_migration.error_demo")
    logger.info("Starting Phase 7 error scenario demo")
    skipped = demo_malformed_records()
    failures = demo_connection_failures()
    logger.info(
        "Phase 7 error demo complete: malformed_records_skipped=%s, connection_failures_handled=%s",
        skipped,
        failures,
    )


if __name__ == "__main__":
    main()
