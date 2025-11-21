"""
Analytics Service API Routes
Implements all REST API endpoints for the Analytics Service
All analytics endpoints require Admin access
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from datetime import date
import logging

from app.schemas import (
    RevenueSummary, DailyRevenue, MonthlyRevenue, ServiceRevenue, StaffRevenue,
    ServicePopularity, ServicePerformance, StaffPerformance, StaffStats,
    AppointmentSummary, BookingTrend, PeakHour,
    TopCustomer, CustomerRetention, DashboardData
)
from app.services import AnalyticsService
from app.database import get_db_manager, DatabaseManager
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


def get_analytics_service(db: DatabaseManager = Depends(get_db_manager)) -> AnalyticsService:
    """Dependency to get AnalyticsService instance"""
    return AnalyticsService(db)


# ============================================================================
# Revenue Analytics Endpoints
# ============================================================================

@router.get("/revenue/summary", response_model=RevenueSummary)
async def get_revenue_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get overall revenue summary (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    
    Returns total revenue, appointment counts, and averages.
    """
    try:
        summary = analytics.get_revenue_summary(start_date, end_date)
        return RevenueSummary(**summary)
    except Exception as e:
        logger.error(f"Error fetching revenue summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue summary"
        )


@router.get("/revenue/daily", response_model=List[DailyRevenue])
async def get_daily_revenue(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(30, ge=1, le=365, description="Number of days"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get daily revenue breakdown (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of days to return (default: 30)
    """
    try:
        data = analytics.get_daily_revenue(start_date, end_date, limit)
        return [DailyRevenue(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching daily revenue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch daily revenue"
        )


@router.get("/revenue/monthly", response_model=List[MonthlyRevenue])
async def get_monthly_revenue(
    year: Optional[int] = Query(None, description="Filter by year"),
    limit: int = Query(12, ge=1, le=60, description="Number of months"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get monthly revenue breakdown (Admin only)
    
    - **year**: Filter by specific year (optional)
    - **limit**: Number of months to return (default: 12)
    """
    try:
        data = analytics.get_monthly_revenue(year, limit)
        return [MonthlyRevenue(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching monthly revenue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch monthly revenue"
        )


@router.get("/revenue/by-service", response_model=List[ServiceRevenue])
async def get_revenue_by_service(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=50, description="Number of services"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get revenue grouped by service (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of services to return (default: 10)
    """
    try:
        data = analytics.get_revenue_by_service(start_date, end_date, limit)
        return [ServiceRevenue(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching revenue by service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue by service"
        )


@router.get("/revenue/by-staff", response_model=List[StaffRevenue])
async def get_revenue_by_staff(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=50, description="Number of staff"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get revenue grouped by staff member (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of staff to return (default: 10)
    """
    try:
        data = analytics.get_revenue_by_staff(start_date, end_date, limit)
        return [StaffRevenue(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching revenue by staff: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue by staff"
        )


@router.get("/revenue/by-date-range", response_model=RevenueSummary)
async def get_revenue_by_date_range(
    start_date: date = Query(..., description="Start date (required)"),
    end_date: date = Query(..., description="End date (required)"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get revenue for a custom date range (Admin only)
    
    - **start_date**: Start date (required)
    - **end_date**: End date (required)
    """
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    try:
        summary = analytics.get_revenue_summary(start_date, end_date)
        return RevenueSummary(**summary)
    except Exception as e:
        logger.error(f"Error fetching revenue by date range: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue"
        )


# ============================================================================
# Service Analytics Endpoints
# ============================================================================

@router.get("/services/popularity", response_model=List[ServicePopularity])
async def get_service_popularity(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=50, description="Number of services"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get service popularity rankings (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of services to return (default: 10)
    
    Returns services ranked by booking count.
    """
    try:
        data = analytics.get_service_popularity(start_date, end_date, limit)
        return [ServicePopularity(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching service popularity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch service popularity"
        )


@router.get("/services/performance", response_model=List[ServicePerformance])
async def get_service_performance(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get service performance metrics (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    
    Returns revenue, bookings, and completion rate per service.
    """
    try:
        data = analytics.get_service_performance(start_date, end_date)
        return [ServicePerformance(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching service performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch service performance"
        )


# ============================================================================
# Staff Analytics Endpoints
# ============================================================================

@router.get("/staff/performance", response_model=List[StaffPerformance])
async def get_staff_performance(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=50, description="Number of staff"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get staff performance metrics (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of staff to return (default: 10)
    
    Returns appointments, revenue, and completion rates per staff.
    """
    try:
        data = analytics.get_staff_performance(start_date, end_date, limit)
        return [StaffPerformance(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching staff performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch staff performance"
        )


@router.get("/staff/{staff_id}/stats", response_model=StaffStats)
async def get_staff_stats(
    staff_id: int,
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed statistics for a specific staff member (Admin only)
    
    - **staff_id**: Staff ID
    
    Returns detailed stats including top services and busiest times.
    """
    try:
        stats = analytics.get_staff_stats(staff_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found or has no appointments"
            )
        return StaffStats(**stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching staff stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch staff statistics"
        )


# ============================================================================
# Appointment Analytics Endpoints
# ============================================================================

@router.get("/appointments/summary", response_model=AppointmentSummary)
async def get_appointment_summary(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get appointment status summary (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    
    Returns counts and rates for each appointment status.
    """
    try:
        summary = analytics.get_appointment_summary(start_date, end_date)
        return AppointmentSummary(**summary)
    except Exception as e:
        logger.error(f"Error fetching appointment summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch appointment summary"
        )


@router.get("/appointments/trends", response_model=List[BookingTrend])
async def get_booking_trends(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(30, ge=1, le=365, description="Number of days"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get booking trends over time (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of days to return (default: 30)
    """
    try:
        data = analytics.get_booking_trends(start_date, end_date, limit)
        return [BookingTrend(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching booking trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch booking trends"
        )


@router.get("/appointments/peak-hours", response_model=List[PeakHour])
async def get_peak_hours(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get peak booking hours (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    
    Returns booking counts grouped by hour of day.
    """
    try:
        data = analytics.get_peak_hours(start_date, end_date)
        return [PeakHour(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching peak hours: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch peak hours"
        )


# ============================================================================
# Customer Analytics Endpoints
# ============================================================================

@router.get("/customers/top", response_model=List[TopCustomer])
async def get_top_customers(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(10, ge=1, le=50, description="Number of customers"),
    sort_by: str = Query("spending", description="Sort by: 'spending' or 'visits'"),
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get top customers by spending or visits (Admin only)
    
    - **start_date**: Filter from date (optional)
    - **end_date**: Filter to date (optional)
    - **limit**: Number of customers to return (default: 10)
    - **sort_by**: Sort by 'spending' or 'visits' (default: spending)
    """
    if sort_by not in ["spending", "visits"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be 'spending' or 'visits'"
        )
    
    try:
        data = analytics.get_top_customers(start_date, end_date, limit, sort_by)
        return [TopCustomer(**item) for item in data]
    except Exception as e:
        logger.error(f"Error fetching top customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch top customers"
        )


@router.get("/customers/retention", response_model=CustomerRetention)
async def get_customer_retention(
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get customer retention metrics (Admin only)
    
    Returns total customers, new/returning customers, retention rate, and lifetime value.
    """
    try:
        data = analytics.get_customer_retention()
        return CustomerRetention(**data)
    except Exception as e:
        logger.error(f"Error fetching customer retention: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch customer retention"
        )


# ============================================================================
# Dashboard Endpoint
# ============================================================================

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    current_admin: Dict = Depends(get_current_admin),
    analytics: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get combined dashboard data (Admin only)
    
    Returns overview data including:
    - Revenue summary (last 30 days)
    - Appointment summary (last 30 days)
    - Top 5 services
    - Top 5 staff
    - Last 7 days revenue
    """
    try:
        data = analytics.get_dashboard_data()
        return DashboardData(**data)
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def health_check(db: DatabaseManager = Depends(get_db_manager)):
    """
    Health check endpoint to verify service and database status
    """
    db_healthy = db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "analytics_service",
        "database": "connected" if db_healthy else "disconnected"
    }