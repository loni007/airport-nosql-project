"""Configuration helpers for the migration pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SqlServerConfig:
    driver: str
    server: str
    database: str
    user: str
    password: str

    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            "TrustServerCertificate=yes;"
        )


@dataclass(frozen=True)
class MongoConfig:
    uri: str
    database: str


@dataclass(frozen=True)
class MigrationConfig:
    sql: SqlServerConfig
    mongo: MongoConfig


def load_config() -> MigrationConfig:
    """Load database settings from environment variables with local defaults."""
    return MigrationConfig(
        sql=SqlServerConfig(
            driver=os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server"),
            server=os.getenv("SQLSERVER_HOST", "localhost"),
            database=os.getenv("SQLSERVER_DATABASE", "AirportManagement"),
            user=os.getenv("SQLSERVER_USER", "sa"),
            password=os.getenv("SQLSERVER_PASSWORD", "YourStrong!Passw0rd"),
        ),
        mongo=MongoConfig(
            uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            database=os.getenv("MONGODB_DATABASE", "airport_nosql"),
        ),
    )
