# Analytics Service - Salon Booking System

Analytics, reporting, and business intelligence microservice for the Salon Booking System.

## Features

✅ **Revenue Analytics** - Total revenue, daily/monthly breakdowns, by service/staff  
✅ **Service Analytics** - Popularity rankings, performance metrics  
✅ **Staff Analytics** - Performance metrics, individual statistics  
✅ **Appointment Analytics** - Status summary, trends, peak hours  
✅ **Customer Analytics** - Top customers, retention metrics  
✅ **Dashboard** - Combined overview data  
✅ **Date Range Filters** - Filter all analytics by custom date ranges  
✅ **Admin Only Access** - All endpoints require admin authentication  

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Python**: 3.9+
- **Database**: MySQL (AWS RDS) - `salon-db`
- **Authentication**: JWT (from User Service)
- **Server**: Uvicorn

## Project Structure

```
analytics_service/
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
SERVICE_NAME=analytics_service
SERVICE_PORT=8005
HOST=0.0.0.0

# Copy JWT_SECRET_KEY from User Service
JWT_SECRET_KEY=your_jwt_secret_key_from_user_service
JWT_ALGORITHM=HS256

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
- **API**: http://localhost:8005
- **Swagger Docs**: http://localhost:8005/docs
- **ReDoc**: http://localhost:8005/redoc

## API Endpoints Overview

### Revenue Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/revenue/summary` | Overall revenue summary |
| `GET /api/v1/analytics/revenue/daily` | Daily revenue breakdown |
| `GET /api/v1/analytics/revenue/monthly` | Monthly revenue breakdown |
| `GET /api/v1/analytics/revenue/by-service` | Revenue by service |
| `GET /api/v1/analytics/revenue/by-staff` | Revenue by staff member |
| `GET /api/v1/analytics/revenue/by-date-range` | Revenue for custom date range |

### Service Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/services/popularity` | Service popularity rankings |
| `GET /api/v1/analytics/services/performance` | Service performance metrics |

### Staff Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/staff/performance` | Staff performance metrics |
| `GET /api/v1/analytics/staff/{staff_id}/stats` | Individual staff statistics |

### Appointment Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/appointments/summary` | Appointment status summary |
| `GET /api/v1/analytics/appointments/trends` | Booking trends over time |
| `GET /api/v1/analytics/appointments/peak-hours` | Peak booking hours |

### Customer Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/customers/top` | Top customers |
| `GET /api/v1/analytics/customers/retention` | Customer retention metrics |

### Dashboard
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/dashboard` | Combined dashboard data |

### Health Check
| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/analytics/health` | Service health check |

## Testing the Endpoints

### 1. Health Check (No auth required)
```bash
curl http://localhost:8005/api/v1/analytics/health
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

---

## Revenue Analytics Examples

### 3. Get Revenue Summary
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/summary" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "total_revenue": 2500.00,
  "total_appointments": 75,
  "completed_appointments": 60,
  "cancelled_appointments": 10,
  "average_revenue_per_appointment": 41.67,
  "period_start": null,
  "period_end": null
}
```

### 4. Get Revenue Summary with Date Filter
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/summary?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 5. Get Daily Revenue (Last 30 Days)
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/daily?limit=30" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "date": "2025-11-18",
    "revenue": 350.00,
    "appointment_count": 12,
    "completed_count": 10
  },
  {
    "date": "2025-11-17",
    "revenue": 280.00,
    "appointment_count": 8,
    "completed_count": 7
  }
]
```

### 6. Get Monthly Revenue
```bash
# All months
curl "http://localhost:8005/api/v1/analytics/revenue/monthly" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Specific year
curl "http://localhost:8005/api/v1/analytics/revenue/monthly?year=2025" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "year": 2025,
    "month": 11,
    "month_name": "November",
    "revenue": 2500.00,
    "appointment_count": 75,
    "completed_count": 60
  }
]
```

### 7. Get Revenue by Service
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/by-service?limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "service_id": 1,
    "service_name": "Men Haircut",
    "category": "Hair",
    "total_revenue": 1050.00,
    "booking_count": 30,
    "average_price": 35.00,
    "percentage_of_total": 42.0
  },
  {
    "service_id": 2,
    "service_name": "Hair Coloring",
    "category": "Hair",
    "total_revenue": 850.00,
    "booking_count": 10,
    "average_price": 85.00,
    "percentage_of_total": 34.0
  }
]
```

### 8. Get Revenue by Staff
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/by-staff" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "staff_id": 1,
    "staff_name": "Jane Smith",
    "position": "Senior Stylist",
    "total_revenue": 1500.00,
    "booking_count": 40,
    "completed_count": 35,
    "average_revenue_per_booking": 42.86,
    "percentage_of_total": 60.0
  }
]
```

### 9. Get Revenue by Custom Date Range
```bash
curl "http://localhost:8005/api/v1/analytics/revenue/by-date-range?start_date=2025-11-01&end_date=2025-11-15" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Service Analytics Examples

### 10. Get Service Popularity
```bash
curl "http://localhost:8005/api/v1/analytics/services/popularity" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "service_id": 1,
    "service_name": "Men Haircut",
    "category": "Hair",
    "booking_count": 45,
    "completed_count": 40,
    "cancellation_count": 3,
    "completion_rate": 88.89,
    "rank": 1
  },
  {
    "service_id": 3,
    "service_name": "Manicure",
    "category": "Nails",
    "booking_count": 30,
    "completed_count": 28,
    "cancellation_count": 1,
    "completion_rate": 93.33,
    "rank": 2
  }
]
```

### 11. Get Service Performance
```bash
curl "http://localhost:8005/api/v1/analytics/services/performance" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "service_id": 1,
    "service_name": "Men Haircut",
    "category": "Hair",
    "total_revenue": 1400.00,
    "booking_count": 45,
    "average_price": 35.00,
    "average_duration": 30,
    "completion_rate": 88.89
  }
]
```

---

## Staff Analytics Examples

### 12. Get Staff Performance
```bash
curl "http://localhost:8005/api/v1/analytics/staff/performance" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "staff_id": 1,
    "staff_name": "Jane Smith",
    "position": "Senior Stylist",
    "total_appointments": 50,
    "completed_appointments": 45,
    "cancelled_appointments": 3,
    "no_show_appointments": 2,
    "total_revenue": 1800.00,
    "completion_rate": 90.0,
    "average_revenue_per_appointment": 40.00
  }
]
```

### 13. Get Individual Staff Stats
```bash
curl "http://localhost:8005/api/v1/analytics/staff/1/stats" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "staff_id": 1,
  "staff_name": "Jane Smith",
  "position": "Senior Stylist",
  "total_appointments": 50,
  "completed_appointments": 45,
  "cancelled_appointments": 3,
  "no_show_appointments": 2,
  "pending_appointments": 5,
  "total_revenue": 1800.00,
  "average_rating": null,
  "top_services": [
    {"service_name": "Men Haircut", "count": 20},
    {"service_name": "Hair Coloring", "count": 15}
  ],
  "busiest_day": "Saturday",
  "busiest_hour": 10
}
```

---

## Appointment Analytics Examples

### 14. Get Appointment Summary
```bash
curl "http://localhost:8005/api/v1/analytics/appointments/summary" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "total_appointments": 100,
  "pending": 10,
  "confirmed": 15,
  "completed": 65,
  "cancelled": 7,
  "no_show": 3,
  "completion_rate": 65.0,
  "cancellation_rate": 7.0,
  "no_show_rate": 3.0
}
```

### 15. Get Booking Trends
```bash
curl "http://localhost:8005/api/v1/analytics/appointments/trends?limit=7" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "date": "2025-11-18",
    "booking_count": 12,
    "completed_count": 10,
    "cancelled_count": 1
  },
  {
    "date": "2025-11-17",
    "booking_count": 8,
    "completed_count": 7,
    "cancelled_count": 0
  }
]
```

### 16. Get Peak Hours
```bash
curl "http://localhost:8005/api/v1/analytics/appointments/peak-hours" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "hour": 10,
    "hour_label": "10:00 - 10:59",
    "booking_count": 25,
    "percentage": 25.0
  },
  {
    "hour": 14,
    "hour_label": "14:00 - 14:59",
    "booking_count": 20,
    "percentage": 20.0
  }
]
```

---

## Customer Analytics Examples

### 17. Get Top Customers by Spending
```bash
curl "http://localhost:8005/api/v1/analytics/customers/top?sort_by=spending&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
[
  {
    "user_id": 5,
    "customer_name": "Alice Johnson",
    "email": "alice@example.com",
    "total_spent": 450.00,
    "visit_count": 8,
    "average_spent_per_visit": 56.25,
    "last_visit": "2025-11-18T14:00:00",
    "rank": 1
  }
]
```

### 18. Get Top Customers by Visits
```bash
curl "http://localhost:8005/api/v1/analytics/customers/top?sort_by=visits&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 19. Get Customer Retention Metrics
```bash
curl "http://localhost:8005/api/v1/analytics/customers/retention" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "total_customers": 50,
  "new_customers_this_month": 8,
  "returning_customers": 35,
  "retention_rate": 70.0,
  "average_visits_per_customer": 2.5,
  "average_lifetime_value": 125.00
}
```

---

## Dashboard Example

### 20. Get Dashboard Data
```bash
curl "http://localhost:8005/api/v1/analytics/dashboard" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "revenue_summary": {
    "total_revenue": 2500.00,
    "total_appointments": 75,
    "completed_appointments": 60,
    "cancelled_appointments": 10,
    "average_revenue_per_appointment": 41.67,
    "period_start": "2025-10-19",
    "period_end": "2025-11-18"
  },
  "appointment_summary": {
    "total_appointments": 75,
    "pending": 5,
    "confirmed": 8,
    "completed": 60,
    "cancelled": 10,
    "no_show": 2,
    "completion_rate": 80.0,
    "cancellation_rate": 13.33,
    "no_show_rate": 2.67
  },
  "top_services": [...],
  "top_staff": [...],
  "recent_revenue": [...]
}
```

---

## Testing with Swagger UI

1. Open: http://localhost:8005/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_ADMIN_ACCESS_TOKEN`
4. Click "Authorize"
5. Test any endpoint directly from the UI

## Common Query Parameters

Most endpoints support these filters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | date | Filter from date (YYYY-MM-DD) |
| `end_date` | date | Filter to date (YYYY-MM-DD) |
| `limit` | int | Number of results to return |

## Access Control

⚠️ **ALL analytics endpoints require Admin authentication**

Regular users will receive:
```json
{
  "detail": "Admin privileges required for analytics access"
}
```

## HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Admin access required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Data Sources

The Analytics Service queries data from:

| Table | Used For |
|-------|----------|
| `appointments` | All analytics (revenue, bookings, etc.) |
| `services` | Service names, categories |
| `staff` | Staff positions |
| `users` | Customer/staff names, emails |

## Performance Notes

- All queries use indexed columns for filtering
- Large date ranges may take longer to process
- Consider caching for frequently accessed dashboards
- Use appropriate `limit` values for pagination

## Troubleshooting

### Issue: No Data Returned
**Cause**: No appointments in the date range or database empty.
**Solution**: Create some test appointments first.

### Issue: Admin Access Required
**Error**: `403 Forbidden`
**Solution**: Login with admin account from User Service.

### Issue: Zero Revenue
**Cause**: No completed appointments (only completed appointments count toward revenue).
**Solution**: Update appointment status to 'completed'.

## Development

### Running with Auto-reload
```bash
uvicorn main:app --reload --port 8005
```

## Production Deployment

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8005
```

## License

Copyright © 2025 Salon Booking System

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Port**: 8005  
**Database**: salon-db (reads from appointments, services, staff, users tables)  
**Access**: Admin only