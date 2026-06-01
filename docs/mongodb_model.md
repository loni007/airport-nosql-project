# MongoDB Model Design

## Modeling Goals

The MongoDB design is optimized for reporting, validation, and visualization rather than a direct table copy. The migration will create documents that answer common airport management questions with fewer joins while preserving SQL identifiers for traceability.

## Collections

| Collection | Source Tables | Main Access Pattern |
| --- | --- | --- |
| `airlines` | AIRLINE, FLIGHT, AIRPLANE | Airline performance, fleet size, flight count |
| `airplanes` | AIRPLANE, AIRLINE, MODEL | Fleet lookup with embedded airline and model details |
| `flights` | FLIGHT, AIRLINE, AIRPLANE, TICKET | Flight schedule, duration, sales and reservation activity |
| `clients` | CLIENT, RESERVE, TRAVELAGENCY | Customer reservation profile |
| `travel_agencies` | TRAVELAGENCY, RESERVE, TICKET | Agency revenue and reservation analytics |
| `reservations` | RESERVE, CLIENT, TICKET, FLIGHT, TRAVELAGENCY | Reservation activity and spot-check validation |
| `maintenance` | CARE, AIRPLANE, EMPLOYER | Maintenance history |
| `migration_runs` | Migration runtime metadata | Idempotency audit and troubleshooting |

## Embedding and Referencing Strategy

### Embedded Data

- `airplanes` embeds compact `airline` and `model` subdocuments because aircraft detail screens need this data together and both parent records are relatively stable.
- `flights` embeds airline name and a compact airplane snapshot for reporting.
- `reservations` embeds compact client, ticket, flight, and agency snapshots so validation and visualization can read reservation activity from one collection.
- `maintenance` embeds compact airplane and employer snapshots because maintenance records are historical events.

### References

- Every document stores the original SQL primary key, for example `sql_airline_id`, `sql_flight_id`, and `sql_reserve_id`.
- Cross-document references use these SQL identifiers and, where useful, MongoDB ObjectIds after upsert.
- Large one-to-many relationships such as all flights for an airline are not embedded inside `airlines`; they are represented by aggregate counters and queried from `flights` when detail is required.

## Required Derived Fields

### `clients`

- `reservation_count`: Number of reservations made by the client.
- `agency_count`: Number of distinct travel agencies used by the client.
- Additional planned field: `total_spent`, based on paid/reserved ticket value.

### `airlines`

- `total_flights`: Number of flights operated by the airline.
- `total_airplanes`: Number of airplanes owned by the airline.
- Additional planned field: `completed_flights`, useful for performance visualization.

### `travel_agencies`

- `total_reservations`: Number of reservations created through the agency.
- `total_ticket_value`: Sum of ticket values for agency reservations.

### `airplanes`

- `airline`: Embedded airline information.
- `model`: Embedded model information.

### `flights`

- `airline_name`: Airline name copied from AIRLINE.
- `flight_duration`: Duration in minutes between scheduled departure and scheduled arrival.

## Proposed Document Shapes

### `airlines`

```json
{
  "sql_airline_id": 1,
  "airline_code": "MAK",
  "name": "Macedonian Air",
  "country": "North Macedonia",
  "founded_year": 1994,
  "headquarters_city": "Skopje",
  "total_flights": 420,
  "total_airplanes": 18,
  "completed_flights": 377,
  "updated_at": "2026-06-01T10:00:00Z"
}
```

### `airplanes`

```json
{
  "sql_airplane_id": 10,
  "registration_number": "Z3-ABC",
  "manufacture_year": 2018,
  "status": "ACTIVE",
  "airline": {
    "sql_airline_id": 1,
    "airline_code": "MAK",
    "name": "Macedonian Air",
    "country": "North Macedonia"
  },
  "model": {
    "sql_model_id": 2,
    "manufacturer": "Airbus",
    "model_name": "A320neo",
    "seat_capacity": 180,
    "range_km": 6300
  },
  "updated_at": "2026-06-01T10:00:00Z"
}
```

### `flights`

```json
{
  "sql_flight_id": 100,
  "flight_number": "MAK102",
  "airline_name": "Macedonian Air",
  "sql_airline_id": 1,
  "sql_airplane_id": 10,
  "origin_airport": "SKP",
  "destination_airport": "VIE",
  "scheduled_departure": "2026-06-10T08:30:00Z",
  "scheduled_arrival": "2026-06-10T10:05:00Z",
  "flight_duration": 95,
  "status": "SCHEDULED",
  "ticket_count": 180,
  "reserved_ticket_count": 136,
  "updated_at": "2026-06-01T10:00:00Z"
}
```

### `reservations`

```json
{
  "sql_reserve_id": 5000,
  "reserved_at": "2026-05-01T14:22:00Z",
  "payment_status": "PAID",
  "reservation_channel": "AGENCY",
  "client": {
    "sql_client_id": 300,
    "full_name": "Elena Petrova",
    "email": "elena.petrova@example.com",
    "passport_number": "P1234567"
  },
  "ticket": {
    "sql_ticket_id": 9000,
    "ticket_number": "TKT-9000",
    "seat_number": "12A",
    "cabin_class": "ECONOMY",
    "price": 210.50,
    "currency": "USD"
  },
  "flight": {
    "sql_flight_id": 100,
    "flight_number": "MAK102",
    "airline_name": "Macedonian Air",
    "origin_airport": "SKP",
    "destination_airport": "VIE"
  },
  "agency": {
    "sql_agency_id": 12,
    "name": "Balkan Travel"
  },
  "updated_at": "2026-06-01T10:00:00Z"
}
```

## Index Plan

| Collection | Index | Purpose |
| --- | --- | --- |
| `airlines` | Unique `sql_airline_id` | Idempotent upserts |
| `airlines` | Unique `airline_code` | Airline lookup |
| `airplanes` | Unique `sql_airplane_id` | Idempotent upserts |
| `airplanes` | Unique `registration_number` | Fleet lookup |
| `flights` | Unique `sql_flight_id` | Idempotent upserts |
| `flights` | `sql_airline_id`, `scheduled_departure` | Airline schedule queries |
| `clients` | Unique `sql_client_id` | Idempotent upserts |
| `clients` | Unique `email` | Customer lookup |
| `travel_agencies` | Unique `sql_agency_id` | Idempotent upserts |
| `reservations` | Unique `sql_reserve_id` | Idempotent upserts |
| `reservations` | `reserved_at` | Activity chart |
| `reservations` | `agency.sql_agency_id` | Agency analytics |
| `maintenance` | Unique `sql_care_id` | Idempotent upserts |

## Idempotency Rules

- Migration scripts will use `replace_one(..., upsert=True)` or bulk upserts keyed by SQL primary keys.
- Unique indexes on SQL identifiers prevent duplicate documents if migration is run multiple times.
- `migration_runs` records each run status, row counts, warnings, and error summaries.

## Validation Impact

The validation layer will compare SQL and MongoDB through:

- Exact collection/table counts where one SQL row maps to one Mongo document.
- Aggregation totals where Mongo documents contain derived fields.
- Checksums built from stable, normalized values.
- Spot checks by SQL primary key to verify embedded snapshots and derived fields.
