"""
Create MongoDB collections and indexes for the airport migration project.

Phase 4 deliverable:
    - defines the MongoDB collection structure
    - creates indexes needed for idempotent migration and analytics
    - supports --dry-run so the model can be verified without MongoDB running

Usage:
    python mongodb/setup_collections.py --dry-run
    python mongodb/setup_collections.py --mongo-uri mongodb://localhost:27017 --database airport_nosql
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IndexSpec:
    collection: str
    keys: list[tuple[str, int]]
    name: str
    unique: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "collection": self.collection,
            "keys": self.keys,
            "name": self.name,
            "unique": self.unique,
        }


COLLECTIONS = [
    "airlines",
    "airplanes",
    "flights",
    "clients",
    "travel_agencies",
    "reservations",
    "maintenance",
    "migration_runs",
]

INDEXES = [
    IndexSpec("airlines", [("sql_airline_id", 1)], "uq_airlines_sql_airline_id", True),
    IndexSpec("airlines", [("airline_code", 1)], "uq_airlines_airline_code", True),
    IndexSpec("airplanes", [("sql_airplane_id", 1)], "uq_airplanes_sql_airplane_id", True),
    IndexSpec("airplanes", [("registration_number", 1)], "uq_airplanes_registration_number", True),
    IndexSpec("airplanes", [("airline.sql_airline_id", 1)], "idx_airplanes_airline"),
    IndexSpec("airplanes", [("model.sql_model_id", 1)], "idx_airplanes_model"),
    IndexSpec("flights", [("sql_flight_id", 1)], "uq_flights_sql_flight_id", True),
    IndexSpec("flights", [("sql_airline_id", 1), ("scheduled_departure", 1)], "idx_flights_airline_departure"),
    IndexSpec("flights", [("flight_number", 1)], "idx_flights_flight_number"),
    IndexSpec("clients", [("sql_client_id", 1)], "uq_clients_sql_client_id", True),
    IndexSpec("clients", [("email", 1)], "uq_clients_email", True),
    IndexSpec("clients", [("passport_number", 1)], "uq_clients_passport_number", True),
    IndexSpec("travel_agencies", [("sql_agency_id", 1)], "uq_travel_agencies_sql_agency_id", True),
    IndexSpec("travel_agencies", [("name", 1)], "uq_travel_agencies_name", True),
    IndexSpec("reservations", [("sql_reserve_id", 1)], "uq_reservations_sql_reserve_id", True),
    IndexSpec("reservations", [("reserved_at", 1)], "idx_reservations_reserved_at"),
    IndexSpec("reservations", [("client.sql_client_id", 1)], "idx_reservations_client"),
    IndexSpec("reservations", [("agency.sql_agency_id", 1)], "idx_reservations_agency"),
    IndexSpec("reservations", [("flight.sql_flight_id", 1)], "idx_reservations_flight"),
    IndexSpec("maintenance", [("sql_care_id", 1)], "uq_maintenance_sql_care_id", True),
    IndexSpec("maintenance", [("airplane.sql_airplane_id", 1)], "idx_maintenance_airplane"),
    IndexSpec("maintenance", [("care_date", 1)], "idx_maintenance_care_date"),
    IndexSpec("migration_runs", [("run_id", 1)], "uq_migration_runs_run_id", True),
    IndexSpec("migration_runs", [("started_at", -1)], "idx_migration_runs_started_at"),
]


def print_plan(database_name: str) -> None:
    plan = {
        "database": database_name,
        "collections": COLLECTIONS,
        "indexes": [index.as_dict() for index in INDEXES],
    }
    print(json.dumps(plan, indent=2))


def apply_indexes(mongo_uri: str, database_name: str) -> None:
    try:
        from pymongo import ASCENDING, DESCENDING, MongoClient
        from pymongo.errors import ConnectionFailure, PyMongoError
    except ImportError as exc:
        raise SystemExit(
            "pymongo is required for live MongoDB setup. Run: python -m pip install -r requirements.txt"
        ) from exc

    direction_map = {1: ASCENDING, -1: DESCENDING}

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
    except ConnectionFailure as exc:
        raise SystemExit(f"Could not connect to MongoDB at {mongo_uri}: {exc}") from exc

    database = client[database_name]

    try:
        existing_collections = set(database.list_collection_names())
        for collection_name in COLLECTIONS:
            if collection_name not in existing_collections:
                database.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection exists: {collection_name}")

        for index in INDEXES:
            keys = [(field, direction_map[direction]) for field, direction in index.keys]
            database[index.collection].create_index(keys, name=index.name, unique=index.unique)
            unique_label = " unique" if index.unique else ""
            print(f"Created{unique_label} index: {index.collection}.{index.name}")
    except PyMongoError as exc:
        raise SystemExit(f"MongoDB setup failed: {exc}") from exc
    finally:
        client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create MongoDB collections and indexes.")
    parser.add_argument(
        "--mongo-uri",
        default=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        help="MongoDB connection URI. Defaults to MONGODB_URI or localhost.",
    )
    parser.add_argument(
        "--database",
        default=os.getenv("MONGODB_DATABASE", "airport_nosql"),
        help="MongoDB database name. Defaults to MONGODB_DATABASE or airport_nosql.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the collection/index plan without connecting to MongoDB.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        print_plan(args.database)
        return

    apply_indexes(args.mongo_uri, args.database)


if __name__ == "__main__":
    main()
