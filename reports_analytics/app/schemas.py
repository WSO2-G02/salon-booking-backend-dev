"""
Pydantic Models for Analytics Service
Request and Response schemas for analytics data
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# ============================================================================
# Revenue Analytics Schemas
# ============================================================================

class RevenueSummary(BaseModel):
    """Overall revenue summary"""
    total_revenue: Decimal
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    average_revenue_per_appointment: Decimal
    period_start: Optional[date]
    period_end: Optional[date]
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class DailyRevenue(BaseModel):
    """Daily revenue data"""
    date: date
    revenue: Decimal
    appointment_count: int
    completed_count: int
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class MonthlyRevenue(BaseModel):
    """Monthly revenue data"""
    year: int
    month: int
    month_name: str
    revenue: Decimal
    appointment_count: int
    completed_count: int
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class ServiceRevenue(BaseModel):
    """Revenue by service"""
    service_id: int
    service_name: str
    category: Optional[str]
    total_revenue: Decimal
    booking_count: int
    average_price: Decimal
    percentage_of_total: float
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class StaffRevenue(BaseModel):
    """Revenue by staff member"""
    staff_id: int
    staff_name: str
    position: Optional[str]
    total_revenue: Decimal
    booking_count: int
    completed_count: int
    average_revenue_per_booking: Decimal
    percentage_of_total: float
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ============================================================================
# Service Analytics Schemas
# ============================================================================

class ServicePopularity(BaseModel):
    """Service popularity metrics"""
    service_id: int
    service_name: str
    category: Optional[str]
    booking_count: int
    completed_count: int
    cancellation_count: int
    completion_rate: float
    rank: int
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class ServicePerformance(BaseModel):
    """Service performance metrics"""
    service_id: int
    service_name: str
    category: Optional[str]
    total_revenue: Decimal
    booking_count: int
    average_price: Decimal
    average_duration: int
    completion_rate: float
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ============================================================================
# Staff Analytics Schemas
# ============================================================================

class StaffPerformance(BaseModel):
    """Staff performance metrics"""
    staff_id: int
    staff_name: str
    position: Optional[str]
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    total_revenue: Decimal
    completion_rate: float
    average_revenue_per_appointment: Decimal
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class StaffStats(BaseModel):
    """Individual staff statistics"""
    staff_id: int
    staff_name: str
    position: Optional[str]
    total_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    pending_appointments: int
    total_revenue: Decimal
    average_rating: Optional[float]
    top_services: List[dict]
    busiest_day: Optional[str]
    busiest_hour: Optional[int]
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ============================================================================
# Appointment Analytics Schemas
# ============================================================================

class AppointmentSummary(BaseModel):
    """Appointment status summary"""
    total_appointments: int
    pending: int
    confirmed: int
    completed: int
    cancelled: int
    no_show: int
    completion_rate: float
    cancellation_rate: float
    no_show_rate: float


class BookingTrend(BaseModel):
    """Booking trend data"""
    date: date
    booking_count: int
    completed_count: int
    cancelled_count: int


class PeakHour(BaseModel):
    """Peak booking hour data"""
    hour: int
    hour_label: str
    booking_count: int
    percentage: float


# ============================================================================
# Customer Analytics Schemas
# ============================================================================

class TopCustomer(BaseModel):
    """Top customer data"""
    user_id: int
    customer_name: str
    email: Optional[str]
    total_spent: Decimal
    visit_count: int
    average_spent_per_visit: Decimal
    last_visit: Optional[datetime]
    rank: int
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class CustomerRetention(BaseModel):
    """Customer retention metrics"""
    total_customers: int
    new_customers_this_month: int
    returning_customers: int
    retention_rate: float
    average_visits_per_customer: float
    average_lifetime_value: Decimal
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ============================================================================
# Dashboard Schema
# ============================================================================

class DashboardData(BaseModel):
    """Combined dashboard data"""
    revenue_summary: RevenueSummary
    appointment_summary: AppointmentSummary
    top_services: List[ServicePopularity]
    top_staff: List[StaffPerformance]
    recent_revenue: List[DailyRevenue]
    
    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


# ============================================================================
# Standard API Response Schemas
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    status: str = "success"
    data: Optional[dict] = None
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_code: str
    message: str
    details: Optional[dict] = None