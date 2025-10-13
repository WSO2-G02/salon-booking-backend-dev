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