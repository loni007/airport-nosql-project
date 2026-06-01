# Team Split

This project is planned as a two-person, 50/50 university submission. Both students should understand the full system well enough to answer presentation questions, but responsibilities are split so work is balanced and traceable.

## Student A Responsibilities

- Relational database design and SQL Server implementation.
- SQL constraints, primary keys, foreign keys, unique constraints, and check constraints.
- Faker-based synthetic data generation.
- Record-count proof for the populated relational database.
- ER diagram and relational design explanation.

## Student B Responsibilities

- MongoDB document model implementation.
- Migration pipeline and transformation logic.
- Idempotency handling.
- Validation scripts and pass/fail report.
- Visualization layer reading from MongoDB.

## Shared Responsibilities

- NoSQL database choice and comparison with Redis and Neo4j.
- Error-handling scenarios and logging review.
- Docker setup verification.
- Final README and report review.
- Presentation and live demonstration.

## Presentation Ownership

Both students should be ready to explain:

- Why MongoDB was chosen.
- How relational tables map to MongoDB documents.
- Which fields are derived during migration.
- How the migration avoids duplicates when rerun.
- How validation proves SQL Server and MongoDB remain consistent.
- What each visualization shows and why it reads only from MongoDB.

## Suggested Phase Ownership

| Phase | Primary Owner | Reviewer |
| --- | --- | --- |
| 1. Design and architecture | Student A | Student B |
| 2. SQL Server schema and seed data | Student A | Student B |
| 3. Faker large dataset | Student A | Student B |
| 4. MongoDB collection design | Student B | Student A |
| 5. Migration pipeline | Student B | Student A |
| 6. Data transformations | Student B | Student A |
| 7. Logging and error handling | Student B | Student A |
| 8. Validation layer | Student B | Student A |
| 9. Visualizations | Student B | Student A |
| 10. Documentation | Shared | Shared |
| 11. Docker support | Shared | Shared |
| 12. Final review | Shared | Shared |

Before submission, each student should run the full project locally and practice explaining one part owned by the other student.
