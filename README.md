# Salon Booking System 

## Table of Contents
1. [Project Architecture Overview](#project-architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Common Components](#common-components)
4. [Service 1: User Service](#service-1-user-service)
5. [Service 2: Service Management Service](#service-2-service-management-service)
6. [Service 3: Staff Management Service](#service-3-staff-management-service)
7. [Service 4: Appointment/Scheduling Service](#service-4-appointmentscheduling-service)
8. [Service 5: Notification Service](#service-5-notification-service)
9. [Service 6: Reports & Analytics Service](#service-6-reports--analytics-service)
10. [Testing Strategy](#testing-strategy)
11. [Deployment & Docker Configuration](#deployment--docker-configuration)

## Project Architecture Overview

### Microservices Communication Pattern
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │ Service Mgmt    │    │ Staff Mgmt      │
│   Port: 8001    │    │ Port: 8002      │    │ Port: 8003      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │  Appointment    │    │ Notification    │    │ Reports &       │
         │  Service        │    │ Service         │    │ Analytics       │
         │  Port: 8004     │    │ (RabbitMQ)      │    │ Port: 8006      │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Queue**: RabbitMQ
- **Authentication**: JWT tokens
- **Password Security**: bcrypt
- **API Documentation**: Automatic with FastAPI/OpenAPI
- **Testing**: pytest
- **Containerization**: Docker

## Development Environment Setup

### Prerequisites Installation
```bash
# Create project directory
mkdir salon-booking-system
cd salon-booking-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install common dependencies
pip install fastapi[all] uvicorn sqlalchemy psycopg2-binary alembic
pip install pydantic-settings python-jose[cryptography] passlib[bcrypt]
pip install pika requests pytest pytest-asyncio httpx
```

### Project Structure
```
salon-booking-system/
├── common/                     # Shared utilities
│   ├── __init__.py
│   ├── database.py
│   ├── security.py
│   └── models.py
├── user-service/              # Port 8001
├── service-management/        # Port 8002
├── staff-management/         # Port 8003
├── appointment-service/      # Port 8004
├── notification-service/     # RabbitMQ Consumer
├── reports-analytics/        # Port 8006
├── docker-compose.yml
└── requirements.txt
```

### Environment Configuration (`.env` file)
```bash
# Database Configuration
POSTGRES_USER=salon_user
POSTGRES_PASSWORD=salon_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=salon_booking

# Security
SECRET_KEY=your-very-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_USER=salon_user
RABBITMQ_PASSWORD=salon_password

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=salon@example.com
SENDER_PASSWORD=your-app-password

# Service URLs (for inter-service communication)
USER_SERVICE_URL=http://localhost:8001
SERVICE_MANAGEMENT_URL=http://localhost:8002
STAFF_SERVICE_URL=http://localhost:8003
APPOINTMENT_SERVICE_URL=http://localhost:8004
REPORTS_SERVICE_URL=http://localhost:8006
```

## Development Workflow & Best Practices

### Getting Started Guide

1. **Clone and Setup**
```bash
# Clone repository
git clone <repository-url>
cd salon-booking-system

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Start PostgreSQL with Docker
docker run --name salon-postgres -e POSTGRES_PASSWORD=salon_password -e POSTGRES_USER=salon_user -e POSTGRES_DB=salon_booking -p 5432:5432 -d postgres:13

# Run database migrations for each service
cd user-service
alembic upgrade head

cd ../service-management
alembic upgrade head
# ... repeat for other services
```

3. **Start Services**
```bash
# Terminal 1: User Service
cd user-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Service Management
cd service-management
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3: Staff Management
cd staff-management
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 4: Appointment Service
cd appointment-service
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Terminal 5: Notification Service
cd notification-service
python app/main.py

# Terminal 6: Reports & Analytics
cd reports-analytics
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```