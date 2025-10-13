"""
Reports & Analytics API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date, timedelta
from .. import crud, models

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

@router.get("/revenue", response_model=models.RevenueReport)
async def get_revenue_report(
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report")
):
    """
    Generate revenue report for a specific date range.
    
    This endpoint demonstrates the API Composition pattern by aggregating
    data from multiple services to create a comprehensive revenue report.
    
    Args:
        start_date: Start date for the report period
        end_date: End date for the report period
    
    Returns:
        Detailed revenue report with breakdowns by service, staff, and date
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 365 days"
        )
    
    try:
        report = await crud.generate_revenue_report(start_date, end_date)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate revenue report"
        )

@router.get("/stylist-performance/{staff_id}", response_model=models.StylistPerformanceReport)
async def get_stylist_performance_report(
    staff_id: int,
    start_date: Optional[date] = Query(None, description="Start date (defaults to 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to today)")
):
    """
    Generate performance report for a specific stylist.
    
    Args:
        staff_id: Staff member ID
        start_date: Report period start (optional)
        end_date: Report period end (optional)
    
    Returns:
        Stylist performance metrics and statistics
    """
    # Default to last 30 days if dates not provided
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    
    try:
        report = await crud.generate_stylist_performance_report(staff_id, start_date, end_date)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found"
            )
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate stylist performance report"
        )

@router.get("/service-popularity", response_model=List[models.ServicePopularityReport])
async def get_service_popularity_report():
    """
    Generate service popularity report.
    
    Returns services ranked by popularity with booking statistics
    and revenue information.
    
    Returns:
        List of services ordered by popularity
    """
    try:
        reports = await crud.generate_service_popularity_report()
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate service popularity report"
        )

@router.get("/business-insights", response_model=models.BusinessInsights)
async def get_business_insights():
    """
    Generate overall business insights dashboard.
    
    Provides key metrics and insights for business management including
    peak booking times, popular services, and customer patterns.
    
    Returns:
        Business insights with key performance indicators
    """
    try:
        insights = await crud.generate_business_insights()
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate business insights"
        )

@router.get("/appointments-summary")
async def get_appointments_summary(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=7)),
    end_date: date = Query(default_factory=date.today)
):
    """
    Get summary of appointments for a date range.
    
    Provides quick overview of appointment statistics.
    
    Args:
        start_date: Start date (defaults to 7 days ago)
        end_date: End date (defaults to today)
    
    Returns:
        Appointment summary statistics
    """
    try:
        appointments = await crud.get_appointments_by_date_range(start_date, end_date)
        
        total_appointments = len(appointments)
        status_counts = {}
        
        for appointment in appointments:
            status = appointment.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_appointments": total_appointments,
            "status_breakdown": status_counts,
            "completion_rate": round(
                (status_counts.get("completed", 0) / total_appointments * 100) if total_appointments > 0 else 0, 
                2
            )
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate appointments summary"
        )