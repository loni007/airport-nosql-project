# Migration Pipeline

This folder contains the SQL Server to MongoDB migration implementation.

## Phase 5 Scope

Phase 5 provides a runnable migration skeleton:

- Loads SQL Server and MongoDB settings from environment variables.
- Connects to SQL Server.
- Connects to MongoDB.
- Reads source table counts from SQL Server.
- Writes an idempotent `migration_runs` metadata document when not in dry-run mode.

The actual data transformation and collection upserts are added in later phases.

## Phase 7 Logging and Error Handling

Phase 7 adds:

- Console and file logging through `migration/logger.py`.
- Explicit database connection failure handling.
- Explicit malformed source record validation helpers.
- A standalone error scenario demo script.

Logs are written to:

```text
logs/migration.log
```

## Environment Variables

| Variable | Default |
| --- | --- |
| `SQLSERVER_DRIVER` | `ODBC Driver 17 for SQL Server` |
| `SQLSERVER_HOST` | `localhost` |
| `SQLSERVER_DATABASE` | `AirportManagement` |
| `SQLSERVER_USER` | `sa` |
| `SQLSERVER_PASSWORD` | `YourStrong!Passw0rd` |
| `MONGODB_URI` | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | `airport_nosql` |

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Dry-run:

```powershell
python migration/migrate.py --dry-run
```

Write migration metadata:

```powershell
python migration/migrate.py
```

Demonstrate idempotent metadata upsert:

```powershell
python migration/migrate.py --run-id demo-run
python migration/migrate.py --run-id demo-run
```

## Error Scenario Demo

Run the Phase 7 error demonstration:

```powershell
python migration/error_demo.py
```

Expected behavior:

- A malformed flight row is logged and skipped.
- A malformed reservation row is logged and skipped.
- A SQL Server connection failure is logged.
- A MongoDB connection failure is logged.

The script exits normally because these failures are intentionally handled for demonstration.
