/*
    Airport Management System - Baseline Seed Data
    Phase 2 deliverable

    Run this after sql/schema.sql. The dataset is intentionally small and
    human-readable. Phase 3 will add the Faker generator and 10,000+ records.
*/

USE AirportManagement;
GO

SET IDENTITY_INSERT dbo.AIRLINE ON;
INSERT INTO dbo.AIRLINE (
    airline_id, airline_code, name, country, founded_year, headquarters_city
) VALUES
    (1, 'MAK', N'Macedonian Air', N'North Macedonia', 1994, N'Skopje'),
    (2, 'ADR', N'Adria Regional', N'Slovenia', 1961, N'Ljubljana'),
    (3, 'BAL', N'Balkan Wings', N'Bulgaria', 2003, N'Sofia'),
    (4, 'AEE', N'Aegean Express Europe', N'Greece', 1999, N'Athens');
SET IDENTITY_INSERT dbo.AIRLINE OFF;
GO

SET IDENTITY_INSERT dbo.MODEL ON;
INSERT INTO dbo.MODEL (
    model_id, manufacturer, model_name, seat_capacity, range_km, max_takeoff_weight_kg
) VALUES
    (1, N'Airbus', N'A320neo', 180, 6300, 79000),
    (2, N'Boeing', N'737-800', 189, 5436, 79015),
    (3, N'Embraer', N'E195-E2', 132, 4815, 61500),
    (4, N'ATR', N'ATR 72-600', 72, 1528, 23000);
SET IDENTITY_INSERT dbo.MODEL OFF;
GO

SET IDENTITY_INSERT dbo.CLIENT ON;
INSERT INTO dbo.CLIENT (
    client_id, first_name, last_name, email, phone, passport_number, nationality, created_at
) VALUES
    (1, N'Elena', N'Petrova', N'elena.petrova@example.com', N'+38970111222', 'P1234567', N'North Macedonia', '2026-01-10T09:00:00'),
    (2, N'Marko', N'Ivanov', N'marko.ivanov@example.com', N'+38970222333', 'P2345678', N'North Macedonia', '2026-01-12T10:30:00'),
    (3, N'Ana', N'Koleva', N'ana.koleva@example.com', N'+359882001122', 'BG3456789', N'Bulgaria', '2026-01-15T13:15:00'),
    (4, N'Nikos', N'Papadopoulos', N'nikos.papadopoulos@example.com', N'+302101234567', 'GR4567890', N'Greece', '2026-01-18T16:45:00'),
    (5, N'Sara', N'Hoxha', N'sara.hoxha@example.com', N'+38344111222', 'XK5678901', N'Kosovo', '2026-01-20T08:20:00');
SET IDENTITY_INSERT dbo.CLIENT OFF;
GO

SET IDENTITY_INSERT dbo.TRAVELAGENCY ON;
INSERT INTO dbo.TRAVELAGENCY (
    agency_id, name, city, country, email, phone
) VALUES
    (1, N'Balkan Travel', N'Skopje', N'North Macedonia', N'bookings@balkantravel.example', N'+38923000111'),
    (2, N'Adria Tours', N'Ljubljana', N'Slovenia', N'office@adriatours.example', N'+38614000222'),
    (3, N'Aegean Holidays', N'Athens', N'Greece', N'contact@aegeanholidays.example', N'+30210300333');
SET IDENTITY_INSERT dbo.TRAVELAGENCY OFF;
GO

SET IDENTITY_INSERT dbo.AIRPLANE ON;
INSERT INTO dbo.AIRPLANE (
    airplane_id, registration_number, airline_id, model_id, manufacture_year, status
) VALUES
    (1, 'Z3-MAK', 1, 1, 2019, 'ACTIVE'),
    (2, 'Z3-OHD', 1, 3, 2021, 'ACTIVE'),
    (3, 'S5-ADR', 2, 2, 2017, 'MAINTENANCE'),
    (4, 'LZ-BAL', 3, 1, 2020, 'ACTIVE'),
    (5, 'SX-AEE', 4, 4, 2018, 'ACTIVE');
SET IDENTITY_INSERT dbo.AIRPLANE OFF;
GO

SET IDENTITY_INSERT dbo.EMPLOYER ON;
INSERT INTO dbo.EMPLOYER (
    employer_id, first_name, last_name, role, email, hire_date, airline_id
) VALUES
    (1, N'Viktor', N'Stojanovski', N'Maintenance Engineer', N'viktor.stojanovski@airport.example', '2018-04-01', 1),
    (2, N'Milena', N'Dimova', N'Flight Operations Manager', N'milena.dimova@airport.example', '2016-09-15', 3),
    (3, N'Janez', N'Novak', N'Aircraft Technician', N'janez.novak@airport.example', '2019-05-20', 2),
    (4, N'Dimitris', N'Georgiou', N'Safety Inspector', N'dimitris.georgiou@airport.example', '2020-02-10', NULL);
SET IDENTITY_INSERT dbo.EMPLOYER OFF;
GO

SET IDENTITY_INSERT dbo.FLIGHT ON;
INSERT INTO dbo.FLIGHT (
    flight_id, flight_number, airline_id, airplane_id, origin_airport, destination_airport,
    scheduled_departure, scheduled_arrival, status
) VALUES
    (1, 'MAK102', 1, 1, 'SKP', 'VIE', '2026-06-10T08:30:00', '2026-06-10T10:05:00', 'SCHEDULED'),
    (2, 'MAK215', 1, 2, 'OHD', 'IST', '2026-06-11T11:00:00', '2026-06-11T12:25:00', 'SCHEDULED'),
    (3, 'ADR330', 2, 3, 'LJU', 'FRA', '2026-06-10T07:15:00', '2026-06-10T09:00:00', 'DELAYED'),
    (4, 'BAL450', 3, 4, 'SOF', 'SKP', '2026-06-12T14:20:00', '2026-06-12T15:25:00', 'SCHEDULED'),
    (5, 'AEE810', 4, 5, 'ATH', 'SKP', '2026-06-13T18:10:00', '2026-06-13T19:40:00', 'SCHEDULED');
SET IDENTITY_INSERT dbo.FLIGHT OFF;
GO

SET IDENTITY_INSERT dbo.TICKET ON;
INSERT INTO dbo.TICKET (
    ticket_id, ticket_number, flight_id, seat_number, cabin_class, price, currency, ticket_status
) VALUES
    (1, 'TKT-000001', 1, '12A', 'ECONOMY', 210.50, 'USD', 'RESERVED'),
    (2, 'TKT-000002', 1, '12B', 'ECONOMY', 210.50, 'USD', 'RESERVED'),
    (3, 'TKT-000003', 2, '3C', 'BUSINESS', 420.00, 'USD', 'RESERVED'),
    (4, 'TKT-000004', 3, '8A', 'ECONOMY', 185.00, 'USD', 'RESERVED'),
    (5, 'TKT-000005', 4, '15D', 'ECONOMY', 140.00, 'USD', 'AVAILABLE'),
    (6, 'TKT-000006', 5, '2A', 'FIRST', 650.00, 'USD', 'RESERVED'),
    (7, 'TKT-000007', 5, '21C', 'ECONOMY', 175.00, 'USD', 'AVAILABLE');
SET IDENTITY_INSERT dbo.TICKET OFF;
GO

SET IDENTITY_INSERT dbo.RESERVE ON;
INSERT INTO dbo.RESERVE (
    reserve_id, client_id, ticket_id, agency_id, reserved_at, payment_status, reservation_channel
) VALUES
    (1, 1, 1, 1, '2026-05-01T14:22:00', 'PAID', 'AGENCY'),
    (2, 2, 2, NULL, '2026-05-02T09:10:00', 'PAID', 'WEB'),
    (3, 3, 3, 2, '2026-05-03T11:45:00', 'PENDING', 'AGENCY'),
    (4, 4, 4, NULL, '2026-05-04T17:30:00', 'PAID', 'MOBILE'),
    (5, 5, 6, 3, '2026-05-05T12:05:00', 'PAID', 'AGENCY');
SET IDENTITY_INSERT dbo.RESERVE OFF;
GO

SET IDENTITY_INSERT dbo.CARE ON;
INSERT INTO dbo.CARE (
    care_id, airplane_id, employer_id, care_type, care_date, notes, cost
) VALUES
    (1, 1, 1, N'Routine inspection', '2026-05-15', N'No issues found.', 850.00),
    (2, 3, 3, N'Engine diagnostics', '2026-05-20', N'Aircraft held for follow-up maintenance.', 2400.00),
    (3, 5, 4, N'Safety audit', '2026-05-22', N'Cabin equipment checked.', 1200.00);
SET IDENTITY_INSERT dbo.CARE OFF;
GO

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
