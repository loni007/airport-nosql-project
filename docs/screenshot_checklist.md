# Screenshot and Demo Checklist

This checklist defines the evidence that should be captured for the final report and presentation. Screenshots should be taken as each phase is completed instead of waiting until the final day.

## Required Screenshots

### Repository Evidence

- GitHub repository homepage for `airport-nosql-project`.
- Git commit history showing multiple phase commits.

### Relational Database

- Rendered ER diagram from `docs/er_diagram.md`.
- SQL Server table list.
- SQL Server record-count query output for all tables.
- Proof that at least one table contains 10,000 or more records.
- SQL Server keys and constraints view, or query output listing primary keys, foreign keys, unique constraints, and check constraints.

### Data Generation

- Terminal output from the Faker generator showing generated row counts.
- Generated large-table count, preferably `TICKET` or `RESERVE`.

### MongoDB

- MongoDB Compass collection list after migration.
- Example `clients` document showing `reservation_count` and `agency_count`.
- Example `airlines` document showing `total_flights` and `total_airplanes`.
- Example `travel_agencies` document showing `total_reservations` and `total_ticket_value`.
- Example `airplanes` document showing embedded `airline` and `model`.
- Example `flights` document showing `airline_name` and `flight_duration`.

### Migration

- First migration run showing successful inserts or upserts.
- Second migration run showing idempotency: no duplicate data and no crash.
- Migration log entry showing a malformed source row handled gracefully.
- Migration log entry showing a database connection failure handled gracefully.

### Validation

- Validation report console output showing pass/fail checks.
- Record-count validation.
- Checksum validation.
- Aggregation comparison.
- Spot-check query comparison.

### Visualization

- Airline performance chart.
- Reservation activity chart.
- Travel agency analytics chart.

### Docker

- `docker compose up -d` output.
- `docker compose ps` output showing SQL Server and MongoDB running.
- Optional: SQL Server Management Studio connected to Docker SQL Server.
- Optional: MongoDB Compass connected to Docker MongoDB.

## Minimum Evidence Set

If time is tight, capture at least:

1. ER diagram.
2. SQL Server record counts with one table over 10,000 rows.
3. SQL Server constraints.
4. MongoDB collections.
5. MongoDB transformed documents with derived fields.
6. Migration run and rerun.
7. Validation pass summary.
8. Three visualization charts.

## Demo Commands

The final presentation should demonstrate these commands after the relevant scripts exist:

```powershell
python migration/migrate.py
python migration/migrate.py
python validation/validate.py
python visualization/charts.py
```

The second migration run is important because it proves idempotency.
