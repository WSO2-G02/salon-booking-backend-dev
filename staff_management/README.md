# Staff Service - Salon Booking System

Staff management and availability microservice for the Salon Booking System.

## Features

✅ **Staff Management** - Create, update, and manage staff profiles  
✅ **Availability Management** - Define staff working hours and availability  
✅ **Time Slot Calculation** - Calculate available booking slots  
✅ **Specialty Search** - Find staff by specialty  
✅ **Authentication via User Service** - Validates JWT tokens from User Service  
✅ **Role-Based Access** - Admin-only endpoints for management  
✅ **Multi-Database Support** - staff_db + user_db for authentication  
✅ **MySQL with AWS RDS** - Production-ready database setup  

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Database**: MySQL (AWS RDS)
- **Authentication**: JWT (from User Service)
- **Server**: Uvicorn

## Project Structure

```
staff_service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Multi-database connection pooling
│   ├── auth.py           # JWT validation
│   ├── dependencies.py    # FastAPI dependencies
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   └── routes.py         # API endpoints
├── main.py               # Application entry point
├── init_database.py      # Database initialization
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

## Prerequisites

1. ✅ **User Service** running and configured
2. ✅ **AWS RDS MySQL** instance with two databases:
   - `user_db` (from User Service)
   - `staff_db` (for this service)
3. ✅ **JWT Secret Key** from User Service

## Setup Instructions

### Step 1: Configure Environment

Copy the JWT_SECRET_KEY from your **User Service** `.env` file:

```bash
cd staff_service
nano .env
```

Fill in the configuration:

```env
# SERVICE
SERVICE_NAME=staff_service
SERVICE_PORT=8003
HOST=0.0.0.0

# JWT (MUST MATCH USER SERVICE!)
JWT_SECRET_KEY=your_jwt_secret_key_from_user_service
JWT_ALGORITHM=HS256

# AWS RDS (Same instance as User Service)
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=3306
DB_NAME=staff_db
DB_USER=admin
DB_PASSWORD=your_password

# USER DATABASE
USER_DB_NAME=user_db

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# LOGGING
LOG_LEVEL=INFO
```

**CRITICAL**: The `JWT_SECRET_KEY` MUST be exactly the same as your User Service!

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python init_database.py
```

Expected output:
```
======================================================================
Staff Service - Database Initialization
======================================================================

Connecting to MySQL server at your-endpoint.rds.amazonaws.com...
✅ Connected to MySQL server
✅ Database 'staff_db' is ready

Creating tables...
Creating table 'staff'... ✅
Creating table 'staff_availability'... ✅

Creating indexes...
✅ Indexes created

======================================================================
✅ Database initialization completed successfully!
======================================================================
```

### Step 4: Run the Service

```bash
python main.py
```

The service will be available at:
- **API**: http://localhost:8003
- **Swagger Docs**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## Database Schema

### Staff Table
```sql
CREATE TABLE staff (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT UNIQUE NOT NULL,          -- Links to user_db.users.id
  employee_id VARCHAR(50) UNIQUE,       -- Unique employee code
  position VARCHAR(100),                -- Job position
  specialties VARCHAR(1000),            -- Comma-separated specialties
  experience_years INT,                 -- Years of experience
  hire_date DATE,                       -- Date of hire
  is_active TINYINT(1) DEFAULT 1,       -- Active status
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Staff Availability Table
```sql
CREATE TABLE staff_availability (
  id INT PRIMARY KEY AUTO_INCREMENT,
  staff_id INT NOT NULL,                -- FK to staff.id
  slot_date DATE NOT NULL,              -- Date of availability
  start_time TIME NOT NULL,             -- Start time
  end_time TIME NOT NULL,               -- End time
  availability_type VARCHAR(20) DEFAULT 'work', -- work/break/unavailable
  FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE
);
```

## API Endpoints

### Authentication
All endpoints require a valid JWT access token from User Service in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Staff Management Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/staff` | Create new staff member | Admin |
| GET | `/api/v1/staff` | List all staff (paginated) | Authenticated |
| GET | `/api/v1/staff/{staff_id}` | Get staff details | Authenticated |
| PUT | `/api/v1/staff/{staff_id}` | Update staff member | Admin |
| DELETE | `/api/v1/staff/{staff_id}` | Deactivate staff member | Admin |

### Availability Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/staff/{staff_id}/availability` | Create availability slot | Admin |
| GET | `/api/v1/staff/{staff_id}/availability` | Get available time slots | Authenticated |

### Search Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/staff/specialty/{specialty}` | Find staff by specialty | Authenticated |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/api/v1/health` | Health check |

## Testing the Endpoints

### 1. Get Access Token from User Service

First, login to User Service to get an access token:

```bash
curl -X POST "http://localhost:8001/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123"
  }'
```

Copy the `access_token` from the response.

### 2. Create a Staff Member (Admin Only)

```bash
curl -X POST "http://localhost:8003/api/v1/staff" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "employee_id": "EMP001",
    "position": "Senior Hair Stylist",
    "specialties": "hair cutting, hair coloring, styling",
    "experience_years": 5,
    "hire_date": "2020-01-15"
  }'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "staff": {
      "id": 1,
      "user_id": 1,
      "employee_id": "EMP001",
      "position": "Senior Hair Stylist",
      "specialties": "hair cutting, hair coloring, styling",
      "experience_years": 5,
      "hire_date": "2020-01-15",
      "is_active": true,
      "created_at": "2025-11-18T10:30:00",
      "updated_at": "2025-11-18T10:30:00"
    }
  },
  "message": "Staff member created successfully"
}
```

### 3. Get All Staff Members

```bash
curl -X GET "http://localhost:8003/api/v1/staff?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Get Specific Staff Member

```bash
curl -X GET "http://localhost:8003/api/v1/staff/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Update Staff Member (Admin Only)

```bash
curl -X PUT "http://localhost:8003/api/v1/staff/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Lead Hair Stylist",
    "experience_years": 6
  }'
```

### 6. Create Availability Slot (Admin Only)

```bash
curl -X POST "http://localhost:8003/api/v1/staff/1/availability" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "staff_id": 1,
    "slot_date": "2025-11-20",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "availability_type": "work"
  }'
```

Expected response:
```json
{
  "id": 1,
  "staff_id": 1,
  "slot_date": "2025-11-20",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "availability_type": "work"
}
```

### 7. Get Available Time Slots

```bash
curl -X GET "http://localhost:8003/api/v1/staff/1/availability?slot_date=2025-11-20&service_duration=60" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Expected response:
```json
{
  "staff_id": 1,
  "slot_date": "2025-11-20",
  "available_slots": [
    {
      "start_time": "09:00:00",
      "end_time": "10:00:00",
      "duration_minutes": 60
    },
    {
      "start_time": "09:30:00",
      "end_time": "10:30:00",
      "duration_minutes": 60
    },
    ...
  ],
  "total_available_minutes": 480
}
```

### 8. Search Staff by Specialty

```bash
curl -X GET "http://localhost:8003/api/v1/staff/specialty/hair%20cutting" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 9. Deactivate Staff Member (Admin Only)

```bash
curl -X DELETE "http://localhost:8003/api/v1/staff/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 10. Health Check

```bash
curl -X GET "http://localhost:8003/api/v1/health"
```

Expected response:
```json
{
  "status": "healthy",
  "service": "staff_service",
  "databases": {
    "staff_db": true,
    "user_db": true
  }
}
```

## Testing with Swagger UI

1. Open: http://localhost:8003/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click "Authorize"
5. Test any endpoint directly from the UI

## Response Formats

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "ERROR_IDENTIFIER",
  "message": "Human readable error message",
  "details": { ... }
}
```

## Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success with no content
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions (not admin)
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (duplicate)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Authentication Flow

```
┌─────────┐           ┌──────────────┐           ┌───────────────┐
│ Client  │           │ User Service │           │ Staff Service │
└────┬────┘           └──────┬───────┘           └───────┬───────┘
     │                       │                           │
     │  1. Login             │                           │
     ├──────────────────────>│                           │
     │                       │                           │
     │  2. Access Token      │                           │
     │<──────────────────────┤                           │
     │                       │                           │
     │  3. API Request       │                           │
     │  + Access Token       │                           │
     ├───────────────────────┼──────────────────────────>│
     │                       │                           │
     │                       │  4. Validate Token        │
     │                       │  (checks user_db)         │
     │                       │<──────────────────────────┤
     │                       │                           │
     │  5. Response          │                           │
     │<──────────────────────┼───────────────────────────┤
```

## Architecture

### Microservices Communication
- **Staff Service** validates JWT tokens by:
  1. Decoding JWT token with shared secret key
  2. Querying `user_db.users` table to verify user exists
  3. Checking user is active and has correct permissions

### Database Strategy
- **staff_db**: Staff and availability data
- **user_db**: User authentication validation
- Both databases on same AWS RDS instance
- Connection pooling for efficiency

## Troubleshooting

### Issue: Authentication Failed

**Error**: `401 Unauthorized - Could not validate credentials`

**Solutions**:
1. Verify JWT_SECRET_KEY matches User Service exactly
2. Check access token hasn't expired (15 min expiry)
3. Ensure User Service is running
4. Verify user_db is accessible

### Issue: Database Connection Failed

**Error**: `Database access denied` or `Database does not exist`

**Solutions**:
1. Check DB credentials in `.env`
2. Verify staff_db exists (run init_database.py)
3. Ensure security group allows port 3306
4. Check RDS instance is running

### Issue: Staff Member Not Found

**Error**: `404 Not Found - Staff member not found`

**Solutions**:
1. Verify staff_id is correct
2. Check if staff member is active
3. Ensure staff exists in database

### Issue: Admin Permission Required

**Error**: `403 Forbidden - Admin privileges required`

**Solutions**:
1. Login with admin account (not regular user)
2. Verify user_type='admin' in user_db.users
3. Check token hasn't expired

## Development

### Running with Auto-reload

```bash
uvicorn main:app --reload --port 8003
```

### Viewing Logs

Logs are output to stdout with timestamps:
```
2025-11-18 10:30:00 - app.database - INFO - Staff database connection established
2025-11-18 10:30:01 - app.routes - INFO - Staff member created: EMP001
```

## Production Deployment

### Recommendations

1. **Environment**: Use Gunicorn + Uvicorn workers
2. **Security**:
   - Use HTTPS
   - Secure JWT_SECRET_KEY
   - Configure proper CORS origins
   - Enable rate limiting
3. **Database**: Use read replicas for scale
4. **Monitoring**: Implement logging, metrics, and alerting

### Sample Production Run

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8003 \
  --access-logfile - \
  --error-logfile -
```

## Integration with Other Services

### User Service Integration
- Validates JWT tokens
- Checks user permissions
- Verifies user exists and is active

### Appointment Service Integration (Future)
- Appointment Service will call Staff Service to:
  - Get available staff
  - Check staff availability
  - Validate staff_id exists

## API Documentation

Full interactive API documentation available at:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## License

Copyright © 2025 Salon Booking System

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Port**: 8003