"""Generate the final project report PDF from structured report content."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "docs" / "final_project_report.pdf"


def styles():
    base = getSampleStyleSheet()
    base["Title"].fontSize = 20
    base["Title"].leading = 24
    base["Heading1"].fontSize = 15
    base["Heading1"].leading = 18
    base["Heading2"].fontSize = 12
    base["Heading2"].leading = 15
    base["BodyText"].fontSize = 9.5
    base["BodyText"].leading = 13
    base.add(
        ParagraphStyle(
            name="CodeBlock",
            parent=base["BodyText"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            backColor=colors.whitesmoke,
            borderColor=colors.lightgrey,
            borderWidth=0.25,
            borderPadding=4,
        )
    )
    return base


def p(text: str, style_name: str = "BodyText"):
    return Paragraph(text, STYLES[style_name])


def table(rows: list[list[str]], widths: list[float] | None = None):
    data = [[p(str(cell)) for cell in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def code(text: str):
    escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return p(escaped.replace("\n", "<br/>"), "CodeBlock")


def add_section(story, title: str):
    story.append(Spacer(1, 0.25 * cm))
    story.append(p(title, "Heading1"))
    story.append(Spacer(1, 0.1 * cm))


def build_story():
    story = []
    story.append(p("Airport Management System: Relational to MongoDB Migration", "Title"))
    story.append(p("Final Project Report"))
    story.append(p("NoSQL Database Course Project"))
    story.append(p("Repository: https://github.com/loni007/airport-nosql-project"))
    story.append(Spacer(1, 0.5 * cm))

    add_section(story, "1. Introduction")
    story.append(p("This project demonstrates an end-to-end migration from a relational SQL Server Airport Management System database to MongoDB. The work includes relational schema design, large synthetic data population, NoSQL data modeling, programmatic migration with transformations, validation, visualization, Docker-based database services, and final review documentation."))
    story.append(p("The project domain is airport management. The relational database contains airlines, airplanes, aircraft models, flights, clients, employers, travel agencies, tickets, reservations, and maintenance care records. MongoDB was chosen as the NoSQL target because the final workload is reporting-oriented and benefits from denormalized documents with embedded snapshots and precomputed fields."))

    add_section(story, "2. Relational Database Design")
    story.append(p("The SQL Server database is named AirportManagement. The schema is implemented in sql/schema.sql and contains ten relational tables. The ER diagram is documented in docs/er_diagram.md with primary keys, foreign keys, and cardinalities."))
    story.append(table([
        ["Table", "Purpose"],
        ["AIRLINE", "Airline company metadata."],
        ["MODEL", "Aircraft model metadata."],
        ["AIRPLANE", "Physical airplanes assigned to airlines and models."],
        ["FLIGHT", "Scheduled flights operated by airlines."],
        ["CLIENT", "Passengers/customers."],
        ["EMPLOYER", "Staff members involved in operations or maintenance."],
        ["TRAVELAGENCY", "Agencies that can create reservations."],
        ["TICKET", "Flight tickets and seat assignments."],
        ["RESERVE", "Reservation transactions."],
        ["CARE", "Maintenance/service records."],
    ], [3.2 * cm, 12.5 * cm]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(p("The schema includes primary keys on every table, foreign keys for all relationships, NOT NULL constraints, unique constraints, and multiple CHECK constraints for business rules such as valid statuses, positive prices, different origin/destination airports, and valid reservation agency usage."))

    add_section(story, "3. Data Population")
    story.append(p("Baseline seed data is implemented in sql/seed.sql. Large synthetic data is generated by sql/generate_fake_data.py using Faker. The generated SQL is stored in sql/generated_seed.sql."))
    story.append(table([
        ["Entity", "Record Count"],
        ["AIRLINE", "4"],
        ["MODEL", "4"],
        ["CLIENT", "2,005"],
        ["TRAVELAGENCY", "3"],
        ["AIRPLANE", "5"],
        ["EMPLOYER", "4"],
        ["FLIGHT", "805"],
        ["TICKET", "15,007"],
        ["RESERVE", "12,005"],
        ["CARE", "303"],
    ], [6 * cm, 5 * cm]))
    story.append(p("The TICKET and RESERVE tables both exceed the 10,000-record requirement while preserving relational integrity."))

    add_section(story, "4. Choice of MongoDB")
    story.append(p("MongoDB was selected because the target workload is document-oriented reporting and visualization. Common airport questions require joined data in the relational model, while MongoDB allows the final reporting views to be stored as denormalized documents with embedded snapshots and derived fields."))
    story.append(p("MongoDB supports nested document structures, indexes for idempotent upserts, Python integration through PyMongo, and convenient visualization workflows."))

    add_section(story, "5. Comparison with Redis and Neo4j")
    story.append(p("Redis is a key-value database optimized for caching, counters, queues, and direct lookups. It would be fast for keys such as airline:1 or client:300, but it is less natural for rich nested reservation documents and validation-oriented reporting queries."))
    story.append(p("Neo4j is a graph database. It could model Client-MADE-Reservation-FOR-Ticket-ON-Flight relationships, but the project focuses on denormalized reporting documents, validation checks, and dashboards. MongoDB is therefore the simpler and more suitable target."))
    story.append(code("(:Client)-[:MADE]->(:Reservation)-[:FOR]->(:Ticket)-[:ON]->(:Flight)\n(:Flight)-[:OPERATED_BY]->(:Airline)\n(:Airplane)-[:OWNED_BY]->(:Airline)\n(:TravelAgency)-[:CREATED]->(:Reservation)"))

    add_section(story, "6. NoSQL Database Modeling")
    story.append(table([
        ["Collection", "Source Tables", "Purpose"],
        ["airlines", "AIRLINE, FLIGHT, AIRPLANE", "Airline performance and fleet counts."],
        ["airplanes", "AIRPLANE, AIRLINE, MODEL", "Fleet lookup with embedded airline/model details."],
        ["flights", "FLIGHT, AIRLINE, TICKET, RESERVE", "Flight schedule and reservation activity."],
        ["clients", "CLIENT, RESERVE, TICKET", "Customer reservation profile."],
        ["travel_agencies", "TRAVELAGENCY, RESERVE, TICKET", "Agency analytics."],
        ["reservations", "RESERVE, CLIENT, TICKET, FLIGHT, AIRLINE, TRAVELAGENCY", "Denormalized reservation records."],
        ["maintenance", "CARE, AIRPLANE, EMPLOYER", "Maintenance history."],
        ["migration_runs", "Runtime metadata", "Migration audit and idempotency evidence."],
    ], [3.5 * cm, 5.2 * cm, 7 * cm]))
    story.append(p("Embedding is used for stable, compact data that is frequently read together, such as airplane airline/model snapshots and reservation client/ticket/flight/agency snapshots. Large one-to-many relationships are not fully embedded; instead, aggregate counters and separate collections are used."))

    add_section(story, "7. Migration Process")
    story.append(p("The migration pipeline is implemented in migration/migrate.py. It connects to SQL Server and MongoDB, reads relational rows, transforms them into MongoDB document structures, normalizes values for BSON, and writes them using idempotent upserts keyed by SQL primary keys."))
    story.append(table([
        ["Collection", "Migrated Documents"],
        ["airlines", "4"],
        ["airplanes", "5"],
        ["flights", "805"],
        ["clients", "2,005"],
        ["travel_agencies", "3"],
        ["reservations", "12,005"],
        ["maintenance", "303"],
    ], [6 * cm, 5 * cm]))
    story.append(p("The migration was rerun with a stable run id to demonstrate idempotency. Because each document is upserted by its SQL ID, repeated runs update existing documents instead of duplicating data."))

    add_section(story, "8. Data Transformations")
    story.append(table([
        ["Collection", "Derived/Embedded Field", "Description"],
        ["clients", "reservation_count", "Number of reservations made by the client."],
        ["clients", "agency_count", "Number of distinct travel agencies used."],
        ["clients", "total_spent", "Sum of ticket prices for the client."],
        ["airlines", "total_flights", "Number of flights operated by the airline."],
        ["airlines", "total_airplanes", "Number of airplanes owned by the airline."],
        ["airlines", "completed_flights", "Number of completed flights."],
        ["travel_agencies", "total_reservations", "Number of reservations created by agency."],
        ["travel_agencies", "total_ticket_value", "Sum of agency ticket prices."],
        ["airplanes", "embedded airline/model", "Airline and model snapshots inside airplane document."],
        ["flights", "airline_name, flight_duration", "Joined airline name and duration in minutes."],
    ], [3.8 * cm, 4.8 * cm, 7.2 * cm]))

    add_section(story, "9. Error Handling")
    story.append(p("Error handling is implemented in migration/errors.py, migration/logger.py, and migration/error_demo.py. The required scenarios are malformed source records and database connection failures."))
    story.append(code("Malformed flight source record skipped\nMalformed reservation source record skipped\nSQL Server connection failure handled\nMongoDB connection failure handled"))

    add_section(story, "10. Validation Results")
    story.append(p("Validation is implemented in validation/validate.py and validation/checksum.py. It compares record counts, checksums, aggregations, and spot-check queries."))
    story.append(code("PASS count:airlines: SQL=4, MongoDB=4\nPASS count:clients: SQL=2005, MongoDB=2005\nPASS count:reservations: SQL=12005, MongoDB=12005\nPASS checksum:flights:key_fields\nValidation summary: 25 passed, 0 failed"))

    add_section(story, "11. Visualization Layer")
    story.append(p("The visualization layer is implemented in visualization/charts.py using Plotly. It reads only from MongoDB."))
    story.append(table([
        ["Visualization", "Output File", "Data Source"],
        ["Airline performance", "visualization/output/airline_performance.html", "airlines"],
        ["Reservation activity", "visualization/output/reservation_activity.html", "reservations"],
        ["Travel agency analytics", "visualization/output/travel_agency_analytics.html", "travel_agencies"],
    ], [4.6 * cm, 7 * cm, 4 * cm]))

    add_section(story, "12. Docker Support")
    story.append(p("Docker support is implemented in docker-compose.yml and includes SQL Server 2022 Developer, MongoDB, and Mongo Express."))
    story.append(code("docker compose up -d\ndocker compose ps\nsqlcmd -S localhost -U sa -P \"YourStrong!Passw0rd\" -C -i sql/schema.sql\npython mongodb/setup_collections.py --mongo-uri mongodb://localhost:27017 --database airport_nosql"))

    add_section(story, "13. Presentation Demo Flow")
    story.append(code("docker compose ps\npython migration/migrate.py\npython migration/migrate.py --run-id demo-idempotency\npython validation/validate.py\npython visualization/charts.py\npython migration/error_demo.py"))

    add_section(story, "14. Conclusion")
    story.append(p("The project successfully implements a complete relational-to-NoSQL migration pipeline. SQL Server is used as the normalized source database with constraints and a large synthetic dataset. MongoDB is used as the denormalized target database with embedded documents and derived fields. The migration is programmatic, idempotent, logged, and validated. The visualization layer proves that the migrated MongoDB data is usable for analytics."))
    story.append(p("The final validation passed with 25 checks and 0 failures, confirming that the migration output matches the relational source for counts, checksums, aggregates, and spot checks."))
    return story


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Airport NoSQL Migration Project")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


STYLES = styles()


def main() -> None:
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    doc.build(build_story(), onFirstPage=page_footer, onLaterPages=page_footer)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
