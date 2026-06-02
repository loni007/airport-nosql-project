"""
Generate a large, relationally consistent SQL Server seed script.

Run after Phase 2 files exist:

    python sql/generate_fake_data.py --output sql/generated_seed.sql

The generated SQL assumes that schema.sql and seed.sql have already been run.
It appends enough data for the course requirement that at least one table has
10,000+ records.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker


BASE_CLIENT_ID = 5
BASE_FLIGHT_ID = 5
BASE_TICKET_ID = 7
BASE_RESERVE_ID = 5
BASE_CARE_ID = 3

AIRLINE_IDS = [1, 2, 3, 4]
AIRPLANES = [
    {"airplane_id": 1, "airline_id": 1},
    {"airplane_id": 2, "airline_id": 1},
    {"airplane_id": 3, "airline_id": 2},
    {"airplane_id": 4, "airline_id": 3},
    {"airplane_id": 5, "airline_id": 4},
]
AGENCY_IDS = [1, 2, 3]
EMPLOYER_IDS = [1, 2, 3, 4]
AIRPORTS = [
    "SKP",
    "OHD",
    "LJU",
    "ZAG",
    "BEG",
    "SOF",
    "ATH",
    "IST",
    "VIE",
    "FRA",
    "MUC",
    "AMS",
    "FCO",
    "CDG",
    "LHR",
]
CABIN_CLASSES = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
PAYMENT_STATUSES = ["PAID", "PAID", "PAID", "PENDING", "REFUNDED"]
FLIGHT_STATUSES = ["SCHEDULED", "SCHEDULED", "SCHEDULED", "DELAYED", "COMPLETED"]
CARE_TYPES = [
    "Routine inspection",
    "Engine diagnostics",
    "Cabin equipment check",
    "Hydraulic system check",
    "Avionics inspection",
]


@dataclass(frozen=True)
class Flight:
    flight_id: int
    airline_id: int
    airplane_id: int


@dataclass(frozen=True)
class Ticket:
    ticket_id: int
    flight_id: int
    price: float


def sql_string(value: object) -> str:
    """Return a SQL literal for simple generated values."""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "N'" + str(value).replace("'", "''") + "'"


def sql_ascii(value: object) -> str:
    """Return a non-Unicode SQL string literal."""
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def batched_insert(table: str, columns: list[str], rows: list[tuple], unicode_strings: bool = True) -> str:
    literal = sql_string if unicode_strings else sql_ascii
    statements: list[str] = []
    batch_size = 500

    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        values = []
        for row in batch:
            values.append("    (" + ", ".join(literal(value) for value in row) + ")")

        statements.append(
            f"INSERT INTO dbo.{table} ({', '.join(columns)}) VALUES\n"
            + ",\n".join(values)
            + ";\nGO\n"
        )

    return "\n".join(statements)


def make_clients(fake: Faker, count: int) -> list[tuple]:
    rows = []
    used_passports: set[str] = set()

    for offset in range(1, count + 1):
        client_id = BASE_CLIENT_ID + offset
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"client{client_id:05d}@airport-demo.example"
        passport = f"PX{client_id:07d}"
        while passport in used_passports:
            passport = f"PX{fake.random_int(min=1000000, max=9999999)}"
        used_passports.add(passport)

        rows.append(
            (
                client_id,
                first_name,
                last_name,
                email,
                fake.phone_number()[:40],
                passport,
                fake.country(),
                fake.date_time_between(start_date="-2y", end_date="-30d").strftime("%Y-%m-%dT%H:%M:%S"),
            )
        )

    return rows


def make_flights(rng: random.Random, count: int) -> tuple[list[tuple], list[Flight]]:
    rows = []
    flights = []
    start_date = datetime(2026, 6, 15, 5, 0, 0)

    for offset in range(1, count + 1):
        flight_id = BASE_FLIGHT_ID + offset
        airplane = rng.choice(AIRPLANES)
        origin, destination = rng.sample(AIRPORTS, 2)
        departure = start_date + timedelta(hours=offset * 2, minutes=rng.randint(0, 45))
        duration_minutes = rng.randint(55, 220)
        arrival = departure + timedelta(minutes=duration_minutes)
        flight_number = f"A{airplane['airline_id']}{1000 + offset}"
        status = rng.choice(FLIGHT_STATUSES)

        rows.append(
            (
                flight_id,
                flight_number,
                airplane["airline_id"],
                airplane["airplane_id"],
                origin,
                destination,
                departure.strftime("%Y-%m-%dT%H:%M:%S"),
                arrival.strftime("%Y-%m-%dT%H:%M:%S"),
                status,
            )
        )
        flights.append(Flight(flight_id, airplane["airline_id"], airplane["airplane_id"]))

    return rows, flights


def seat_for(index: int) -> str:
    row = 1 + (index // 6)
    letter = "ABCDEF"[index % 6]
    return f"{row}{letter}"


def make_tickets(rng: random.Random, count: int, flights: list[Flight]) -> tuple[list[tuple], list[Ticket]]:
    rows = []
    tickets = []
    per_flight_counter = {flight.flight_id: 0 for flight in flights}

    for offset in range(1, count + 1):
        ticket_id = BASE_TICKET_ID + offset
        flight = flights[(offset - 1) % len(flights)]
        seat_index = per_flight_counter[flight.flight_id]
        per_flight_counter[flight.flight_id] += 1

        cabin_class = rng.choices(CABIN_CLASSES, weights=[72, 12, 13, 3], k=1)[0]
        base_price = {
            "ECONOMY": 90,
            "PREMIUM_ECONOMY": 170,
            "BUSINESS": 320,
            "FIRST": 620,
        }[cabin_class]
        price = round(base_price + rng.uniform(15, 180), 2)
        status = "RESERVED" if offset <= 12_000 else "AVAILABLE"

        rows.append(
            (
                ticket_id,
                f"TKT-{ticket_id:06d}",
                flight.flight_id,
                seat_for(seat_index),
                cabin_class,
                price,
                "USD",
                status,
            )
        )
        tickets.append(Ticket(ticket_id, flight.flight_id, price))

    return rows, tickets


def make_reservations(
    rng: random.Random,
    count: int,
    client_count: int,
    tickets: list[Ticket],
) -> list[tuple]:
    rows = []
    reservation_start = datetime(2026, 5, 10, 8, 0, 0)

    for offset in range(1, count + 1):
        reserve_id = BASE_RESERVE_ID + offset
        ticket = tickets[offset - 1]
        client_id = rng.randint(1, BASE_CLIENT_ID + client_count)
        use_agency = rng.random() < 0.42
        agency_id = rng.choice(AGENCY_IDS) if use_agency else None
        channel = "AGENCY" if use_agency else rng.choice(["DIRECT", "MOBILE", "WEB"])
        reserved_at = reservation_start + timedelta(minutes=offset * rng.randint(1, 5))

        rows.append(
            (
                reserve_id,
                client_id,
                ticket.ticket_id,
                agency_id,
                reserved_at.strftime("%Y-%m-%dT%H:%M:%S"),
                rng.choice(PAYMENT_STATUSES),
                channel,
            )
        )

    return rows


def make_care_records(fake: Faker, rng: random.Random, count: int) -> list[tuple]:
    rows = []
    for offset in range(1, count + 1):
        care_id = BASE_CARE_ID + offset
        care_date = fake.date_between(start_date="-180d", end_date="-5d").strftime("%Y-%m-%d")
        cost = round(rng.uniform(250, 7500), 2)

        rows.append(
            (
                care_id,
                rng.choice(AIRPLANES)["airplane_id"],
                rng.choice(EMPLOYER_IDS),
                rng.choice(CARE_TYPES),
                care_date,
                fake.sentence(nb_words=8),
                cost,
            )
        )

    return rows


def build_script(args: argparse.Namespace) -> str:
    fake = Faker()
    Faker.seed(args.seed)
    rng = random.Random(args.seed)

    client_rows = make_clients(fake, args.clients)
    flight_rows, flights = make_flights(rng, args.flights)
    ticket_rows, tickets = make_tickets(rng, args.tickets, flights)
    reserve_rows = make_reservations(rng, args.reservations, args.clients, tickets)
    care_rows = make_care_records(fake, rng, args.care_records)

    if args.reservations > args.tickets:
        raise ValueError("reservations cannot exceed tickets because each reservation needs a unique ticket")

    sections = [
        "/*\n"
        "    Generated airport dataset for Phase 3.\n"
        f"    Seed: {args.seed}\n"
        f"    Generated clients: {args.clients}\n"
        f"    Generated flights: {args.flights}\n"
        f"    Generated tickets: {args.tickets}\n"
        f"    Generated reservations: {args.reservations}\n"
        f"    Generated care records: {args.care_records}\n"
        "*/\n\n"
        "USE AirportManagement;\nGO\n",
        "SET IDENTITY_INSERT dbo.CLIENT ON;\nGO\n",
        batched_insert(
            "CLIENT",
            ["client_id", "first_name", "last_name", "email", "phone", "passport_number", "nationality", "created_at"],
            client_rows,
        ),
        "SET IDENTITY_INSERT dbo.CLIENT OFF;\nGO\n",
        "SET IDENTITY_INSERT dbo.FLIGHT ON;\nGO\n",
        batched_insert(
            "FLIGHT",
            [
                "flight_id",
                "flight_number",
                "airline_id",
                "airplane_id",
                "origin_airport",
                "destination_airport",
                "scheduled_departure",
                "scheduled_arrival",
                "status",
            ],
            flight_rows,
            unicode_strings=False,
        ),
        "SET IDENTITY_INSERT dbo.FLIGHT OFF;\nGO\n",
        "SET IDENTITY_INSERT dbo.TICKET ON;\nGO\n",
        batched_insert(
            "TICKET",
            ["ticket_id", "ticket_number", "flight_id", "seat_number", "cabin_class", "price", "currency", "ticket_status"],
            ticket_rows,
            unicode_strings=False,
        ),
        "SET IDENTITY_INSERT dbo.TICKET OFF;\nGO\n",
        "SET IDENTITY_INSERT dbo.RESERVE ON;\nGO\n",
        batched_insert(
            "RESERVE",
            ["reserve_id", "client_id", "ticket_id", "agency_id", "reserved_at", "payment_status", "reservation_channel"],
            reserve_rows,
            unicode_strings=False,
        ),
        "SET IDENTITY_INSERT dbo.RESERVE OFF;\nGO\n",
        "SET IDENTITY_INSERT dbo.CARE ON;\nGO\n",
        batched_insert(
            "CARE",
            ["care_id", "airplane_id", "employer_id", "care_type", "care_date", "notes", "cost"],
            care_rows,
        ),
        "SET IDENTITY_INSERT dbo.CARE OFF;\nGO\n",
        """
SELECT 'AIRLINE' AS table_name, COUNT(*) AS record_count FROM dbo.AIRLINE
UNION ALL SELECT 'MODEL', COUNT(*) FROM dbo.MODEL
UNION ALL SELECT 'CLIENT', COUNT(*) FROM dbo.CLIENT
UNION ALL SELECT 'TRAVELAGENCY', COUNT(*) FROM dbo.TRAVELAGENCY
UNION ALL SELECT 'AIRPLANE', COUNT(*) FROM dbo.AIRPLANE
UNION ALL SELECT 'EMPLOYER', COUNT(*) FROM dbo.EMPLOYER
UNION ALL SELECT 'FLIGHT', COUNT(*) FROM dbo.FLIGHT
UNION ALL SELECT 'TICKET', COUNT(*) FROM dbo.TICKET
UNION ALL SELECT 'RESERVE', COUNT(*) FROM dbo.RESERVE
UNION ALL SELECT 'CARE', COUNT(*) FROM dbo.CARE;
GO
""",
    ]

    return "\n".join(sections)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate large SQL Server airport seed data.")
    parser.add_argument("--output", default="sql/generated_seed.sql", help="Output SQL file path.")
    parser.add_argument("--seed", type=int, default=20260602, help="Random seed for reproducible data.")
    parser.add_argument("--clients", type=int, default=2000, help="Number of additional clients to generate.")
    parser.add_argument("--flights", type=int, default=800, help="Number of additional flights to generate.")
    parser.add_argument("--tickets", type=int, default=15000, help="Number of additional tickets to generate.")
    parser.add_argument("--reservations", type=int, default=12000, help="Number of additional reservations to generate.")
    parser.add_argument("--care-records", type=int, default=300, help="Number of additional maintenance records.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.reservations > args.tickets:
        raise SystemExit("--reservations cannot exceed --tickets")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_script(args), encoding="utf-8")

    print(f"Generated SQL file: {output}")
    print(f"Generated clients: {args.clients}")
    print(f"Generated flights: {args.flights}")
    print(f"Generated tickets: {args.tickets}")
    print(f"Generated reservations: {args.reservations}")
    print(f"Generated care records: {args.care_records}")
    print(f"Expected total TICKET records after seed.sql: {BASE_TICKET_ID + args.tickets}")
    print(f"Expected total RESERVE records after seed.sql: {BASE_RESERVE_ID + args.reservations}")


if __name__ == "__main__":
    main()
