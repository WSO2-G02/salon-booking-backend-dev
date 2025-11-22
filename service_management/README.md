# Service Management - Salon Booking System

Salon service management microservice for managing offered services (haircut, coloring, styling, etc.).

## Features

✅ **Service CRUD** - Create, read, update, delete salon services  
✅ **Category Management** - Organize services by category  
✅ **Price Management** - Set and update service prices  
✅ **Duration Tracking** - Track service duration in minutes  
✅ **Active/Inactive Status** - Soft delete services  
✅ **Search & Filter** - By category, price range  
✅ **Authentication via User Service** - Validates JWT tokens  
✅ **Role-Based Access** - Admin for write, users for read  
✅ **MySQL with AWS RDS** - Production-ready database  

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Database**: MySQL (AWS RDS) - `salon-db`
- **Authentication**: JWT (from User Service)
- **Server**: Uvicorn

## Project Structure

```
service_management/
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
SERVICE_NAME=service_management
SERVICE_PORT=8002
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
- **API**: http://localhost:8002
- **Swagger Docs**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

**Note**: No database initialization needed - the `services` table already exists in your `salon-db`!

## Database Schema

### Services Table
```sql
CREATE TABLE services (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,           -- Service name (unique)
  description TEXT,                     -- Service description
  category VARCHAR(50),                 -- Category (e.g., "Hair", "Nails")
  price DECIMAL(10, 2) NOT NULL,        -- Service price
  duration_minutes INT NOT NULL,        -- Duration in minutes
  is_active TINYINT(1) DEFAULT 1,       -- Active status
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## API Endpoints

### Admin Endpoints (Requires admin token)
```
POST   /api/v1/services                 - Create new service
PUT    /api/v1/services/{id}           - Update service
DELETE /api/v1/services/{id}           - Deactivate service
```

### User Endpoints (Requires any valid token)
```
GET    /api/v1/services                    - List all services
GET    /api/v1/services/{id}               - Get service details
GET    /api/v1/services/category/{category} - Get services by category
GET    /api/v1/services/price-range        - Get services by price range
GET    /api/v1/categories                  - Get all categories
```

### Public Endpoints
```
GET    /                  - Service information
GET    /api/v1/health    - Health check
```

## Testing the Endpoints

### 1. Health Check (No auth required)
```bash
curl http://localhost:8002/api/v1/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "service_management",
  "database": "connected"
}
```

### 2. Get Admin Token (from User Service)
```bash
curl -X POST "http://localhost:8001/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin123"
  }'
```

Save the `access_token`.

### 3. Create a Service (Admin only)
```bash
curl -X POST "http://localhost:8002/api/v1/services" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Men Haircut",
    "description": "Professional mens haircut with styling",
    "category": "Hair",
    "price": 35.00,
    "duration_minutes": 30
  }'
```

Expected response:
```json
{
  "status": "success",
  "data": {
    "service": {
      "id": 1,
      "name": "Men Haircut",
      "description": "Professional mens haircut with styling",
      "category": "Hair",
      "price": 35.00,
      "duration_minutes": 30,
      "is_active": true,
      "created_at": "2025-11-18T10:00:00",
      "updated_at": "2025-11-18T10:00:00"
    }
  },
  "message": "Service created successfully"
}
```

### 4. Create More Services
```bash
# Hair Coloring
curl -X POST "http://localhost:8002/api/v1/services" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hair Coloring",
    "description": "Full hair coloring service",
    "category": "Hair",
    "price": 85.00,
    "duration_minutes": 120
  }'

# Manicure
curl -X POST "http://localhost:8002/api/v1/services" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manicure",
    "description": "Professional nail care and polish",
    "category": "Nails",
    "price": 25.00,
    "duration_minutes": 45
  }'

# Facial Treatment
curl -X POST "http://localhost:8002/api/v1/services" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Facial Treatment",
    "description": "Deep cleansing facial",
    "category": "Skincare",
    "price": 65.00,
    "duration_minutes": 60
  }'
```

### 5. Get All Services (Any authenticated user)
```bash
curl -X GET "http://localhost:8002/api/v1/services" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get Services by Category
```bash
curl -X GET "http://localhost:8002/api/v1/services/category/Hair" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Get All Categories
```bash
curl -X GET "http://localhost:8002/api/v1/categories" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
[
  "Hair",
  "Nails",
  "Skincare"
]
```

### 8. Get Services by Price Range
```bash
# Services between $20 and $50
curl -X GET "http://localhost:8002/api/v1/services/price-range?min_price=20&max_price=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 9. Get Specific Service
```bash
curl -X GET "http://localhost:8002/api/v1/services/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 10. Update Service (Admin only)
```bash
curl -X PUT "http://localhost:8002/api/v1/services/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 40.00,
    "duration_minutes": 35
  }'
```

### 11. Filter Active Services Only
```bash
curl -X GET "http://localhost:8002/api/v1/services?active_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 12. Deactivate Service (Admin only)
```bash
curl -X DELETE "http://localhost:8002/api/v1/services/1" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Testing with Swagger UI

1. Open: http://localhost:8002/docs
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
- `409 Conflict` - Resource conflict (duplicate name)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Validation Rules

### Service Name
- Required
- Unique
- 1-100 characters
- Cannot be empty

### Price
- Required
- Must be greater than zero
- Decimal with 2 decimal places
- Example: `25.00`, `35.50`

### Duration
- Required
- Must be greater than zero
- Maximum 1440 minutes (24 hours)
- Integer only

### Category
- Optional
- Max 50 characters

### Description
- Optional
- Text field

## Example Service Categories

Common categories for salon services:
- **Hair**: Haircut, Coloring, Styling, Treatment
- **Nails**: Manicure, Pedicure, Gel Nails, Nail Art
- **Skincare**: Facial, Peeling, Mask, Treatment
- **Makeup**: Full Makeup, Event Makeup, Bridal Makeup
- **Massage**: Swedish, Deep Tissue, Aromatherapy
- **Waxing**: Full Body, Partial, Threading

## Architecture

### Authentication Flow
```
1. User logs into User Service → Gets access_token
2. User calls Service Management with access_token
3. Service Management:
   - Decodes JWT token (using shared secret)
   - Queries users table to verify user exists
   - Checks user permissions (admin/user)
   - Processes request if authorized
```

### Permission Levels
- **Admin**: Full access (create, update, delete services)
- **Authenticated User**: Read-only access (view services)
- **Public**: No access (all endpoints require authentication)

## Troubleshooting

### Issue: Authentication Failed
**Error**: `401 Unauthorized`

**Solutions**:
1. Verify JWT_SECRET_KEY matches User Service
2. Check token hasn't expired (15 min expiry)
3. Ensure User Service is running
4. Get fresh token from User Service

### Issue: Service Name Already Exists
**Error**: `409 Conflict - Service with name 'X' already exists`

**Solutions**:
1. Use a different service name
2. Update the existing service instead
3. Check if service was soft-deleted (is_active=0)

### Issue: Admin Permission Required
**Error**: `403 Forbidden - Admin privileges required`

**Solutions**:
1. Login with admin account
2. Verify user_type='admin' in users table
3. Check token is valid

## Integration with Other Services

### User Service Integration
- Validates JWT tokens
- Checks user permissions
- Verifies user exists and is active

### Appointment Service Integration (Future)
- Appointment Service will call Service Management to:
  - Get available services
  - Validate service_id exists
  - Get service price and duration
  - Check if service is active

## Development

### Running with Auto-reload
```bash
uvicorn main:app --reload --port 8002
```

### Viewing Logs
Logs are output to stdout with timestamps:
```
2025-11-18 10:00:00 - app.database - INFO - Database connection established
2025-11-18 10:00:05 - app.routes - INFO - Service created: Men Haircut
```

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
  --bind 0.0.0.0:8002
```

## License

Copyright © 2025 Salon Booking System

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Port**: 8002  
**Dependencies**: User Service (8001), AWS RDS MySQL (`salon-db`)