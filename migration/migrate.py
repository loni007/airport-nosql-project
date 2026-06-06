"""
Phase 5 migration pipeline entry point.

This phase intentionally stops at a safe migration skeleton:
    - loads SQL Server and MongoDB configuration
    - verifies both database connections
    - reads SQL source counts
    - writes one idempotent migration_runs document

Phase 6 will add the actual transformation/upsert logic.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from config import load_config
from db import connect_mongo, connect_sql, ensure_migration_run_indexes, fetch_source_counts


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_run_document(run_id: str, source_counts: dict[str, int], dry_run: bool) -> dict[str, Any]:
    now = utc_now()
    return {
        "run_id": run_id,
        "phase": 5,
        "status": "DRY_RUN" if dry_run else "STARTED",
        "started_at": now,
        "finished_at": now if dry_run else None,
        "source_counts": source_counts,
        "message": "Phase 5 skeleton verified connections and source counts.",
    }


def write_migration_run(database: Any, run_document: dict[str, Any]) -> None:
    """Upsert by run_id so metadata writes remain idempotent."""
    database.migration_runs.replace_one(
        {"run_id": run_document["run_id"]},
        run_document,
        upsert=True,
    )


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
    config = load_config()
    run_id = args.run_id or str(uuid.uuid4())

    sql_connection = connect_sql(config.sql)
    mongo_client = connect_mongo(config.mongo)

    try:
        source_counts = fetch_source_counts(sql_connection)
        run_document = create_run_document(run_id, source_counts, args.dry_run)

        if not args.dry_run:
            database = mongo_client[config.mongo.database]
            ensure_migration_run_indexes(database)
            write_migration_run(database, run_document)

        printable = dict(run_document)
        printable["started_at"] = printable["started_at"].isoformat()
        if printable["finished_at"]:
            printable["finished_at"] = printable["finished_at"].isoformat()
        print(json.dumps(printable, indent=2))
    finally:
        sql_connection.close()
        mongo_client.close()


if __name__ == "__main__":
    main()
