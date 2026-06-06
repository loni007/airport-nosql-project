# Visualization Layer

Phase 9 provides three MongoDB-only visualizations using Plotly.

## Charts

- `airline_performance.html`: compares total flights, completed flights, and fleet size.
- `reservation_activity.html`: shows reservation volume and ticket value over time.
- `travel_agency_analytics.html`: compares agency ticket value and reservation count.

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Generate charts:

```powershell
python visualization/charts.py
```

The script reads only from MongoDB:

```text
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=airport_nosql
```

Output files are written to:

```text
visualization/output/
```

## Screenshot Targets

Capture one screenshot for each generated HTML file:

- Airline performance chart.
- Reservation activity chart.
- Travel agency analytics chart.
