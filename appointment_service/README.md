# Appointment Service - Salon Booking System

Appointment booking and management microservice for the Salon Booking System.

## Features

✅ **Appointment Booking** - Create new appointments  
✅ **View Appointments** - Get appointments by user, staff, date  
✅ **Update/Reschedule** - Modify appointment details  
✅ **Cancel Appointments** - Cancel bookings  
✅ **Status Management** - Track appointment status (pending/confirmed/completed/cancelled/no-show)  
✅ **User Permissions** - Users can manage their own appointments  
✅ **Admin Access** - Full appointment management  
✅ **Authentication via User Service** - Validates JWT tokens  
✅ **MySQL with AWS RDS** - Production-ready database  

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Database**: MySQL (AWS RDS) - `salon-db`
- **Authentication**: JWT (from User Service)
- **Server**: Uvicorn

## Project Structure

```
appointment_service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # MySQL connection pooling
│   ├── auth.py           # JWT validation
│   ├── dependencies.py    # FastAPI dependencies
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   └── routes.py         # API endpoints
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Setup Instructions

### Step 1: Configure Environment

Your `.env` file should have:

```env
SERVICE_NAME=appointment_service
SERVICE_PORT=8004
HOST=0.0.0.0

# Copy JWT_SECRET_KEY from User Service
JWT_SECRET_KEY=your_jwt_secret_key_from_user_service
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Your AWS RDS credentials
DB_HOST=database-1.cn8e0eyq896c.eu-north-1.rds.amazonaws.com
DB_PORT=3306
DB_NAME=salon-db
DB_USER=admin
DB_PASSWORD=4343435

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
```

**CRITICAL**: The `JWT_SECRET_KEY` MUST match your User Service!

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Service

```bash
python main.py
```

The service will be available at:
- **API**: http://localhost:8004
- **Swagger Docs**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

**Note**: No database initialization needed - the `appointments` table already exists in your `salon-db`!

## Database Schema

### Appointments Table
```sql
CREATE TABLE appointments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,                    -- FK to users.id
  staff_id INT NOT NULL,                   -- FK to staff.id
  service_id INT NOT NULL,                 -- FK to services.id
  appointment_date DATE NOT NULL,          -- Date of appointment
  appointment_time TIME NOT NULL,          -- Time of appointment
  status VARCHAR(20) DEFAULT 'pending',    -- Status
  total_price DECIMAL(10, 2) NOT NULL,     -- Total price
  notes TEXT,                              -- Special notes
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (staff_id) REFERENCES staff(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);
```

**Status Values**: `pending`, `confirmed`, `completed`, `cancelled`, `no-show`

## API Endpoints

### User Endpoints (Requires user token)
```
POST   /api/v1/appointments                       - Create appointment (own only)
GET    /api/v1/appointments/{id}                  - Get appointment details (own only)
GET    /api/v1/users/{user_id}/appointments       - Get user's appointments (own only)
PUT    /api/v1/appointments/{id}                  - Update appointment (own only)
DELETE /api/v1/appointments/{id}                  - Cancel appointment (own only)
GET    /api/v1/staff/{staff_id}/appointments      - Get staff appointments
GET    /api/v1/appointments/date/{date}           - Get appointments by date
```

### Admin Endpoints (Requires admin token)
```
GET    /api/v1/appointments                       - List all appointments (paginated)
POST   /api/v1/appointments                       - Create appointment for any user
PUT    /api/v1/appointments/{id}                  - Update any appointment (including status)
DELETE /api/v1/appointments/{id}                  - Cancel any appointment
```

### Public Endpoints
```
GET    /                  - Service information
GET    /api/v1/health    - Health check
```

## Testing the Endpoints

### 1. Health Check (No auth required)
```bash
curl http://localhost:8004/api/v1/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "appointment_service",
  "database": "connected"
}
```

### 2. Get Access Token (from User Service)
```bash
# Regular user
curl -X POST "http://localhost:8001/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "John123"
  }'

# Admin
curl -X POST "http://localhost:8001/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123"
  }'
```

Save the `access_token`.

### 3. Create an Appointment (Authenticated user)

**Prerequisites**: You need:
- Valid `user_id` (from users table)
- Valid `staff_id` (from staff table - use internal ID, not user_id)
- Valid `service_id` (from services table)

```bash
curl -X POST "http://localhost:8004/api/v1/appointments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "staff_id": 1,
    "service_id": 1,
    "appointment_date": "2025-11-25",
    "appointment_time": "10:00:00",
    "notes": "Please use organic products"
  }'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "appointment": {
      "id": 1,
      "user_id": 2,
      "staff_id": 1,
      "service_id": 1,
      "appointment_date": "2025-11-25",
      "appointment_time": "10:00:00",
      "status": "pending",
      "total_price": 35.00,
      "notes": "Please use organic products",
      "created_at": "2025-11-18T15:00:00",
      "updated_at": "2025-11-18T15:00:00"
    }
  },
  "message": "Appointment created successfully"
}
```

### 4. Get My Appointments (User)
```bash
curl -X GET "http://localhost:8004/api/v1/users/2/appointments" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Get Appointment Details
```bash
curl -X GET "http://localhost:8004/api/v1/appointments/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "id": 1,
  "user_id": 2,
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "user_phone": "+1234567890",
  "staff_id": 1,
  "staff_name": "Jane Smith",
  "staff_position": "Senior Hair Stylist",
  "service_id": 1,
  "service_name": "Men Haircut",
  "service_duration": 30,
  "appointment_date": "2025-11-25",
  "appointment_time": "10:00:00",
  "status": "pending",
  "total_price": 35.00,
  "notes": "Please use organic products",
  "created_at": "2025-11-18T15:00:00",
  "updated_at": "2025-11-18T15:00:00"
}
```

### 6. Get Staff's Appointments
```bash
# All appointments for staff member 1
curl -X GET "http://localhost:8004/api/v1/staff/1/appointments" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Appointments for staff on specific date
curl -X GET "http://localhost:8004/api/v1/staff/1/appointments?appointment_date=2025-11-25" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get Appointments by Date
```bash
curl -X GET "http://localhost:8004/api/v1/appointments/date/2025-11-25" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Update/Reschedule Appointment (User - own only)
```bash
curl -X PUT "http://localhost:8004/api/v1/appointments/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_date": "2025-11-26",
    "appointment_time": "14:00:00",
    "notes": "Changed to afternoon slot"
  }'
```

### 9. Update Appointment Status (Admin only)
```bash
curl -X PUT "http://localhost:8004/api/v1/appointments/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }'
```

### 10. Cancel Appointment (User - own only)
```bash
curl -X DELETE "http://localhost:8004/api/v1/appointments/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 11. Get All Appointments (Admin only)
```bash
# Paginated list
curl -X GET "http://localhost:8004/api/v1/appointments?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Filter by status
curl -X GET "http://localhost:8004/api/v1/appointments?status_filter=pending" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# From specific date onwards
curl -X GET "http://localhost:8004/api/v1/appointments?from_date=2025-11-20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 12. Get User's Future Appointments
```bash
curl -X GET "http://localhost:8004/api/v1/users/2/appointments?from_date=2025-11-18&status_filter=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Testing with Swagger UI

1. Open: http://localhost:8004/docs
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
- `201 Created` - Appointment created
- `204 No Content` - Appointment cancelled
- `400 Bad Request` - Invalid request (validation failed)
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Appointment not found
- `500 Internal Server Error` - Server error

## Permission Rules

### Regular Users Can:
- ✅ Create appointments for themselves only
- ✅ View their own appointments
- ✅ Update their own appointments (except status)
- ✅ Cancel their own appointments
- ✅ View staff appointments
- ✅ View appointments by date

### Regular Users Cannot:
- ❌ Create appointments for other users
- ❌ View other users' appointments
- ❌ Update other users' appointments
- ❌ Change appointment status
- ❌ View all appointments list

### Admins Can:
- ✅ Everything users can do, PLUS:
- ✅ Create appointments for any user
- ✅ View all appointments
- ✅ Update any appointment
- ✅ Change appointment status
- ✅ Cancel any appointment

## Appointment Workflow

```
1. User selects service → Gets duration & price
2. User selects staff → Checks availability
3. User books appointment → Status: "pending"
4. Admin confirms → Status: "confirmed"
5. Service completed → Status: "completed"

Alternative paths:
- User cancels → Status: "cancelled"
- User doesn't show → Status: "no-show"
```

## Validation Rules

### Appointment Date
- Cannot be in the past
- Must be valid date format (YYYY-MM-DD)

### Appointment Time
- Must be valid time format (HH:MM:SS)
- System checks for staff conflicts automatically

### Status Values
- `pending` - Initial state when booked
- `confirmed` - Admin confirmed
- `completed` - Service finished
- `cancelled` - Cancelled by user or admin
- `no-show` - User didn't show up

### Notes
- Optional
- Max 500 characters

## Error Scenarios

### "Staff member is not available at this time"
**Cause**: Another appointment exists for the same staff at the same time.  
**Solution**: Choose a different time or staff member.

### "User not found or inactive"
**Cause**: Invalid user_id or user is deactivated.  
**Solution**: Verify user_id exists and is active.

### "Staff member not found or inactive"
**Cause**: Invalid staff_id or staff is deactivated.  
**Solution**: Verify staff_id exists and is active.

### "Service not found or inactive"
**Cause**: Invalid service_id or service is deactivated.  
**Solution**: Verify service_id exists and is active.

### "You can only create appointments for yourself"
**Cause**: Non-admin trying to book for another user.  
**Solution**: Login with admin account or book for yourself.

### "You can only view your own appointments"
**Cause**: Non-admin trying to view another user's appointments.  
**Solution**: Login with admin account or view only your own.

## Integration with Other Services

### User Service Integration
- Validates JWT tokens
- Checks user permissions
- Verifies user exists and is active

### Staff Service Integration
- Validates staff_id exists
- Checks staff is active
- Links to staff details

### Service Management Integration
- Validates service_id exists
- Gets service price (auto-calculated)
- Gets service duration

## Architecture

### Authentication Flow
```
1. User logs into User Service → Gets access_token
2. User calls Appointment Service with access_token
3. Appointment Service:
   - Decodes JWT token
   - Queries users table to verify user exists
   - Checks user permissions
   - Processes request if authorized
```

### Permission Check
```
Non-Admin User:
- Can create appointment where user_id = their own ID
- Can view appointment where user_id = their own ID
- Can update appointment where user_id = their own ID
- Cannot change status field

Admin User:
- Can do everything
- No restrictions
```

## Development

### Running with Auto-reload
```bash
uvicorn main:app --reload --port 8004
```

### Viewing Logs
Logs are output to stdout with timestamps:
```
2025-11-18 15:00:00 - app.database - INFO - Database connection established
2025-11-18 15:00:05 - app.routes - INFO - Appointment created: ID 1
```

## Troubleshooting

### Issue: Foreign Key Constraint Failed
**Error**: `Cannot add or update a child row: a foreign key constraint fails`

**Cause**: user_id, staff_id, or service_id doesn't exist in respective tables.

**Solution**:
1. Verify user exists: `SELECT * FROM users WHERE id = ?`
2. Verify staff exists: `SELECT * FROM staff WHERE id = ?`
3. Verify service exists: `SELECT * FROM services WHERE id = ?`

### Issue: Authentication Failed
**Error**: `401 Unauthorized`

**Solutions**:
1. Verify JWT_SECRET_KEY matches User Service
2. Get fresh token (tokens expire in 15 min)
3. Check User Service is running

### Issue: Cannot View Appointment
**Error**: `403 Forbidden - You can only view your own appointments`

**Solution**:
- If user: Can only view appointments where user_id matches your ID
- If need to view all: Login with admin account

## Production Deployment

### Recommendations
1. **Environment**: Use Gunicorn + Uvicorn workers
2. **Security**: HTTPS, secure JWT_SECRET_KEY, proper CORS
3. **Database**: Connection pooling, read replicas
4. **Monitoring**: Logging, metrics, alerting

### Sample Production Run
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8004
```

## License

Copyright © 2025 Salon Booking System

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Port**: 8004  
**Dependencies**: User Service (8001), Staff Service (8003), Service Management (8002), AWS RDS MySQL (`salon-db`)