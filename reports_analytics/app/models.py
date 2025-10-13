"""
Models for Reports & Analytics Service.
This service primarily aggregates data from other services,
so it doesn't maintain its own persistent storage.
"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date, datetime
from decimal import Decimal

class RevenueReport(BaseModel):
    """Revenue report schema"""
    start_date: date
    end_date: date
    total_revenue: Decimal
    total_appointments: int
    average_appointment_value: Decimal
    revenue_by_service: Dict[str, Decimal]
    revenue_by_staff: Dict[str, Decimal]
    daily_breakdown: List[Dict[str, any]]

class StylistPerformanceReport(BaseModel):
    """Stylist performance report schema"""
    staff_id: int
    staff_name: str
    period_start: date
    period_end: date
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    total_revenue_generated: Decimal
    average_appointment_duration: int
    customer_satisfaction_score: Optional[float] = None
    specialties: List[str]

class ServicePopularityReport(BaseModel):
    """Service popularity report schema"""
    service_id: int
    service_name: str
    category: str
    total_bookings: int
    completed_bookings: int
    total_revenue: Decimal
    average_rating: Optional[float] = None
    booking_trend: List[Dict[str, any]]  # Monthly/weekly trends

class BusinessInsights(BaseModel):
    """Overall business insights"""
    report_date: date
    total_active_customers: int
    new_customers_this_month: int
    customer_retention_rate: float
    peak_booking_hours: List[int]  # Hours of the day (0-23)
    peak_booking_days: List[str]   # Days of the week
    most_popular_services: List[str]
    top_performing_staff: List[str]
    average_booking_lead_time: int  # Days in advance