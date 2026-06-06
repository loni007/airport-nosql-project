# Docker Setup

Phase 11 provides Docker support for the database services used by the project.

## Services

| Service | Purpose | Port |
| --- | --- | --- |
| `sqlserver` | SQL Server 2022 Developer source database | `1433` |
| `mongodb` | MongoDB target database | `27017` |
| `mongo-express` | Optional browser UI for MongoDB | `8081` |

## Start Services

From the project root:

```powershell
docker compose up -d
docker compose ps
```

Expected services:

```text
airport_sqlserver       running
airport_mongodb         running
airport_mongo_express   running
```

## Load SQL Server Data

After SQL Server is healthy:

```powershell
sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -i sql/schema.sql
sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -i sql/seed.sql
sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -i sql/generated_seed.sql
```

## Prepare MongoDB

```powershell
python mongodb/setup_collections.py --mongo-uri mongodb://localhost:27017 --database airport_nosql
```

## Stop Services

```powershell
docker compose down
```

To remove database volumes:

```powershell
docker compose down -v
```

Use `down -v` only when you intentionally want to delete local database data.

## Screenshot Targets

Capture:

- `docker compose up -d`
- `docker compose ps`
- SQL Server loaded row counts
- MongoDB collections visible after setup/migration
