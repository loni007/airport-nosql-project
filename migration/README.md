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
