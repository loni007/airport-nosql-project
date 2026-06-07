# Phase 10 Report Sections

These sections can be copied into `docs/report.md` when Phase 10 starts.

## Choice of MongoDB

MongoDB was selected because the migrated airport data is best consumed through document-oriented reporting views. The relational source contains strongly connected tables such as airlines, airplanes, flights, tickets, clients, agencies, and reservations. In the relational model, useful questions require several joins, for example finding reservation activity by agency or showing a flight with airline and ticket information. MongoDB allows the project to store denormalized documents with embedded snapshots and derived fields, reducing query complexity for reporting and visualization.

The migration is intentionally not a direct table-to-collection copy. It produces documents that reflect expected access patterns:

- airline performance by total flights and total airplanes
- client profiles with reservation counts and agency usage
- travel agency analytics with reservation totals and ticket value
- airplanes with embedded airline and model details
- flights with airline names and calculated duration

MongoDB is also a good fit for the visualization layer because charts can read directly from collections that already contain reporting-ready fields.

## Comparison with Redis

Redis is a key-value database optimized for very fast lookups, caching, counters, sessions, leaderboards, and short-lived operational state. It could store airport data using keys such as:

```text
airline:1
client:300
flight:100
agency:12:reservation_count
```

This would be fast for direct key access, but it would be weaker for the project requirements because the dataset needs rich document structures, embedded data, aggregation validation, and visualization queries. Redis would require more manual key design and secondary indexing. It is less natural for storing full migrated reservation documents with nested flight, ticket, client, and agency information.

## Comparison with Neo4j

Neo4j is a graph database and would model the airport system through nodes and relationships:

```text
(:Client)-[:MADE]->(:Reservation)-[:FOR]->(:Ticket)-[:ON]->(:Flight)
(:Flight)-[:OPERATED_BY]->(:Airline)
(:Airplane)-[:OWNED_BY]->(:Airline)
(:Airplane)-[:HAS_MODEL]->(:Model)
(:TravelAgency)-[:CREATED]->(:Reservation)
```

Neo4j would be useful for path-based questions such as finding frequent client-agency-airline patterns or graph centrality of airports and agencies. However, the project focuses on migration with denormalized reporting documents, derived fields, validation checks, and charts. MongoDB is simpler and more direct for storing the transformed reporting shape.

## NoSQL Modeling

The MongoDB model uses collections for `airlines`, `airplanes`, `flights`, `clients`, `travel_agencies`, `reservations`, `maintenance`, and `migration_runs`. The design keeps SQL primary keys as `sql_*` fields so every MongoDB document can be traced back to the relational source.

Embedding decisions:

- `airplanes` embeds compact airline and model subdocuments because airplane lookups usually need these details together.
- `reservations` embeds client, ticket, flight, and agency snapshots because reservation analytics should not require repeated joins.
- `flights` stores `airline_name` and calculated `flight_duration` for schedule and performance reporting.

Referencing decisions:

- Large one-to-many relationships are not embedded fully inside parent documents. For example, airlines do not embed every flight. Instead, airline documents contain aggregate counters and flight details remain in the `flights` collection.
- SQL IDs remain in documents to support validation, idempotent upserts, and traceability.

## Data Transformations

The migration computes derived fields during transformation:

| Collection | Derived Field | Description |
| --- | --- | --- |
| `clients` | `reservation_count` | Number of reservations made by the client. |
| `clients` | `agency_count` | Number of distinct travel agencies used by the client. |
| `clients` | `total_spent` | Sum of ticket prices for the client reservations. |
| `airlines` | `total_flights` | Number of flights operated by the airline. |
| `airlines` | `total_airplanes` | Number of airplanes owned by the airline. |
| `travel_agencies` | `total_reservations` | Number of reservations created by the agency. |
| `travel_agencies` | `total_ticket_value` | Sum of ticket prices sold through the agency. |
| `airplanes` | embedded `airline` | Airline snapshot embedded in airplane document. |
| `airplanes` | embedded `model` | Aircraft model snapshot embedded in airplane document. |
| `flights` | `airline_name` | Airline name copied from the joined airline table. |
| `flights` | `flight_duration` | Duration in minutes between scheduled departure and arrival. |

These transformations prove that the migration is not a simple copy from SQL tables to MongoDB collections.

## Validation Results

The validation layer compares SQL Server and MongoDB after migration. It includes:

- record counts per mapped entity
- hash/checksum comparison for key flight fields
- airline aggregate comparisons
- travel agency revenue and reservation comparisons
- client spot checks for reservation counts and agency counts

Expected successful output:

```text
Validation Report
=================
PASS count:airlines
PASS count:airplanes
PASS count:flights
PASS count:clients
PASS count:travel_agencies
PASS count:reservations
PASS count:maintenance
PASS checksum:flights:key_fields
Validation summary: all checks passed
```

Any failed validation should be explained by identifying the source table, MongoDB collection, expected value, actual value, and likely cause.

## Final Demo Checklist

The final presentation should demonstrate:

```powershell
python sql/generate_fake_data.py --output sql/generated_seed.sql
python mongodb/setup_collections.py --dry-run
python migration/migrate.py
python migration/migrate.py
python validation/validate.py
python visualization/charts.py
```

The second migration run is required because it demonstrates idempotency.
