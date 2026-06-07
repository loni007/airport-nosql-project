"""SQL Server to MongoDB migration entry point."""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any

from config import load_config
from db import connect_mongo, connect_sql, ensure_migration_run_indexes, fetch_source_counts
from errors import DatabaseConnectionError, MalformedSourceRecordError
from logger import get_logger
from transformers import (
    build_airline_documents,
    build_airplane_documents,
    build_client_documents,
    build_flight_documents,
    build_maintenance_documents,
    build_reservation_documents,
    build_travel_agency_documents,
)


TABLE_QUERIES = {
    "airlines": "SELECT * FROM dbo.AIRLINE ORDER BY airline_id",
    "models": "SELECT * FROM dbo.MODEL ORDER BY model_id",
    "clients": "SELECT * FROM dbo.CLIENT ORDER BY client_id",
    "travel_agencies": "SELECT * FROM dbo.TRAVELAGENCY ORDER BY agency_id",
    "airplanes": "SELECT * FROM dbo.AIRPLANE ORDER BY airplane_id",
    "employers": "SELECT * FROM dbo.EMPLOYER ORDER BY employer_id",
    "flights": "SELECT * FROM dbo.FLIGHT ORDER BY flight_id",
    "tickets": "SELECT * FROM dbo.TICKET ORDER BY ticket_id",
    "reservations": "SELECT * FROM dbo.RESERVE ORDER BY reserve_id",
    "care": "SELECT * FROM dbo.CARE ORDER BY care_id",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_run_document(run_id: str, source_counts: dict[str, int], dry_run: bool) -> dict[str, Any]:
    now = utc_now()
    return {
        "run_id": run_id,
        "phase": 6,
        "status": "DRY_RUN" if dry_run else "STARTED",
        "started_at": now,
        "finished_at": now if dry_run else None,
        "source_counts": source_counts,
        "target_counts": {},
        "message": "Migration transformed SQL Server rows into MongoDB documents.",
    }


def write_migration_run(database: Any, run_document: dict[str, Any]) -> None:
    """Upsert by run_id so metadata writes remain idempotent."""
    database.migration_runs.replace_one(
        {"run_id": run_document["run_id"]},
        run_document,
        upsert=True,
    )


def fetch_rows(sql_connection: Any, query: str) -> list[dict[str, Any]]:
    """Fetch SQL rows as dictionaries keyed by column name."""
    cursor = sql_connection.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_source_tables(sql_connection: Any) -> dict[str, list[dict[str, Any]]]:
    """Load all SQL tables needed by the transformation layer."""
    return {name: fetch_rows(sql_connection, query) for name, query in TABLE_QUERIES.items()}


def normalize_for_mongo(value: Any) -> Any:
    """Convert SQL/Python values into BSON-encodable values."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [normalize_for_mongo(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_for_mongo(item) for key, item in value.items()}
    return value


def upsert_documents(database: Any, collection_name: str, key_field: str, documents: list[dict[str, Any]]) -> int:
    """Idempotently upsert documents by their preserved SQL primary key."""
    collection = database[collection_name]
    for document in documents:
        document = normalize_for_mongo(document)
        collection.replace_one({key_field: document[key_field]}, document, upsert=True)
    return len(documents)


def build_documents(source: dict[str, list[dict[str, Any]]]) -> dict[str, tuple[str, list[dict[str, Any]]]]:
    """Build all MongoDB target documents from loaded SQL rows."""
    return {
        "airlines": (
            "sql_airline_id",
            build_airline_documents(source["airlines"], source["flights"], source["airplanes"]),
        ),
        "airplanes": (
            "sql_airplane_id",
            build_airplane_documents(source["airplanes"], source["airlines"], source["models"]),
        ),
        "flights": (
            "sql_flight_id",
            build_flight_documents(source["flights"], source["airlines"], source["tickets"], source["reservations"]),
        ),
        "clients": (
            "sql_client_id",
            build_client_documents(source["clients"], source["reservations"], source["tickets"]),
        ),
        "travel_agencies": (
            "sql_agency_id",
            build_travel_agency_documents(source["travel_agencies"], source["reservations"], source["tickets"]),
        ),
        "reservations": (
            "sql_reserve_id",
            build_reservation_documents(
                source["reservations"],
                source["clients"],
                source["tickets"],
                source["flights"],
                source["airlines"],
                source["travel_agencies"],
            ),
        ),
        "maintenance": (
            "sql_care_id",
            build_maintenance_documents(source["care"], source["airplanes"], source["employers"]),
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the airport SQL Server to MongoDB migration pipeline.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify SQL Server and MongoDB connectivity without writing migration metadata.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional stable run id. Useful when demonstrating idempotent metadata upserts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = get_logger()
    config = load_config()
    run_id = args.run_id or str(uuid.uuid4())

    logger.info("Migration started: run_id=%s dry_run=%s", run_id, args.dry_run)

    try:
        sql_connection = connect_sql(config.sql)
        logger.info("Connected to SQL Server database=%s server=%s", config.sql.database, config.sql.server)
        mongo_client = connect_mongo(config.mongo)
        logger.info("Connected to MongoDB database=%s uri=%s", config.mongo.database, config.mongo.uri)
    except DatabaseConnectionError:
        logger.exception("Database connection failure. Migration cannot continue.")
        raise SystemExit(2)

    try:
        source_counts = fetch_source_counts(sql_connection)
        logger.info("SQL source counts loaded: %s", source_counts)
        run_document = create_run_document(run_id, source_counts, args.dry_run)
        source = fetch_source_tables(sql_connection)
        logger.info("Loaded SQL source tables for transformation")
        target_documents = build_documents(source)
        target_counts = {collection: len(documents) for collection, (_, documents) in target_documents.items()}
        run_document["target_counts"] = target_counts

        if not args.dry_run:
            database = mongo_client[config.mongo.database]
            ensure_migration_run_indexes(database)
            for collection_name, (key_field, documents) in target_documents.items():
                migrated_count = upsert_documents(database, collection_name, key_field, documents)
                logger.info("Upserted %s documents into %s", migrated_count, collection_name)
            run_document["status"] = "COMPLETED"
            run_document["finished_at"] = utc_now()
            write_migration_run(database, run_document)
            logger.info("Migration run metadata upserted: run_id=%s", run_id)

        printable = dict(run_document)
        printable["started_at"] = printable["started_at"].isoformat()
        if printable["finished_at"]:
            printable["finished_at"] = printable["finished_at"].isoformat()
        print(json.dumps(printable, indent=2))
    except (MalformedSourceRecordError, ValueError):
        logger.exception("Malformed source record encountered.")
        raise SystemExit(3)
    finally:
        sql_connection.close()
        mongo_client.close()
        logger.info("Migration finished: run_id=%s", run_id)


if __name__ == "__main__":
    main()
