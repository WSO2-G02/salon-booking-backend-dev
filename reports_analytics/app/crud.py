"""
Data aggregation functions for Reports & Analytics Service.
These functions call other microservices to collect and analyze data.
"""
import requests
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from . import models
import logging

logger = logging.getLogger(__name__)

# Service URLs
APPOINTMENT_SERVICE_URL = "http://appointment-service:8004"
SERVICE_MANAGEMENT_URL = "http://service-management:8002"
STAFF_SERVICE_URL = "http://staff-service:8003"
USER_SERVICE_URL = "http://user-service:8001"

async def get_appointments_by_date_range(start_date: date, end_date: date) -> List[Dict]:
    """
    Fetch appointments within date range from Appointment Service.
    
    Args:
        start_date: Start date for the range
        end_date: End date for the range
    
    Returns:
        List of appointment dictionaries
    """
    try:
        response = requests.get(
            f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000  # Adjust based on expected volume
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch appointments: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        logger.error(f"Error fetching appointments: {e}")
        return []

async def get_service_details(service_id: int) -> Optional[Dict]:
    """Get service details from Service Management Service"""
    try:
        response = requests.get(f"{SERVICE_MANAGEMENT_URL}/api/v1/services/{service_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching service {service_id}: {e}")
        return None

async def get_staff_details(staff_id: int) -> Optional[Dict]:
    """Get staff details from Staff Management Service"""
    try:
        response = requests.get(f"{STAFF_SERVICE_URL}/api/v1/staff/{staff_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching staff {staff_id}: {e}")
        return None

async def generate_revenue_report(start_date: date, end_date: date) -> models.RevenueReport:
    """
    Generate comprehensive revenue report.
    
    This function demonstrates the API Composition pattern by:
    1. Fetching appointments from Appointment Service
    2. Getting service details from Service Management Service
    3. Getting staff details from Staff Management Service
    4. Aggregating and calculating metrics
    
    Args:
        start_date: Report start date
        end_date: Report end date
    
    Returns:
        Revenue report with comprehensive metrics
    """
    # Fetch appointments in date range
    appointments = await get_appointments_by_date_range(start_date, end_date)
    
    # Filter only completed appointments for revenue calculation
    completed_appointments = [
        apt for apt in appointments 
        if apt.get("status") == "completed"
    ]
    
    total_revenue = Decimal('0.00')
    revenue_by_service = {}
    revenue_by_staff = {}
    daily_breakdown = {}
    service_cache = {}
    staff_cache = {}
    
    # Process each completed appointment
    for appointment in completed_appointments:
        # Get service details (with caching)
        service_id = appointment["service_id"]
        if service_id not in service_cache:
            service_cache[service_id] = await get_service_details(service_id)
        
        service_info = service_cache[service_id]
        if not service_info:
            continue
        
        # Get staff details (with caching)
        staff_id = appointment["staff_id"]
        if staff_id not in staff_cache:
            staff_cache[staff_id] = await get_staff_details(staff_id)
        
        staff_info = staff_cache[staff_id]
        
        # Calculate revenue
        appointment_revenue = Decimal(str(appointment["service_price"]))
        total_revenue += appointment_revenue
        
        # Revenue by service
        service_name = service_info["name"]
        revenue_by_service[service_name] = revenue_by_service.get(service_name, Decimal('0.00')) + appointment_revenue
        
        # Revenue by staff
        if staff_info:
            staff_name = staff_info.get("employee_id", f"Staff {staff_id}")
            revenue_by_staff[staff_name] = revenue_by_staff.get(staff_name, Decimal('0.00')) + appointment_revenue
        
        # Daily breakdown
        appointment_date = datetime.fromisoformat(appointment["appointment_datetime"]).date()
        date_str = appointment_date.isoformat()
        if date_str not in daily_breakdown:
            daily_breakdown[date_str] = {"date": date_str, "revenue": Decimal('0.00'), "appointments": 0}
        
        daily_breakdown[date_str]["revenue"] += appointment_revenue
        daily_breakdown[date_str]["appointments"] += 1
    
    # Calculate average appointment value
    total_appointments = len(completed_appointments)
    average_appointment_value = total_revenue / total_appointments if total_appointments > 0 else Decimal('0.00')
    
    # Convert daily breakdown to list and sort by date
    daily_breakdown_list = sorted(daily_breakdown.values(), key=lambda x: x["date"])
    
    return models.RevenueReport(
        start_date=start_date,
        end_date=end_date,
        total_revenue=total_revenue,
        total_appointments=total_appointments,
        average_appointment_value=average_appointment_value,
        revenue_by_service=revenue_by_service,
        revenue_by_staff=revenue_by_staff,
        daily_breakdown=daily_breakdown_list
    )

async def generate_stylist_performance_report(
    staff_id: int,
    start_date: date,
    end_date: date
) -> Optional[models.StylistPerformanceReport]:
    """
    Generate performance report for a specific stylist.
    
    Args:
        staff_id: Staff member ID
        start_date: Report period start
        end_date: Report period end
    
    Returns:
        Stylist performance report or None if staff not found
    """
    # Get staff details
    staff_info = await get_staff_details(staff_id)
    if not staff_info:
        return None
    
    # Get appointments for this staff member
    try:
        response = requests.get(
            f"{APPOINTMENT_SERVICE_URL}/api/v1/appointments/staff/{staff_id}",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
        
        if response.status_code != 200:
            return None
            
        appointments = response.json()
        
    except requests.RequestException:
        return None
    
    # Analyze appointment data
    total_appointments = len(appointments)
    completed_appointments = len([a for a in appointments if a["status"] == "completed"])
    cancelled_appointments = len([a for a in appointments if a["status"] == "cancelled"])
    no_show_appointments = len([a for a in appointments if a["status"] == "no_show"])
    
    # Calculate total revenue generated
    total_revenue = sum(
        Decimal(str(a["service_price"])) 
        for a in appointments 
        if a["status"] == "completed"
    )
    
    # Calculate average appointment duration
    total_duration = sum(a["duration_minutes"] for a in appointments if a["status"] == "completed")
    average_duration = total_duration // completed_appointments if completed_appointments > 0 else 0
    
    return models.StylistPerformanceReport(
        staff_id=staff_id,
        staff_name=staff_info.get("employee_id", f"Staff {staff_id}"),
        period_start=start_date,
        period_end=end_date,
        total_appointments=total_appointments,
        completed_appointments=completed_appointments,
        cancelled_appointments=cancelled_appointments,
        no_show_appointments=no_show_appointments,
        total_revenue_generated=total_revenue,
        average_appointment_duration=average_duration,
        specialties=staff_info.get("specialties", [])
    )

async def generate_service_popularity_report() -> List[models.ServicePopularityReport]:
    """
    Generate service popularity report.
    
    Returns:
        List of service popularity reports
    """
    # Get all services
    try:
        response = requests.get(f"{SERVICE_MANAGEMENT_URL}/api/v1/services")
        if response.status_code != 200:
            return []
        
        services = response.json()
        
    except requests.RequestException:
        return []
    
    # Get appointments for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    appointments = await get_appointments_by_date_range(start_date, end_date)
    
    service_reports = []
    
    for service in services:
        service_id = service["id"]
        
        # Filter appointments for this service
        service_appointments = [a for a in appointments if a["service_id"] == service_id]
        completed_appointments = [a for a in service_appointments if a["status"] == "completed"]
        
        # Calculate metrics
        total_bookings = len(service_appointments)
        completed_bookings = len(completed_appointments)
        total_revenue = sum(
            Decimal(str(a["service_price"])) 
            for a in completed_appointments
        )
        
        # Create booking trend (simplified - weekly counts)
        booking_trend = []  # In production, implement proper trending logic
        
        service_reports.append(models.ServicePopularityReport(
            service_id=service_id,
            service_name=service["name"],
            category=service["category"],
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            total_revenue=total_revenue,
            booking_trend=booking_trend
        ))
    
    # Sort by popularity (total bookings)
    service_reports.sort(key=lambda x: x.total_bookings, reverse=True)
    
    return service_reports

async def generate_business_insights() -> models.BusinessInsights:
    """
    Generate overall business insights dashboard.
    
    Returns:
        Business insights with key metrics
    """
    report_date = date.today()
    
    # Get recent appointments for analysis
    start_date = report_date - timedelta(days=30)
    appointments = await get_appointments_by_date_range(start_date, report_date)
    
    # Analyze peak booking patterns
    hour_counts = {}
    day_counts = {}
    
    for appointment in appointments:
        appointment_datetime = datetime.fromisoformat(appointment["appointment_datetime"])
        hour = appointment_datetime.hour
        day_name = appointment_datetime.strftime("%A")
        
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
        day_counts[day_name] = day_counts.get(day_name, 0) + 1
    
    # Get peak hours and days
    peak_hours = sorted(hour_counts.keys(), key=hour_counts.get, reverse=True)[:3]
    peak_days = sorted(day_counts.keys(), key=day_counts.get, reverse=True)[:3]
    
    # Get service popularity
    service_reports = await generate_service_popularity_report()
    most_popular_services = [report.service_name for report in service_reports[:5]]
    
    # Calculate average booking lead time
    lead_times = []
    for appointment in appointments:
        appointment_datetime = datetime.fromisoformat(appointment["appointment_datetime"])
        created_at = datetime.fromisoformat(appointment["created_at"])
        lead_time_days = (appointment_datetime.date() - created_at.date()).days
        lead_times.append(lead_time_days)
    
    average_lead_time = sum(lead_times) // len(lead_times) if lead_times else 0
    
    return models.BusinessInsights(
        report_date=report_date,
        total_active_customers=len(set(a["user_id"] for a in appointments)),  # Simplified
        new_customers_this_month=0,  # Would need User Service integration
        customer_retention_rate=0.0,  # Would need historical analysis
        peak_booking_hours=peak_hours,
        peak_booking_days=peak_days,
        most_popular_services=most_popular_services,
        top_performing_staff=[],  # Would need staff performance analysis
        average_booking_lead_time=average_lead_time
    )