"""Database connection helpers used by the migration pipeline."""

from __future__ import annotations

from typing import Any

from config import MongoConfig, SqlServerConfig
from errors import DatabaseConnectionError


def connect_sql(config: SqlServerConfig) -> Any:
    """Connect to SQL Server using pyodbc."""
    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError("pyodbc is required. Run: python -m pip install -r requirements.txt") from exc

    try:
        return pyodbc.connect(config.connection_string, timeout=10)
    except Exception as exc:
        raise DatabaseConnectionError(f"SQL Server connection failed: {exc}") from exc


def connect_mongo(config: MongoConfig) -> Any:
    """Connect to MongoDB and verify the server responds."""
    try:
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError("pymongo is required. Run: python -m pip install -r requirements.txt") from exc

    try:
        client = MongoClient(config.uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except Exception as exc:
        raise DatabaseConnectionError(f"MongoDB connection failed: {exc}") from exc


def fetch_source_counts(sql_connection: Any) -> dict[str, int]:
    """Return source row counts for every relational entity."""
    queries = {
        "AIRLINE": "SELECT COUNT(*) FROM dbo.AIRLINE",
        "MODEL": "SELECT COUNT(*) FROM dbo.MODEL",
        "CLIENT": "SELECT COUNT(*) FROM dbo.CLIENT",
        "TRAVELAGENCY": "SELECT COUNT(*) FROM dbo.TRAVELAGENCY",
        "AIRPLANE": "SELECT COUNT(*) FROM dbo.AIRPLANE",
        "EMPLOYER": "SELECT COUNT(*) FROM dbo.EMPLOYER",
        "FLIGHT": "SELECT COUNT(*) FROM dbo.FLIGHT",
        "TICKET": "SELECT COUNT(*) FROM dbo.TICKET",
        "RESERVE": "SELECT COUNT(*) FROM dbo.RESERVE",
        "CARE": "SELECT COUNT(*) FROM dbo.CARE",
    }

    cursor = sql_connection.cursor()
    counts: dict[str, int] = {}
    for table_name, query in queries.items():
        cursor.execute(query)
        counts[table_name] = int(cursor.fetchone()[0])
    return counts


def ensure_migration_run_indexes(database: Any) -> None:
    """Create indexes needed before migration run metadata is written."""
    database.migration_runs.create_index("run_id", name="uq_migration_runs_run_id", unique=True)
    database.migration_runs.create_index([("started_at", -1)], name="idx_migration_runs_started_at")
