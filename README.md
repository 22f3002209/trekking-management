#
# Trekking Management Application

A role-based web application for managing trekking activities, bookings, trek staff, and trekkers.

This project was developed as part of the Modern Application Development I course in the IIT Madras BS Degree program. The application is designed to make trek management easier by bringing trek creation, staff assignment, booking management, participant tracking, and trekking history into one system.

## Features

The application has three types of users:

### Admin
- Secure login
- Create and manage treks
- Manage trek staff and trekkers
- Approve or reject trek staff registration requests
- Assign staff members to treks
- View bookings and trekking history
- Search records by name or ID
- View overall statistics through the dashboard

### Trek Staff
- Register and log in
- Manage profile
- View assigned treks
- Update trek status
- Update available slots
- View participant details
- Track completed treks
- Maintain trekking records

### Trekker
- Register and log in
- Browse available treks
- Search and filter treks
- Book treks
- Cancel bookings
- Check booking status
- View personal trekking history

## Some Important Functionalities

The application includes validations to handle common booking and management problems:

- Prevents duplicate trek bookings
- Prevents overbooking
- Allows bookings only for open treks with available slots
- Prevents staff scheduling conflicts
- Restricts trek management to assigned staff
- Maintains booking and trekking history after trek completion
- Provides role-based access to different parts of the application

## Technologies Used

### Backend
- Python
- Flask
- Flask-Login
- SQLAlchemy

### Database
- SQLite

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Jinja2

## Database

The application uses SQLite with separate tables for:

- Admin
- Trek Staff
- Trekker
- Trek
- Booking
- Trek History

The database is used to manage users, treks, bookings, staff assignments, and trekking records.

## Project Structure

```text
Trekking-Management-Application/
│
├── app/
│   ├── templates/
│   ├── static/
│   └── ...
│
├── instance/
├── requirements.txt
├── run.py
└── README.md
