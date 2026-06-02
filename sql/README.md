# SQL Server Setup

This folder contains the Phase 2 relational database deliverables.

## Files

- `schema.sql`: creates the `AirportManagement` database and all relational tables.
- `seed.sql`: inserts a small valid starter dataset for smoke testing.

Phase 3 will add the Faker generator and large 10,000+ record dataset.

## Run With `sqlcmd`

Update the server name if your SQL Server instance is different.

```powershell
sqlcmd -S localhost -U sa -P "<password>" -i sql/schema.sql
sqlcmd -S localhost -U sa -P "<password>" -i sql/seed.sql
```

For Windows authentication:

```powershell
sqlcmd -S localhost -E -i sql/schema.sql
sqlcmd -S localhost -E -i sql/seed.sql
```

## Expected Phase 2 Counts

After running `seed.sql`, the final query should return:

| table_name | record_count |
| --- | ---: |
| AIRLINE | 4 |
| MODEL | 4 |
| CLIENT | 5 |
| TRAVELAGENCY | 3 |
| AIRPLANE | 5 |
| EMPLOYER | 4 |
| FLIGHT | 5 |
| TICKET | 7 |
| RESERVE | 5 |
| CARE | 3 |

## Constraint Coverage

The schema includes:

- Primary keys on every table.
- Foreign keys for all relationships.
- `NOT NULL` constraints where business data is required.
- Unique constraints for codes, names, emails, passport numbers, registration numbers, tickets, and seats.
- Multiple `CHECK` constraints for status values, prices, capacities, airport codes, schedule order, and dates.

## Screenshot Target

For the final report, capture:

- SQL Server table list.
- The row-count output from `seed.sql`.
- Constraint/key view from SQL Server Management Studio or an equivalent metadata query.
