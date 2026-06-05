# MongoDB Setup

This folder contains the Phase 4 MongoDB database structure setup.

## Collections

The project uses these MongoDB collections:

- `airlines`
- `airplanes`
- `flights`
- `clients`
- `travel_agencies`
- `reservations`
- `maintenance`
- `migration_runs`

The model is intentionally not a one-table-to-one-collection copy. Later migration phases will add embedded snapshots and derived fields described in `docs/mongodb_model.md`.

## Dry Run

Verify the collection and index plan without a MongoDB server:

```powershell
python mongodb/setup_collections.py --dry-run
```

## Apply to MongoDB

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run against local MongoDB:

```powershell
python mongodb/setup_collections.py --mongo-uri mongodb://localhost:27017 --database airport_nosql
```

Environment variables are also supported:

```powershell
$env:MONGODB_URI="mongodb://localhost:27017"
$env:MONGODB_DATABASE="airport_nosql"
python mongodb/setup_collections.py
```

## Index Purpose

The unique indexes on `sql_*` fields make migration idempotent. Running the migration repeatedly will update existing documents instead of creating duplicates.

Analytics indexes support:

- Airline schedule queries.
- Reservation activity by date.
- Travel agency analytics.
- Client and flight spot checks.
