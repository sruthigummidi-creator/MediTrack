# MediTrack

MediTrack is a web-based healthcare management application developed using
Python, FastAPI, SQLAlchemy, SQLite, HTML, CSS, JavaScript and Chart.js.

## 1. Project Overview

MediTrack provides a centralized platform for managing:

- Patient registration and profiles
- Appointment booking, updating and cancellation
- Doctor consultations
- Prescriptions
- Treatment information
- Patient notifications
- Role-based access
- JWT authentication
- Audit logging
- Analytics dashboard
- CSV and PDF reports

The application runs as a web application and can be accessed through
Google Chrome.

## 2. Main Features

### Patient Management
- Register patients
- Store patient information
- View patient profiles
- Maintain patient records

### Appointment Management
- Book appointments
- Update appointments
- Cancel/delete appointments
- Prevent duplicate doctor time slots
- Track appointment status:
  - Pending
  - Completed
  - Cancelled

### Consultation and Prescription
- Record consultations
- Store symptoms, diagnosis and treatment
- Create prescriptions
- Maintain treatment-related information

### Authentication and Security
- Login authentication
- Role-based access for patients and doctors
- JWT token verification
- Failed-login audit logging
- Appointment audit logging
- Protected audit-log API

## 3. Analytics

The dashboard provides:

- Total patients
- Total appointments
- Total consultations
- Total prescriptions
- Appointment status distribution
- Patient age distribution
- Gender distribution
- Doctor consultation statistics
- Visit trends by day

Charts are displayed using Chart.js.

## 4. Reporting

MediTrack supports appointment reports in:

- CSV format
- PDF format

CSV endpoint:

    /reports/appointments.csv

PDF endpoint:

    /reports/appointments.pdf

## 5. System Architecture

The application follows a simple layered architecture:

    Browser
       |
       v
    FastAPI Application
       |
       +---- Authentication
       |
       +---- Business Logic
       |
       +---- REST APIs
       |
       +---- Analytics
       |
       +---- Reporting
       |
       v
    SQLAlchemy ORM
       |
       v
    SQLite Database

## 6. Database

The application uses SQLite with SQLAlchemy ORM.

Main database tables/models include:

- Patient
- Appointment
- Consultation
- Prescription
- Notification
- User
- AuditLog

Alembic is used for database migrations.

## 7. APIs

Important API endpoints include:

    GET    /api/patients
    POST   /api/appointments
    GET    /api/appointments
    PUT    /api/appointments/{appointment_id}
    DELETE /api/appointments/{appointment_id}
    GET    /api/audit-logs

Reports:

    GET /reports/appointments.csv
    GET /reports/appointments.pdf

## 8. Authentication

MediTrack uses JWT-based authentication.

The application verifies JWT tokens using:

- Secret key
- HS256 algorithm
- Username
- Role
- Patient ID

Role-based access is used to restrict protected functionality.

## 9. Installation

Install Python 3.12 or compatible Python version.

Install required packages:

    pip install fastapi
    pip install sqlalchemy
    pip install python-jose
    pip install alembic
    pip install reportlab
    pip install pytest
    pip install httpx2

## 10. Database Migration

Run:

    python -m alembic upgrade head

This applies all database migrations.

## 11. Running the Application

Start the MediTrack application using the project's configured
FastAPI/Uvicorn command.

Then open the application in Chrome.

Default local address:

    http://127.0.0.1:8000

## 12. Dashboard

After login, the dashboard provides visual analytics including:

- System statistics
- Appointment status
- Age distribution
- Gender distribution
- Doctor consultation analytics
- Visit trends

## 13. Testing

MediTrack includes automated tests using pytest.

Run:

    python -m pytest test_app.py -v -s

Current tests cover:

- Valid JWT token
- Invalid JWT token
- Dashboard availability
- Unauthorized audit-log access
- Dashboard performance

The performance test checks that the dashboard responds within
the defined response-time threshold.

## 14. Performance Optimization

Database indexes were added to frequently queried fields:

- Appointment date
- Appointment doctor
- Appointment status
- Consultation patient ID

These indexes improve filtering and lookup performance.

## 15. Security Testing

Security tests verify:

- Valid JWT tokens are accepted
- Invalid JWT tokens are rejected
- Unauthorized audit-log access is blocked

## 16. Reporting

Appointment data can be exported for external use.

CSV reports are suitable for:

- Spreadsheet analysis
- Data processing
- Record sharing

PDF reports are suitable for:

- Printing
- Documentation
- Formal reporting

## 17. Deployment

Before deployment:

1. Apply database migrations.
2. Install all dependencies.
3. Configure the application.
4. Start the FastAPI server.
5. Open the application in a browser.
6. Verify authentication.
7. Verify appointments.
8. Verify analytics.
9. Verify reports.
10. Perform user acceptance testing.

## 18. User Acceptance Testing

The following workflows should be verified:

- Patient registration
- Login
- Appointment booking
- Appointment update
- Appointment cancellation
- Consultation recording
- Prescription creation
- Dashboard analytics
- CSV report generation
- PDF report generation
- Logout

## 19. Milestone 4 Validation

Milestone 4 includes:

- Analytics
- Reporting
- Unit testing
- Integration testing
- Security testing
- Performance testing
- Database optimization
- Documentation
- Deployment
- User acceptance testing

## 20. Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- JWT
- HTML
- CSS
- JavaScript
- Chart.js
- ReportLab
- pytest

## 21. Project Status

MediTrack Milestone 4 development includes analytics, reporting,
automated testing, security testing, performance testing,
database optimization and project documentation.