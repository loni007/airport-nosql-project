# Phase 12 Final Review Checklist

Use this checklist before submission and presentation.

## Repository

- [ ] GitHub repository is accessible.
- [ ] Commits are separated by phase.
- [ ] No generated cache files are committed.
- [ ] README explains setup and execution.
- [ ] Both students understand the repository structure.

## SQL Server

- [ ] `sql/schema.sql` runs successfully.
- [ ] `sql/seed.sql` runs successfully.
- [ ] `sql/generated_seed.sql` runs successfully.
- [ ] At least one table has 10,000+ rows.
- [ ] Primary keys, foreign keys, unique constraints, `NOT NULL`, and check constraints are visible.
- [ ] Record-count screenshot is captured.

## MongoDB

- [ ] MongoDB is running.
- [ ] `mongodb/setup_collections.py` creates collections and indexes.
- [ ] Collections exist in MongoDB Compass.
- [ ] Unique indexes exist for idempotent SQL IDs.
- [ ] MongoDB collection screenshot is captured.

## Migration

- [ ] Migration connects to SQL Server.
- [ ] Migration connects to MongoDB.
- [ ] Migration writes all required collections.
- [ ] Migration computes required derived fields.
- [ ] Migration embeds airline/model information in airplane documents.
- [ ] Migration embeds reservation snapshots.
- [ ] Migration can run twice without duplicates.
- [ ] Migration rerun screenshot is captured.

## Error Handling

- [ ] Malformed source row scenario is demonstrated or logged.
- [ ] Database connection failure scenario is demonstrated or logged.
- [ ] Logs are readable and include severity, timestamp, and message.
- [ ] Migration continues when only one malformed row is encountered.

## Validation

- [ ] Record-count validation passes.
- [ ] Checksum/hash validation passes.
- [ ] Aggregation comparisons pass.
- [ ] Spot checks pass.
- [ ] Validation summary screenshot is captured.

## Visualization

- [ ] Airline performance chart reads only from MongoDB.
- [ ] Reservation activity chart reads only from MongoDB.
- [ ] Travel agency analytics chart reads only from MongoDB.
- [ ] Chart screenshots are captured.

## Report

- [ ] Introduction is complete.
- [ ] Relational Database Design section includes ER diagram.
- [ ] Data Population section includes counts and screenshots.
- [ ] Choice of MongoDB is justified.
- [ ] Redis comparison is included.
- [ ] Neo4j comparison is included.
- [ ] One alternative NoSQL schema sketch is included.
- [ ] NoSQL Modeling section explains embedding and referencing.
- [ ] Migration Process section explains idempotency.
- [ ] Data Transformations section lists derived fields.
- [ ] Validation Results section includes output and explanation.
- [ ] Visualization Layer section includes screenshots.
- [ ] Conclusion is complete.

## Presentation

- [ ] Demo fits in 5-10 minutes.
- [ ] Both students know their parts.
- [ ] Both students can explain each other's work at a high level.
- [ ] Demo commands are practiced.
- [ ] Screenshots are ready in case live demo fails.

## Final Commands

```powershell
python sql/generate_fake_data.py --output sql/generated_seed.sql
python mongodb/setup_collections.py --dry-run
python migration/migrate.py
python migration/migrate.py
python validation/validate.py
python visualization/charts.py
```
