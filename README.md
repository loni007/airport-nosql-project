# Airport NoSQL Migration Project

This project migrates a SQL Server Airport Management System database to MongoDB with a query-oriented NoSQL model, derived fields, validation scripts, visualizations, and Docker support.

## Current Status

Phase 1 is complete: relational design, MongoDB modeling strategy, and project architecture.


## Phase 1 Documents

- `docs/er_diagram.md`: relational entity design, constraints, cardinalities, and Mermaid ER diagram.
- `docs/mongodb_model.md`: MongoDB collections, embedding/reference strategy, derived fields, indexes, and idempotency rules.
- `docs/project_architecture.md`: phased implementation plan, target structure, runtime components, and configuration plan.
- `docs/screenshot_checklist.md`: exact screenshots and demo evidence to capture for the report and presentation.
- `docs/team_split.md`: 50/50 team responsibility split for a two-student submission.
- `mongodb/setup_collections.py`: MongoDB collection and index setup script with dry-run support.
- `mongodb/README.md`: MongoDB setup commands and index explanation.
- `migration/migrate.py`: migration pipeline entry point.
- `migration/README.md`: migration configuration and run instructions.

## Planned Workflow

1. Build SQL Server schema and seed data.
2. Generate large relationally consistent data with Faker.
3. Build MongoDB collection/index setup.
4. Implement idempotent migration with transformations.
5. Add logging, error handling, validation, and visualizations.
6. Complete Docker support and final report.

## Course Deliverable Checklist

- Relational database with ER diagram, constraints, and 10,000+ records in at least one table.
- MongoDB model with documented embedding and referencing decisions.
- Programmatic migration with non-1:1 transformations and derived fields.
- Idempotent migration that can be rerun without duplicates.
- Explicit error handling for malformed source records and connection failures.
- Automated validation with counts, checksums, aggregation checks, and spot checks.
- Three MongoDB-only visualizations.
- Final report, screenshots, README instructions, and presentation-ready demo.

## Requirements

The implementation phases will use:

- SQL Server
- MongoDB
- Python 3.11 or newer
- Faker
- PyODBC or SQLAlchemy
- PyMongo
- Plotly or Matplotlib

Detailed setup commands will be added in later phases once the runnable scripts exist.
