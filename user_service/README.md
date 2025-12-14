# User Service - Salon Booking System

User management and authentication microservice for the Salon Booking System.

## Features

- ✅ User registration and authentication
- ✅ JWT-based access and refresh tokens
- ✅ Role-based access control (User/Admin)
- ✅ Secure password hashing with bcrypt
- ✅ User profile management
- ✅ Admin user management
- ✅ MySQL database with connection pooling
- ✅ RESTful API with FastAPI
- ✅ Comprehensive error handling
- ✅ API documentation (Swagger/ReDoc)

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Database**: MySQL (AWS RDS compatible)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Server**: Uvicorn

## Project Structure

```
user_service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # Database connection & pooling
│   ├── auth.py           # JWT & password utilities
│   ├── dependencies.py    # FastAPI dependencies
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   └── routes.py         # API endpoints
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Setup Instructions

### 1. Generate JWT Secret Key

First, generate a secure secret key for JWT token encryption:

```bash
cd user_service
python ../generate_secret_key.py
```

Save the generated key - you'll need it for the `.env` file.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Service Configuration
SERVICE_NAME=user_service
SERVICE_PORT=8001
HOST=0.0.0.0

# JWT Configuration
JWT_SECRET_KEY=your_generated_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration (AWS RDS MySQL)
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306
DB_NAME=user_db
DB_USER=your_db_username
DB_PASSWORD=your_db_password

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Logging
LOG_LEVEL=INFO
```

### 4. Create Database Tables

The service expects the following tables to exist. Run these SQL scripts on your MySQL database:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(100) NULL,
  `phone` VARCHAR(20) NULL,
  `user_type` VARCHAR(10) NOT NULL DEFAULT 'user',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CHECK (`user_type` IN ('admin', 'user'))
) ENGINE=InnoDB;

-- Sessions table
CREATE TABLE IF NOT EXISTS `sessions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `refresh_token` VARCHAR(500) NOT NULL,
  `expires_at` DATETIME NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;
```

### 5. Run the Service

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The service will be available at:
- **API**: http://localhost:8001
- **Swagger Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/register` | Register new customer |
| POST | `/api/v1/login` | Login and get tokens |
| POST | `/api/v1/refresh` | Refresh access token |
| POST | `/api/v1/logout` | Logout (invalidate refresh token) |

### Authenticated User Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/api/v1/profile` | Get user profile | User |
| PUT | `/api/v1/profile` | Update user profile | User |
| PUT | `/api/v1/profile/password` | Change password | User |

### Admin Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/users` | Create new user | Admin |
| GET | `/api/v1/users` | List all users (paginated) | Admin |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/api/v1/health` | Health check |

## API Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://localhost:8001/api/v1/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe",
    "phone": "+1234567890"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8001/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 3. Get Profile (Authenticated)

```bash
curl -X GET "http://localhost:8001/api/v1/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Refresh Token

```bash
curl -X POST "http://localhost:8001/api/v1/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 5. Create User (Admin)

```bash
curl -X POST "http://localhost:8001/api/v1/users" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@salon.com",
    "password": "AdminPass123",
    "user_type": "admin",
    "full_name": "Admin User"
  }'
```

## Authentication Flow

1. **Login**: User submits credentials → Receives access_token (15 min) and refresh_token (7 days)
2. **API Request**: Include access_token in `Authorization: Bearer <token>` header
3. **Token Expiry**: When access_token expires (401 response), use refresh_token to get new access_token
4. **Logout**: Submit refresh_token to invalidate session

## Error Response Format

All errors follow this format:

```json
{
  "status": "error",
  "error_code": "ERROR_IDENTIFIER",
  "message": "Human-readable error message",
  "details": {
    "additional": "information"
  }
}
```

Common HTTP Status Codes:
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `409 Conflict` - Resource conflict (e.g., duplicate username)
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Security Features

- ✅ Password hashing with bcrypt (salt rounds: 12)
- ✅ JWT tokens with expiration
- ✅ Refresh token rotation
- ✅ Session management in database
- ✅ Role-based access control
- ✅ Input validation with Pydantic
- ✅ SQL injection protection (parameterized queries)
- ✅ CORS configuration

## Database Connection Pooling

The service uses MySQL connection pooling for efficient database operations:
- Pool size: 10 connections
- Automatic connection lifecycle management
- Transaction support with rollback on errors

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (to be implemented)
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Monitoring

### Health Check

Check service health:
```bash
curl http://localhost:8001/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "service": "user_service",
  "database": "connected"
}
```

### Logs

Logs are output to stdout in the format:
```
2025-01-15 10:30:45 - app.database - INFO - Database connection pool initialized successfully
```

## Troubleshooting

### Database Connection Issues

1. Verify MySQL server is running and accessible
2. Check DB credentials in `.env`
3. Ensure database `user_db` exists
4. Verify tables are created
5. Check firewall/security group rules (for AWS RDS)

### JWT Token Issues

1. Ensure JWT_SECRET_KEY is set and matches across service restarts
2. Check token expiration times in configuration
3. Verify token format in Authorization header: `Bearer <token>`

### Import Errors

If you get import errors, ensure you're running from the parent directory:
```bash
cd /path/to/user_service
python main.py
```

## Production Deployment

### Recommendations

1. **Environment**: Use production WSGI server (Gunicorn + Uvicorn workers)
2. **Security**: 
   - Use HTTPS
   - Set strong JWT_SECRET_KEY
   - Configure proper CORS origins
   - Enable rate limiting
3. **Database**: Use connection pooling, read replicas for scale
4. **Monitoring**: Implement logging, metrics, and alerting
5. **Secrets**: Use AWS Secrets Manager or similar for credentials

### Sample Production Run

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --access-logfile - \
  --error-logfile -
```

## License

Copyright © 2025 Salon Booking System

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review logs for error messages
3. Verify database connectivity
4. Check environment configuration

---

**Version**: 1.0.0  
**Last Updated**: November 2025# Trigger build
