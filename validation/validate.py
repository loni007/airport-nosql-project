"""
Phase 8 validation layer.

Copy to:
    validation/validate.py

This script compares SQL Server source data and MongoDB migrated data.
It expects the migration to preserve SQL primary keys as sql_* fields.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any

from checksum import collection_checksum


SQL_COUNT_QUERIES = {
    "airlines": "SELECT COUNT(*) AS count_value FROM dbo.AIRLINE",
    "airplanes": "SELECT COUNT(*) AS count_value FROM dbo.AIRPLANE",
    "flights": "SELECT COUNT(*) AS count_value FROM dbo.FLIGHT",
    "clients": "SELECT COUNT(*) AS count_value FROM dbo.CLIENT",
    "travel_agencies": "SELECT COUNT(*) AS count_value FROM dbo.TRAVELAGENCY",
    "reservations": "SELECT COUNT(*) AS count_value FROM dbo.RESERVE",
    "maintenance": "SELECT COUNT(*) AS count_value FROM dbo.CARE",
}


@dataclass
class ValidationResult:
    name: str
    passed: bool
    details: str


def connect_sql(args: argparse.Namespace):
    import pyodbc

    connection_string = (
        f"DRIVER={{{args.sql_driver}}};"
        f"SERVER={args.sql_server};"
        f"DATABASE={args.sql_database};"
        f"UID={args.sql_user};"
        f"PWD={args.sql_password};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def connect_mongo(args: argparse.Namespace):
    from pymongo import MongoClient

    client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


def sql_scalar(cursor: Any, query: str) -> Any:
    cursor.execute(query)
    row = cursor.fetchone()
    return row[0]


def validate_counts(cursor: Any, mongo_db: Any) -> list[ValidationResult]:
    results = []
    for collection_name, query in SQL_COUNT_QUERIES.items():
        sql_count = int(sql_scalar(cursor, query))
        mongo_count = mongo_db[collection_name].count_documents({})
        results.append(
            ValidationResult(
                name=f"count:{collection_name}",
                passed=sql_count == mongo_count,
                details=f"SQL={sql_count}, MongoDB={mongo_count}",
            )
        )
    return results


def validate_airline_aggregates(cursor: Any, mongo_db: Any) -> list[ValidationResult]:
    cursor.execute(
        """
        SELECT
            a.airline_id,
            COUNT(DISTINCT f.flight_id) AS total_flights,
            COUNT(DISTINCT p.airplane_id) AS total_airplanes
        FROM dbo.AIRLINE a
        LEFT JOIN dbo.FLIGHT f ON f.airline_id = a.airline_id
        LEFT JOIN dbo.AIRPLANE p ON p.airline_id = a.airline_id
        GROUP BY a.airline_id
        """
    )
    results = []
    for row in cursor.fetchall():
        doc = mongo_db.airlines.find_one({"sql_airline_id": row.airline_id})
        passed = bool(doc) and doc.get("total_flights") == row.total_flights and doc.get("total_airplanes") == row.total_airplanes
        results.append(
            ValidationResult(
                name=f"aggregate:airline:{row.airline_id}",
                passed=passed,
                details=f"expected flights={row.total_flights}, airplanes={row.total_airplanes}; mongo={doc}",
            )
        )
    return results


def validate_travel_agency_aggregates(cursor: Any, mongo_db: Any) -> list[ValidationResult]:
    cursor.execute(
        """
        SELECT
            ta.agency_id,
            COUNT(r.reserve_id) AS total_reservations,
            COALESCE(SUM(t.price), 0) AS total_ticket_value
        FROM dbo.TRAVELAGENCY ta
        LEFT JOIN dbo.RESERVE r ON r.agency_id = ta.agency_id
        LEFT JOIN dbo.TICKET t ON t.ticket_id = r.ticket_id
        GROUP BY ta.agency_id
        """
    )
    results = []
    for row in cursor.fetchall():
        doc = mongo_db.travel_agencies.find_one({"sql_agency_id": row.agency_id})
        expected_value = round(float(row.total_ticket_value), 2)
        actual_value = round(float(doc.get("total_ticket_value", 0)), 2) if doc else None
        passed = bool(doc) and doc.get("total_reservations") == row.total_reservations and actual_value == expected_value
        results.append(
            ValidationResult(
                name=f"aggregate:travel_agency:{row.agency_id}",
                passed=passed,
                details=f"expected reservations={row.total_reservations}, value={expected_value}; mongo={doc}",
            )
        )
    return results


def validate_client_spot_checks(cursor: Any, mongo_db: Any, limit: int) -> list[ValidationResult]:
    cursor.execute(
        f"""
        SELECT TOP ({limit})
            c.client_id,
            c.email,
            COUNT(r.reserve_id) AS reservation_count,
            COUNT(DISTINCT r.agency_id) AS agency_count
        FROM dbo.CLIENT c
        LEFT JOIN dbo.RESERVE r ON r.client_id = c.client_id
        GROUP BY c.client_id, c.email
        ORDER BY c.client_id
        """
    )
    results = []
    for row in cursor.fetchall():
        doc = mongo_db.clients.find_one({"sql_client_id": row.client_id})
        passed = (
            bool(doc)
            and doc.get("email") == row.email
            and doc.get("reservation_count") == row.reservation_count
            and doc.get("agency_count") == row.agency_count
        )
        results.append(
            ValidationResult(
                name=f"spot_check:client:{row.client_id}",
                passed=passed,
                details=f"expected email={row.email}, reservations={row.reservation_count}, agencies={row.agency_count}; mongo={doc}",
            )
        )
    return results


def validate_flight_checksum(cursor: Any, mongo_db: Any) -> ValidationResult:
    cursor.execute(
        """
        SELECT flight_id, flight_number, airline_id, origin_airport, destination_airport, status
        FROM dbo.FLIGHT
        ORDER BY flight_id
        """
    )
    sql_records = [
        {
            "flight_id": row.flight_id,
            "flight_number": row.flight_number,
            "airline_id": row.airline_id,
            "origin_airport": row.origin_airport,
            "destination_airport": row.destination_airport,
            "status": row.status,
        }
        for row in cursor.fetchall()
    ]
    mongo_records = [
        {
            "flight_id": doc["sql_flight_id"],
            "flight_number": doc["flight_number"],
            "airline_id": doc["sql_airline_id"],
            "origin_airport": doc["origin_airport"],
            "destination_airport": doc["destination_airport"],
            "status": doc["status"],
        }
        for doc in mongo_db.flights.find({}, {"_id": 0}).sort("sql_flight_id", 1)
    ]
    sql_checksum = collection_checksum(sql_records, "flight_id")
    mongo_checksum = collection_checksum(mongo_records, "flight_id")
    return ValidationResult(
        name="checksum:flights:key_fields",
        passed=sql_checksum == mongo_checksum,
        details=f"SQL={sql_checksum}, MongoDB={mongo_checksum}",
    )


def print_report(results: list[ValidationResult]) -> None:
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print("Validation Report")
    print("=================")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.name}: {result.details}")
    print("-----------------")
    print(f"Validation summary: {passed} passed, {failed} failed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate SQL Server source data against MongoDB target data.")
    parser.add_argument("--sql-driver", default=os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server"))
    parser.add_argument("--sql-server", default=os.getenv("SQLSERVER_HOST", "localhost"))
    parser.add_argument("--sql-database", default=os.getenv("SQLSERVER_DATABASE", "AirportManagement"))
    parser.add_argument("--sql-user", default=os.getenv("SQLSERVER_USER", "sa"))
    parser.add_argument("--sql-password", default=os.getenv("SQLSERVER_PASSWORD", "YourStrong!Passw0rd"))
    parser.add_argument("--mongo-uri", default=os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    parser.add_argument("--mongo-database", default=os.getenv("MONGODB_DATABASE", "airport_nosql"))
    parser.add_argument("--spot-check-limit", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sql_connection = connect_sql(args)
    mongo_client = connect_mongo(args)
    try:
        cursor = sql_connection.cursor()
        mongo_db = mongo_client[args.mongo_database]
        results = []
        results.extend(validate_counts(cursor, mongo_db))
        results.extend(validate_airline_aggregates(cursor, mongo_db))
        results.extend(validate_travel_agency_aggregates(cursor, mongo_db))
        results.extend(validate_client_spot_checks(cursor, mongo_db, args.spot_check_limit))
        results.append(validate_flight_checksum(cursor, mongo_db))
        print_report(results)
        if any(not result.passed for result in results):
            raise SystemExit(1)
    finally:
        sql_connection.close()
        mongo_client.close()


if __name__ == "__main__":
    main()
