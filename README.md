# Airport NoSQL Migration Project

This project migrates a SQL Server Airport Management System database to MongoDB with a query-oriented NoSQL model, derived fields, validation scripts, visualizations, and Docker support.

## Current Status

Phase 1 is complete: relational design, MongoDB modeling strategy, and project architecture.

## Phase 1 Documents

- `docs/er_diagram.md`: relational entity design, constraints, cardinalities, and Mermaid ER diagram.
- `docs/mongodb_model.md`: MongoDB collections, embedding/reference strategy, derived fields, indexes, and idempotency rules.
- `docs/project_architecture.md`: phased implementation plan, target structure, runtime components, and configuration plan.

## Planned Workflow

1. Build SQL Server schema and seed data.
2. Generate large relationally consistent data with Faker.
3. Build MongoDB collection/index setup.
4. Implement idempotent migration with transformations.
5. Add logging, error handling, validation, and visualizations.
6. Complete Docker support and final report.

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
