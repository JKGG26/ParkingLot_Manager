# Parking Management System

## Overview

The Parking Management System is a comprehensive solution for managing parking lots and vehicle entries, utilizing a Django-based REST API and a Flask microservice for email handling. The system supports JWT authentication, role-based access, and provides various indicators and statistics for better parking management.

## Features

- **User Roles**:
  - **Admin**:
    - Manage Socio users (CRUD operations).
    - Manage parking lots (CRUD operations).
    - Send emails to Socio users.
    - View detailed indicators and statistics.
  - **Socio**:
    - Register vehicle entries and exits.
    - View details of associated parking lots and vehicles.
    - Access indicators for associated parking lots.

- **API Endpoints**:
  - **User Management**:
    - `api/register-socio/`: Register a new Socio user.
    - `api/login/`: Obtain a JWT token.
    - `api/logout/`: Logout and invalidate the JWT token.
  
  - **Parking Lots**:
    - `api/create-parking-lot/`: Create a new parking lot.
    - `api/parking-lots/`: List all parking lots.
    - `api/parking-lots/<int:id>`: Get details of a specific parking lot.
    - `api/delete-parking-lot/<int:id>`: Delete a specific parking lot.
    - `api/edit-parking-lot/<int:id>`: Edit a specific parking lot.

  - **User-Parking Relations**:
    - `api/set-socio-parking/`: Associate a Socio with a parking lot.
    - `api/delete-socio-parking/<int:id>`: Remove a Socio from a parking lot.
  
  - **Vehicle Management**:
    - `api/register-vehicle-entry/`: Register a vehicle entry into a parking lot.
    - `api/register-vehicle-exit/`: Register a vehicle exit from a parking lot.
    - `api/vehicles-entries/`: List all vehicle entries.
    - `api/vehicles-entries/<int:id>`: Get vehicle entries for a specific parking lot.

  - **Indicators and Statistics**:
    - `api/top-<int:top>-vehicles-entries/`: Get top vehicles by entries.
    - `api/top-<int:top>-vehicles-entries/<int:id>`: Get top vehicles by entries for a specific parking lot.
    - `api/first-time-vehicles/<int:id>`: Get first-time vehicles for a specific parking lot.
    - `api/incomes-last-<int:days>-days-parking-lot/<int:id>`: Get income data for the last X days for a specific parking lot.
    - `api/incomes-parking-lot/<int:id>`: Get summary income data for a specific parking lot.
    - `api/top-<int:top>-socios-vehicles-entries/last-<int:days>-days/`: Get top Socios by vehicle entries for the last X days.
    - `api/top-socios-vehicles-entries/`: Get top Socios by vehicle entries for the week.
    - `api/top-<int:top>-parking-lots-incomes/`: Get top parking lots by income.

  - **Email Service**:
    - `api/send-mail/`: Send an email to users.

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL
- Virtual environment (recommended)

### Steps

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/JKGG26/ParkingLot_Manager.git
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv env
    source env\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**:

    Create a .env file in the root directory with the following content:

    ```bash
    SECRET_KEY=<your-secret-key>
    DJANGO_SETTINGS_MODULE=RESTAPI.settings
    ADMIN_USER=<admin-username>
    ADMIN_PWD=<admin-password>
    ```

5. **Set Up the Database**:

    Ensure PostgreSQL is installed and running.

    Create a PostgreSQL database and user, and update the database settings in RESTAPI/settings.py.

6. **Set Up the environment variables**:

    Set up environtment variables for database connection and admin credentials:

    - `DB_NAME`="your_db_name"
    - `DB_USER`="your_db_user"
    - `DB_PWD`="your_db_password"
    - `DB_HOST`="your_db_host"
    - `DB_PORT`="your_db_port"
    - `ADMIN_USER`="your_admin_usermail"
    - `ADMIN_PWD`="your_admin_password"

    For example, for local tests with temporal environment variables, you can set them in PowerShell as:

    ```bash
    $env:DB_NAME="my_db_name"
    $env:DB_USER="my_db_user"
    $env:DB_PWD="my_db_password"
    $env:DB_HOST="localhost"
    $env:DB_PORT="5432"
    $env:ADMIN_USER="admin@mail.com"
    $env:ADMIN_PWD="admin"
    ```

7. **Apply Django Migrations**:

    ```bash
    cd RESTAPI
    python manage.py makemigrations
    python manage.py migrate
    ```

8. **Run the Django Server**:
    ```bash
    python manage.py runserver
    ```

9. **Run the Flask Microservice to send Emails**:

    In other terminal out of RESTAPI directory, activate the python 'env' and run the microservices/send_mail.py file with python:

    ```bash
    env\Scripts\activate
    cd microservices
    python send_mail.py
    ```
