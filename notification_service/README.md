# Notification Service - Salon Booking System

Email notification microservice for sending transactional emails via Gmail SMTP.

## Features

✅ **User Registration Email** - Welcome email for new users  
✅ **Password Reset Email** - Secure password reset links  
✅ **Staff Welcome Email** - Onboarding email for new staff  
✅ **Appointment Confirmation** - Booking confirmation emails  
✅ **Appointment Update** - Rescheduling notification emails  
✅ **Appointment Cancellation** - Cancellation notification emails  
✅ **Professional HTML Templates** - Beautiful, responsive email templates  
✅ **Gmail SMTP Integration** - Reliable email delivery  

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Email**: Gmail SMTP with App Password
- **Database**: MySQL (AWS RDS) - for token validation
- **Server**: Uvicorn

## Project Structure

```
notification_service/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # MySQL connection (token validation)
│   ├── auth.py           # JWT validation
│   ├── dependencies.py    # FastAPI dependencies
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Email sending logic
│   ├── templates.py      # HTML email templates
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
SERVICE_NAME=notification_service
SERVICE_PORT=8006
HOST=0.0.0.0

# Copy JWT_SECRET_KEY from User Service
JWT_SECRET_KEY=your_jwt_secret_key_from_user_service

# Gmail SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=designervexel@gmail.com
SMTP_PASSWORD=jicefziqfhwketrg
SMTP_FROM_NAME=Salon Booking System

# Database (for token validation)
DB_HOST=database-1.cn8e0eyq896c.eu-north-1.rds.amazonaws.com
DB_PORT=3306
DB_NAME=salon-db
DB_USER=admin
DB_PASSWORD=4343435

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
LOG_LEVEL=INFO
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the Service

```bash
python main.py
```

The service will be available at:
- **API**: http://localhost:8006
- **Swagger Docs**: http://localhost:8006/docs
- **ReDoc**: http://localhost:8006/redoc

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/notifications/email/register-user` | POST | None | Send registration welcome email |
| `/api/v1/notifications/email/reset-password` | POST | None | Send password reset email |
| `/api/v1/notifications/email/create-staff` | POST | Admin | Send staff welcome email |
| `/api/v1/notifications/email/create-appointment` | POST | User | Send appointment confirmation |
| `/api/v1/notifications/email/update-appointment` | POST | User | Send appointment update notification |
| `/api/v1/notifications/email/cancel-appointment` | POST | User | Send appointment cancellation |
| `/api/v1/notifications/health` | GET | None | Health check |

## Testing the Endpoints

### 1. Health Check
```bash
curl http://localhost:8006/api/v1/notifications/health
```

### 2. Send Registration Email (No auth required)
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/register-user" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "full_name": "John Doe",
    "username": "johndoe"
  }'
```

### 3. Send Password Reset Email
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "full_name": "John Doe",
    "reset_token": "https://salon.com/reset?token=abc123",
    "expiry_minutes": 30
  }'
```

### 4. Send Staff Welcome Email (Admin only)
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/create-staff" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "staff@example.com",
    "full_name": "Jane Smith",
    "position": "Senior Stylist",
    "username": "janesmith",
    "temporary_password": "TempPass123"
  }'
```

### 5. Send Appointment Confirmation (Authenticated)
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/create-appointment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customer_name": "John Doe",
    "service_name": "Men Haircut",
    "staff_name": "Jane Smith",
    "appointment_datetime": "2025-11-25T10:00:00",
    "duration_minutes": 30,
    "price": 35.00,
    "appointment_id": 123
  }'
```

### 6. Send Appointment Update Email
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/update-appointment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customer_name": "John Doe",
    "service_name": "Men Haircut",
    "staff_name": "Jane Smith",
    "old_datetime": "2025-11-25T10:00:00",
    "new_datetime": "2025-11-26T14:00:00",
    "appointment_id": 123,
    "change_reason": "Customer requested different time"
  }'
```

### 7. Send Appointment Cancellation Email
```bash
curl -X POST "http://localhost:8006/api/v1/notifications/email/cancel-appointment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "customer_name": "John Doe",
    "service_name": "Men Haircut",
    "staff_name": "Jane Smith",
    "appointment_datetime": "2025-11-25T10:00:00",
    "appointment_id": 123,
    "cancellation_reason": "Schedule conflict"
  }'
```

## Response Format

### Success Response
```json
{
  "status": "success",
  "message": "Registration welcome email sent successfully",
  "email_sent_to": "customer@example.com",
  "email_type": "register_user"
}
```

### Error Response
```json
{
  "status": "error",
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "Failed to send email",
  "details": {}
}
```

## Email Templates

The service includes 6 professional HTML email templates:

1. **Registration Welcome** - Colorful welcome with account details
2. **Password Reset** - Security-focused with expiry warning
3. **Staff Welcome** - Professional onboarding with credentials
4. **Appointment Confirmation** - Detailed booking information
5. **Appointment Update** - Clear old vs new datetime comparison
6. **Appointment Cancellation** - Friendly cancellation notice

All templates feature:
- Responsive design
- Modern gradient headers
- Clear information boxes
- Call-to-action buttons
- Professional footer

## Gmail SMTP Setup

### Using App Password (Recommended)

1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account → Security → App Passwords
3. Generate a new app password for "Mail"
4. Use this password in `SMTP_PASSWORD`

### SMTP Settings
```
Host: smtp.gmail.com
Port: 587 (TLS)
User: your-email@gmail.com
Password: your-app-password (16 characters, no spaces)
```

## Integration with Other Services

### How to Call from Other Microservices

Add to your service's `config.py`:
```python
NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
```

Add to your `.env`:
```env
NOTIFICATION_SERVICE_URL=http://localhost:8006
```

### Sample Integration Code

```python
import httpx
from app.config import get_settings

settings = get_settings()

async def send_notification(endpoint: str, data: dict, token: str = None):
    """Send notification via Notification Service"""
    url = f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/notifications/email/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=30.0)
            return response.json()
    except Exception as e:
        print(f"Notification failed: {e}")
        return None
```

## Troubleshooting

### Issue: Authentication Failed
**Error**: `SMTP Authentication failed`
**Solution**: 
- Verify Gmail app password is correct (16 characters)
- Ensure 2FA is enabled on Gmail account
- Check for spaces in password

### Issue: Connection Timeout
**Error**: `Connection timed out`
**Solution**:
- Check SMTP_HOST and SMTP_PORT settings
- Verify network allows outbound SMTP
- Check firewall rules

### Issue: Email Not Received
**Solution**:
- Check spam/junk folder
- Verify recipient email address
- Check Gmail sending limits

## Production Considerations

1. **Rate Limiting**: Gmail has sending limits (500/day for regular, 2000/day for Workspace)
2. **Email Provider**: Consider using SendGrid, Mailgun, or AWS SES for production
3. **Queue System**: Add Redis/RabbitMQ for async email processing
4. **Logging**: Store email logs for debugging
5. **Templates**: Consider external template storage for easy updates

## License

Copyright © 2025 Salon Booking System

---

**Version**: 1.0.0  
**Port**: 8006  
**Dependencies**: User Service (for token validation)