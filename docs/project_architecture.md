# Project Architecture

## Scope

This repository implements a SQL Server to MongoDB migration for an Airport Management System. The work is divided into phases so each stage is independently reviewable and testable.

## Target Directory Structure

```text
airport-nosql-project/
|-- sql/
|   |-- schema.sql
|   |-- seed.sql
|   `-- generate_fake_data.py
|-- migration/
|   |-- migrate.py
|   |-- transformers.py
|   `-- logger.py
|-- validation/
|   |-- validate.py
|   `-- checksum.py
|-- visualization/
|   |-- dashboard.ipynb
|   `-- charts.py
|-- docs/
|   |-- report.md
|   |-- er_diagram.md
|   |-- mongodb_model.md
|   `-- project_architecture.md
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

The current repository root is used as the project root rather than nesting another directory inside it.

## Phase Plan

| Phase | Deliverable | Verification |
| --- | --- | --- |
| 1 | Relational design, MongoDB design, architecture | Documentation exists and is internally consistent |
| 2 | SQL Server schema and baseline seed data | SQL schema can be executed in SQL Server |
| 3 | Faker data generator for 10,000+ records | Generated SQL/CSV maintains relational integrity |
| 4 | Final MongoDB collection/index design | Index creation script and model docs align |
| 5 | Migration pipeline skeleton | Connects to SQL Server and MongoDB with dry-run option |
| 6 | Data transformations | Derived fields generated from SQL source data |
| 7 | Logging and error handling | Malformed records and connection failures are handled explicitly |
| 8 | Validation layer | Pass/fail report compares SQL and MongoDB |
| 9 | Visualization layer | Charts read only from MongoDB |
| 10 | Documentation | README and report are complete |
| 11 | Docker support | SQL Server and MongoDB start through Compose |
| 12 | Final review | Full workflow runs cleanly from setup to validation |

## Runtime Components

### SQL Server

SQL Server is the source of truth for relational data. It will contain strict constraints so invalid records are blocked before migration, while controlled malformed input scenarios can still be tested by staging or script-level validation.

### Python Data Generator

The Faker-based generator will create realistic airport data with deterministic seeding. It will generate at least 10,000 records in a high-volume table, most likely `TICKET` and `RESERVE`, while preserving foreign key integrity.

### Migration Pipeline

The migration layer will:

- Read from SQL Server using parameterized queries.
- Transform rows into MongoDB document shapes.
- Upsert documents by stable SQL primary keys.
- Log row counts, warnings, skipped malformed rows, and connection errors.
- Continue when individual malformed source records can be skipped safely.

### MongoDB

MongoDB stores query-optimized documents, derived fields, and embedded snapshots used by validation and visualization. It is not a one-table-to-one-collection copy.

### Validation

Validation scripts compare SQL Server and MongoDB using counts, checksums, aggregate comparisons, and spot checks. Reports will be deterministic and readable from the terminal.

### Visualization

Charts read only from MongoDB and focus on:

- Airline performance.
- Reservation activity.
- Travel agency analytics.

## Configuration Plan

Python scripts will read connection settings from environment variables:

| Variable | Purpose |
| --- | --- |
| `SQLSERVER_HOST` | SQL Server host |
| `SQLSERVER_PORT` | SQL Server port |
| `SQLSERVER_DATABASE` | Source database |
| `SQLSERVER_USER` | SQL Server username |
| `SQLSERVER_PASSWORD` | SQL Server password |
| `MONGODB_URI` | MongoDB connection string |
| `MONGODB_DATABASE` | Destination database |

Development defaults will match `docker-compose.yml` once Docker support is added.

## Quality Rules

- Scripts must be idempotent where reruns are expected.
- Migration must not duplicate MongoDB data when executed multiple times.
- Logging must be explicit enough to explain skipped rows and failed connections.
- Validation must fail loudly when derived fields drift from SQL source data.
- Documentation must describe commands, expected output, and project assumptions.
