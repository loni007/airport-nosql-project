from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable


Row = dict[str, Any]


def to_float(value: Any) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def duration_minutes(start: datetime, end: datetime) -> int:
    if not start or not end:
        raise ValueError("flight row is malformed: missing scheduled departure or arrival")
    if end <= start:
        raise ValueError("flight row is malformed: scheduled_arrival must be after scheduled_departure")
    return int((end - start).total_seconds() // 60)


def build_airline_documents(airlines: Iterable[Row], flights: Iterable[Row], airplanes: Iterable[Row]) -> list[Row]:
    flight_counts: dict[int, int] = defaultdict(int)
    completed_counts: dict[int, int] = defaultdict(int)
    airplane_counts: dict[int, int] = defaultdict(int)

    for flight in flights:
        airline_id = flight["airline_id"]
        flight_counts[airline_id] += 1
        if flight.get("status") == "COMPLETED":
            completed_counts[airline_id] += 1

    for airplane in airplanes:
        airplane_counts[airplane["airline_id"]] += 1

    documents = []
    for airline in airlines:
        airline_id = airline["airline_id"]
        documents.append(
            {
                "sql_airline_id": airline_id,
                "airline_code": airline["airline_code"],
                "name": airline["name"],
                "country": airline["country"],
                "founded_year": airline.get("founded_year"),
                "headquarters_city": airline.get("headquarters_city"),
                "total_flights": flight_counts[airline_id],
                "total_airplanes": airplane_counts[airline_id],
                "completed_flights": completed_counts[airline_id],
            }
        )
    return documents


def build_airplane_documents(airplanes: Iterable[Row], airlines: Iterable[Row], models: Iterable[Row]) -> list[Row]:
    airline_by_id = {row["airline_id"]: row for row in airlines}
    model_by_id = {row["model_id"]: row for row in models}
    documents = []

    for airplane in airplanes:
        airline = airline_by_id.get(airplane["airline_id"])
        model = model_by_id.get(airplane["model_id"])
        if not airline or not model:
            raise ValueError(f"airplane {airplane['airplane_id']} has missing airline or model reference")

        documents.append(
            {
                "sql_airplane_id": airplane["airplane_id"],
                "registration_number": airplane["registration_number"],
                "manufacture_year": airplane["manufacture_year"],
                "status": airplane["status"],
                "airline": {
                    "sql_airline_id": airline["airline_id"],
                    "airline_code": airline["airline_code"],
                    "name": airline["name"],
                    "country": airline["country"],
                },
                "model": {
                    "sql_model_id": model["model_id"],
                    "manufacturer": model["manufacturer"],
                    "model_name": model["model_name"],
                    "seat_capacity": model["seat_capacity"],
                    "range_km": model["range_km"],
                },
            }
        )
    return documents


def build_flight_documents(
    flights: Iterable[Row],
    airlines: Iterable[Row],
    tickets: Iterable[Row],
    reservations: Iterable[Row],
) -> list[Row]:
    airline_by_id = {row["airline_id"]: row for row in airlines}
    ticket_count_by_flight: dict[int, int] = defaultdict(int)
    reserved_ticket_ids = {row["ticket_id"] for row in reservations}
    reserved_count_by_flight: dict[int, int] = defaultdict(int)

    for ticket in tickets:
        flight_id = ticket["flight_id"]
        ticket_count_by_flight[flight_id] += 1
        if ticket["ticket_id"] in reserved_ticket_ids:
            reserved_count_by_flight[flight_id] += 1

    documents = []
    for flight in flights:
        airline = airline_by_id.get(flight["airline_id"])
        if not airline:
            raise ValueError(f"flight {flight['flight_id']} has missing airline reference")

        documents.append(
            {
                "sql_flight_id": flight["flight_id"],
                "flight_number": flight["flight_number"],
                "sql_airline_id": flight["airline_id"],
                "sql_airplane_id": flight.get("airplane_id"),
                "airline_name": airline["name"],
                "origin_airport": flight["origin_airport"],
                "destination_airport": flight["destination_airport"],
                "scheduled_departure": flight["scheduled_departure"],
                "scheduled_arrival": flight["scheduled_arrival"],
                "flight_duration": duration_minutes(flight["scheduled_departure"], flight["scheduled_arrival"]),
                "status": flight["status"],
                "ticket_count": ticket_count_by_flight[flight["flight_id"]],
                "reserved_ticket_count": reserved_count_by_flight[flight["flight_id"]],
            }
        )
    return documents


def build_client_documents(clients: Iterable[Row], reservations: Iterable[Row], tickets: Iterable[Row]) -> list[Row]:
    reservations_by_client: dict[int, list[Row]] = defaultdict(list)
    ticket_by_id = {row["ticket_id"]: row for row in tickets}

    for reservation in reservations:
        reservations_by_client[reservation["client_id"]].append(reservation)

    documents = []
    for client in clients:
        client_reservations = reservations_by_client[client["client_id"]]
        agency_ids = {row["agency_id"] for row in client_reservations if row.get("agency_id") is not None}
        total_spent = sum(to_float(ticket_by_id[row["ticket_id"]]["price"]) for row in client_reservations if row["ticket_id"] in ticket_by_id)

        documents.append(
            {
                "sql_client_id": client["client_id"],
                "first_name": client["first_name"],
                "last_name": client["last_name"],
                "full_name": f"{client['first_name']} {client['last_name']}",
                "email": client["email"],
                "phone": client.get("phone"),
                "passport_number": client["passport_number"],
                "nationality": client["nationality"],
                "created_at": client["created_at"],
                "reservation_count": len(client_reservations),
                "agency_count": len(agency_ids),
                "total_spent": round(total_spent, 2),
            }
        )
    return documents


def build_travel_agency_documents(agencies: Iterable[Row], reservations: Iterable[Row], tickets: Iterable[Row]) -> list[Row]:
    reservations_by_agency: dict[int, list[Row]] = defaultdict(list)
    ticket_by_id = {row["ticket_id"]: row for row in tickets}

    for reservation in reservations:
        if reservation.get("agency_id") is not None:
            reservations_by_agency[reservation["agency_id"]].append(reservation)

    documents = []
    for agency in agencies:
        agency_reservations = reservations_by_agency[agency["agency_id"]]
        total_ticket_value = sum(
            to_float(ticket_by_id[row["ticket_id"]]["price"])
            for row in agency_reservations
            if row["ticket_id"] in ticket_by_id
        )

        documents.append(
            {
                "sql_agency_id": agency["agency_id"],
                "name": agency["name"],
                "city": agency["city"],
                "country": agency["country"],
                "email": agency["email"],
                "phone": agency.get("phone"),
                "total_reservations": len(agency_reservations),
                "total_ticket_value": round(total_ticket_value, 2),
            }
        )
    return documents
def build_reservation_documents(
    reservations: Iterable[Row],
    clients: Iterable[Row],
    tickets: Iterable[Row],
    flights: Iterable[Row],
    airlines: Iterable[Row],
    agencies: Iterable[Row],
) -> list[Row]:
    client_by_id = {row["client_id"]: row for row in clients}
    ticket_by_id = {row["ticket_id"]: row for row in tickets}
    flight_by_id = {row["flight_id"]: row for row in flights}
    airline_by_id = {row["airline_id"]: row for row in airlines}
    agency_by_id = {row["agency_id"]: row for row in agencies}
    documents = []

    for reservation in reservations:
        client = client_by_id.get(reservation["client_id"])
        ticket = ticket_by_id.get(reservation["ticket_id"])
        if not client or not ticket:
            raise ValueError(f"reservation {reservation['reserve_id']} has missing client or ticket reference")

        flight = flight_by_id.get(ticket["flight_id"])
        if not flight:
            raise ValueError(f"reservation {reservation['reserve_id']} has ticket with missing flight reference")

        airline = airline_by_id.get(flight["airline_id"])
        agency = agency_by_id.get(reservation.get("agency_id"))

        documents.append(
            {
                "sql_reserve_id": reservation["reserve_id"],
                "reserved_at": reservation["reserved_at"],
                "payment_status": reservation["payment_status"],
                "reservation_channel": reservation["reservation_channel"],
                "client": {
                    "sql_client_id": client["client_id"],
                    "full_name": f"{client['first_name']} {client['last_name']}",
                    "email": client["email"],
                    "passport_number": client["passport_number"],
                },
                "ticket": {
                    "sql_ticket_id": ticket["ticket_id"],
                    "ticket_number": ticket["ticket_number"],
                    "seat_number": ticket["seat_number"],
                    "cabin_class": ticket["cabin_class"],
                    "price": to_float(ticket["price"]),
                    "currency": ticket["currency"],
                },
                "flight": {
                    "sql_flight_id": flight["flight_id"],
                    "flight_number": flight["flight_number"],
                    "airline_name": airline["name"] if airline else None,
                    "origin_airport": flight["origin_airport"],
                    "destination_airport": flight["destination_airport"],
                },
                "agency": None
                if agency is None
                else {
                    "sql_agency_id": agency["agency_id"],
                    "name": agency["name"],
                },
            }
        )
    return documents


def build_maintenance_documents(care_rows: Iterable[Row], airplanes: Iterable[Row], employers: Iterable[Row]) -> list[Row]:
    airplane_by_id = {row["airplane_id"]: row for row in airplanes}
    employer_by_id = {row["employer_id"]: row for row in employers}
    documents = []

    for care in care_rows:
        airplane = airplane_by_id.get(care["airplane_id"])
        employer = employer_by_id.get(care["employer_id"])
        if not airplane or not employer:
            raise ValueError(f"care record {care['care_id']} has missing airplane or employer reference")

        documents.append(
            {
                "sql_care_id": care["care_id"],
                "care_type": care["care_type"],
                "care_date": care["care_date"],
                "notes": care.get("notes"),
                "cost": to_float(care["cost"]),
                "airplane": {
                    "sql_airplane_id": airplane["airplane_id"],
                    "registration_number": airplane["registration_number"],
                },
                "employer": {
                    "sql_employer_id": employer["employer_id"],
                    "full_name": f"{employer['first_name']} {employer['last_name']}",
                    "role": employer["role"],
                },
            }
        )
    return documents