/*
    Airport Management System - SQL Server Schema
    Phase 2 deliverable

    This script creates the relational source database used by the MongoDB
    migration project. It is intentionally idempotent: rerunning it drops the
    existing project tables in dependency order and recreates them.
*/

IF DB_ID(N'AirportManagement') IS NULL
BEGIN
    CREATE DATABASE AirportManagement;
END;
GO

USE AirportManagement;
GO

DROP TABLE IF EXISTS dbo.CARE;
DROP TABLE IF EXISTS dbo.RESERVE;
DROP TABLE IF EXISTS dbo.TICKET;
DROP TABLE IF EXISTS dbo.FLIGHT;
DROP TABLE IF EXISTS dbo.EMPLOYER;
DROP TABLE IF EXISTS dbo.AIRPLANE;
DROP TABLE IF EXISTS dbo.MODEL;
DROP TABLE IF EXISTS dbo.TRAVELAGENCY;
DROP TABLE IF EXISTS dbo.CLIENT;
DROP TABLE IF EXISTS dbo.AIRLINE;
GO

CREATE TABLE dbo.AIRLINE (
    airline_id INT IDENTITY(1,1) NOT NULL,
    airline_code VARCHAR(8) NOT NULL,
    name NVARCHAR(120) NOT NULL,
    country NVARCHAR(80) NOT NULL,
    founded_year SMALLINT NULL,
    headquarters_city NVARCHAR(100) NULL,
    CONSTRAINT PK_AIRLINE PRIMARY KEY (airline_id),
    CONSTRAINT UQ_AIRLINE_code UNIQUE (airline_code),
    CONSTRAINT UQ_AIRLINE_name UNIQUE (name),
    CONSTRAINT CK_AIRLINE_founded_year CHECK (
        founded_year IS NULL OR founded_year BETWEEN 1900 AND 2026
    )
);
GO

CREATE TABLE dbo.MODEL (
    model_id INT IDENTITY(1,1) NOT NULL,
    manufacturer NVARCHAR(100) NOT NULL,
    model_name NVARCHAR(100) NOT NULL,
    seat_capacity INT NOT NULL,
    range_km INT NOT NULL,
    max_takeoff_weight_kg INT NULL,
    CONSTRAINT PK_MODEL PRIMARY KEY (model_id),
    CONSTRAINT UQ_MODEL_manufacturer_name UNIQUE (manufacturer, model_name),
    CONSTRAINT CK_MODEL_seat_capacity CHECK (seat_capacity > 0),
    CONSTRAINT CK_MODEL_range_km CHECK (range_km > 0),
    CONSTRAINT CK_MODEL_max_takeoff_weight CHECK (
        max_takeoff_weight_kg IS NULL OR max_takeoff_weight_kg > 0
    )
);
GO

CREATE TABLE dbo.CLIENT (
    client_id INT IDENTITY(1,1) NOT NULL,
    first_name NVARCHAR(80) NOT NULL,
    last_name NVARCHAR(80) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    phone NVARCHAR(40) NULL,
    passport_number VARCHAR(30) NOT NULL,
    nationality NVARCHAR(80) NOT NULL,
    created_at DATETIME2(0) NOT NULL CONSTRAINT DF_CLIENT_created_at DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_CLIENT PRIMARY KEY (client_id),
    CONSTRAINT UQ_CLIENT_email UNIQUE (email),
    CONSTRAINT UQ_CLIENT_passport_number UNIQUE (passport_number)
);
GO

CREATE TABLE dbo.TRAVELAGENCY (
    agency_id INT IDENTITY(1,1) NOT NULL,
    name NVARCHAR(150) NOT NULL,
    city NVARCHAR(100) NOT NULL,
    country NVARCHAR(80) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    phone NVARCHAR(40) NULL,
    CONSTRAINT PK_TRAVELAGENCY PRIMARY KEY (agency_id),
    CONSTRAINT UQ_TRAVELAGENCY_name UNIQUE (name),
    CONSTRAINT UQ_TRAVELAGENCY_email UNIQUE (email)
);
GO

CREATE TABLE dbo.AIRPLANE (
    airplane_id INT IDENTITY(1,1) NOT NULL,
    registration_number VARCHAR(20) NOT NULL,
    airline_id INT NOT NULL,
    model_id INT NOT NULL,
    manufacture_year SMALLINT NOT NULL,
    status VARCHAR(20) NOT NULL CONSTRAINT DF_AIRPLANE_status DEFAULT 'ACTIVE',
    CONSTRAINT PK_AIRPLANE PRIMARY KEY (airplane_id),
    CONSTRAINT UQ_AIRPLANE_registration_number UNIQUE (registration_number),
    CONSTRAINT FK_AIRPLANE_AIRLINE FOREIGN KEY (airline_id) REFERENCES dbo.AIRLINE(airline_id),
    CONSTRAINT FK_AIRPLANE_MODEL FOREIGN KEY (model_id) REFERENCES dbo.MODEL(model_id),
    CONSTRAINT CK_AIRPLANE_manufacture_year CHECK (
        manufacture_year BETWEEN 1960 AND 2026
    ),
    CONSTRAINT CK_AIRPLANE_status CHECK (status IN ('ACTIVE', 'MAINTENANCE', 'RETIRED'))
);
GO

CREATE TABLE dbo.EMPLOYER (
    employer_id INT IDENTITY(1,1) NOT NULL,
    first_name NVARCHAR(80) NOT NULL,
    last_name NVARCHAR(80) NOT NULL,
    role NVARCHAR(80) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    airline_id INT NULL,
    CONSTRAINT PK_EMPLOYER PRIMARY KEY (employer_id),
    CONSTRAINT UQ_EMPLOYER_email UNIQUE (email),
    CONSTRAINT FK_EMPLOYER_AIRLINE FOREIGN KEY (airline_id) REFERENCES dbo.AIRLINE(airline_id),
    CONSTRAINT CK_EMPLOYER_hire_date CHECK (hire_date <= '2026-12-31')
);
GO

CREATE TABLE dbo.FLIGHT (
    flight_id INT IDENTITY(1,1) NOT NULL,
    flight_number VARCHAR(16) NOT NULL,
    airline_id INT NOT NULL,
    airplane_id INT NULL,
    origin_airport CHAR(3) NOT NULL,
    destination_airport CHAR(3) NOT NULL,
    scheduled_departure DATETIME2(0) NOT NULL,
    scheduled_arrival DATETIME2(0) NOT NULL,
    status VARCHAR(20) NOT NULL CONSTRAINT DF_FLIGHT_status DEFAULT 'SCHEDULED',
    CONSTRAINT PK_FLIGHT PRIMARY KEY (flight_id),
    CONSTRAINT UQ_FLIGHT_airline_number_departure UNIQUE (airline_id, flight_number, scheduled_departure),
    CONSTRAINT FK_FLIGHT_AIRLINE FOREIGN KEY (airline_id) REFERENCES dbo.AIRLINE(airline_id),
    CONSTRAINT FK_FLIGHT_AIRPLANE FOREIGN KEY (airplane_id) REFERENCES dbo.AIRPLANE(airplane_id),
    CONSTRAINT CK_FLIGHT_airports CHECK (origin_airport <> destination_airport),
    CONSTRAINT CK_FLIGHT_schedule CHECK (scheduled_arrival > scheduled_departure),
    CONSTRAINT CK_FLIGHT_origin_airport CHECK (origin_airport NOT LIKE '%[^A-Z]%'),
    CONSTRAINT CK_FLIGHT_destination_airport CHECK (destination_airport NOT LIKE '%[^A-Z]%'),
    CONSTRAINT CK_FLIGHT_status CHECK (status IN ('SCHEDULED', 'DELAYED', 'CANCELLED', 'COMPLETED'))
);
GO

CREATE TABLE dbo.TICKET (
    ticket_id INT IDENTITY(1,1) NOT NULL,
    ticket_number VARCHAR(30) NOT NULL,
    flight_id INT NOT NULL,
    seat_number VARCHAR(8) NOT NULL,
    cabin_class VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    currency CHAR(3) NOT NULL CONSTRAINT DF_TICKET_currency DEFAULT 'USD',
    ticket_status VARCHAR(20) NOT NULL CONSTRAINT DF_TICKET_status DEFAULT 'AVAILABLE',
    CONSTRAINT PK_TICKET PRIMARY KEY (ticket_id),
    CONSTRAINT UQ_TICKET_ticket_number UNIQUE (ticket_number),
    CONSTRAINT UQ_TICKET_flight_seat UNIQUE (flight_id, seat_number),
    CONSTRAINT FK_TICKET_FLIGHT FOREIGN KEY (flight_id) REFERENCES dbo.FLIGHT(flight_id),
    CONSTRAINT CK_TICKET_cabin_class CHECK (
        cabin_class IN ('ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST')
    ),
    CONSTRAINT CK_TICKET_price CHECK (price >= 0),
    CONSTRAINT CK_TICKET_currency CHECK (currency NOT LIKE '%[^A-Z]%'),
    CONSTRAINT CK_TICKET_status CHECK (ticket_status IN ('AVAILABLE', 'RESERVED', 'CANCELLED', 'USED'))
);
GO

CREATE TABLE dbo.RESERVE (
    reserve_id INT IDENTITY(1,1) NOT NULL,
    client_id INT NOT NULL,
    ticket_id INT NOT NULL,
    agency_id INT NULL,
    reserved_at DATETIME2(0) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    reservation_channel VARCHAR(20) NOT NULL,
    CONSTRAINT PK_RESERVE PRIMARY KEY (reserve_id),
    CONSTRAINT UQ_RESERVE_ticket UNIQUE (ticket_id),
    CONSTRAINT FK_RESERVE_CLIENT FOREIGN KEY (client_id) REFERENCES dbo.CLIENT(client_id),
    CONSTRAINT FK_RESERVE_TICKET FOREIGN KEY (ticket_id) REFERENCES dbo.TICKET(ticket_id),
    CONSTRAINT FK_RESERVE_TRAVELAGENCY FOREIGN KEY (agency_id) REFERENCES dbo.TRAVELAGENCY(agency_id),
    CONSTRAINT CK_RESERVE_payment_status CHECK (payment_status IN ('PENDING', 'PAID', 'REFUNDED', 'FAILED')),
    CONSTRAINT CK_RESERVE_channel CHECK (reservation_channel IN ('DIRECT', 'AGENCY', 'MOBILE', 'WEB')),
    CONSTRAINT CK_RESERVE_agency_channel CHECK (
        (reservation_channel = 'AGENCY' AND agency_id IS NOT NULL)
        OR (reservation_channel <> 'AGENCY')
    )
);
GO

CREATE TABLE dbo.CARE (
    care_id INT IDENTITY(1,1) NOT NULL,
    airplane_id INT NOT NULL,
    employer_id INT NOT NULL,
    care_type NVARCHAR(80) NOT NULL,
    care_date DATE NOT NULL,
    notes NVARCHAR(500) NULL,
    cost DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_CARE PRIMARY KEY (care_id),
    CONSTRAINT FK_CARE_AIRPLANE FOREIGN KEY (airplane_id) REFERENCES dbo.AIRPLANE(airplane_id),
    CONSTRAINT FK_CARE_EMPLOYER FOREIGN KEY (employer_id) REFERENCES dbo.EMPLOYER(employer_id),
    CONSTRAINT CK_CARE_date CHECK (care_date <= '2026-12-31'),
    CONSTRAINT CK_CARE_cost CHECK (cost >= 0)
);
GO

CREATE INDEX IX_AIRPLANE_airline_id ON dbo.AIRPLANE(airline_id);
CREATE INDEX IX_AIRPLANE_model_id ON dbo.AIRPLANE(model_id);
CREATE INDEX IX_EMPLOYER_airline_id ON dbo.EMPLOYER(airline_id);
CREATE INDEX IX_FLIGHT_airline_departure ON dbo.FLIGHT(airline_id, scheduled_departure);
CREATE INDEX IX_FLIGHT_airplane_id ON dbo.FLIGHT(airplane_id);
CREATE INDEX IX_TICKET_flight_id ON dbo.TICKET(flight_id);
CREATE INDEX IX_RESERVE_client_id ON dbo.RESERVE(client_id);
CREATE INDEX IX_RESERVE_agency_id ON dbo.RESERVE(agency_id);
CREATE INDEX IX_RESERVE_reserved_at ON dbo.RESERVE(reserved_at);
CREATE INDEX IX_CARE_airplane_id ON dbo.CARE(airplane_id);
CREATE INDEX IX_CARE_employer_id ON dbo.CARE(employer_id);
GO
