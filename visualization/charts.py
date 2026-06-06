"""
Phase 9 MongoDB-only visualization layer.

The charts in this script read exclusively from MongoDB collections created by
the migration. They do not query SQL Server.

Usage:
    python visualization/charts.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import plotly.graph_objects as go
from pymongo import MongoClient


OUTPUT_DIR = Path("visualization/output")


def connect_mongo(uri: str, database_name: str) -> Any:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client, client[database_name]


def airline_performance_chart(database: Any) -> go.Figure:
    airlines = list(
        database.airlines.find(
            {},
            {
                "_id": 0,
                "name": 1,
                "total_flights": 1,
                "total_airplanes": 1,
                "completed_flights": 1,
            },
        ).sort("total_flights", -1)
    )

    names = [row["name"] for row in airlines]
    total_flights = [row.get("total_flights", 0) for row in airlines]
    completed_flights = [row.get("completed_flights", 0) for row in airlines]
    airplanes = [row.get("total_airplanes", 0) for row in airlines]

    figure = go.Figure()
    figure.add_bar(name="Total flights", x=names, y=total_flights)
    figure.add_bar(name="Completed flights", x=names, y=completed_flights)
    figure.add_scatter(
        name="Airplanes",
        x=names,
        y=airplanes,
        mode="lines+markers",
        yaxis="y2",
    )
    figure.update_layout(
        title="Airline Performance",
        xaxis_title="Airline",
        yaxis_title="Flights",
        yaxis2={
            "title": "Airplanes",
            "overlaying": "y",
            "side": "right",
            "rangemode": "tozero",
        },
        barmode="group",
        template="plotly_white",
    )
    return figure


def reservation_activity_chart(database: Any) -> go.Figure:
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$reserved_at",
                    }
                },
                "reservations": {"$sum": 1},
                "ticket_value": {"$sum": "$ticket.price"},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    rows = list(database.reservations.aggregate(pipeline))

    dates = [row["_id"] for row in rows]
    reservations = [row["reservations"] for row in rows]
    ticket_value = [round(row.get("ticket_value", 0), 2) for row in rows]

    figure = go.Figure()
    figure.add_scatter(name="Reservations", x=dates, y=reservations, mode="lines+markers")
    figure.add_bar(name="Ticket value", x=dates, y=ticket_value, yaxis="y2", opacity=0.45)
    figure.update_layout(
        title="Reservation Activity",
        xaxis_title="Reservation date",
        yaxis_title="Reservations",
        yaxis2={
            "title": "Ticket value",
            "overlaying": "y",
            "side": "right",
            "rangemode": "tozero",
        },
        template="plotly_white",
    )
    return figure


def travel_agency_analytics_chart(database: Any) -> go.Figure:
    agencies = list(
        database.travel_agencies.find(
            {},
            {
                "_id": 0,
                "name": 1,
                "total_reservations": 1,
                "total_ticket_value": 1,
            },
        ).sort("total_ticket_value", -1)
    )

    names = [row["name"] for row in agencies]
    reservations = [row.get("total_reservations", 0) for row in agencies]
    ticket_value = [round(row.get("total_ticket_value", 0), 2) for row in agencies]

    figure = go.Figure()
    figure.add_bar(name="Total ticket value", x=names, y=ticket_value)
    figure.add_scatter(
        name="Total reservations",
        x=names,
        y=reservations,
        mode="lines+markers",
        yaxis="y2",
    )
    figure.update_layout(
        title="Travel Agency Analytics",
        xaxis_title="Travel agency",
        yaxis_title="Ticket value",
        yaxis2={
            "title": "Reservations",
            "overlaying": "y",
            "side": "right",
            "rangemode": "tozero",
        },
        template="plotly_white",
    )
    return figure


def save_chart(figure: go.Figure, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    figure.write_html(path, include_plotlyjs="cdn", full_html=True)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MongoDB-only airport analytics charts.")
    parser.add_argument("--mongo-uri", default=os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    parser.add_argument("--database", default=os.getenv("MONGODB_DATABASE", "airport_nosql"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client, database = connect_mongo(args.mongo_uri, args.database)
    try:
        outputs = [
            save_chart(airline_performance_chart(database), "airline_performance.html"),
            save_chart(reservation_activity_chart(database), "reservation_activity.html"),
            save_chart(travel_agency_analytics_chart(database), "travel_agency_analytics.html"),
        ]
        print("Generated MongoDB-only visualization files:")
        for output in outputs:
            print(f"- {output}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
