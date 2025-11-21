"""
Analytics Service Business Logic Layer
Handles all analytics-related operations
"""
from typing import Optional, Dict, List
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import calendar

from app.database import DatabaseManager

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for analytics operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ========================================================================
    # Revenue Analytics
    # ========================================================================
    
    def get_revenue_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get overall revenue summary
        
        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
        
        Returns:
            Revenue summary dictionary
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN status = 'completed' THEN service_price ELSE 0 END), 0) as total_revenue,
                COUNT(*) as total_appointments,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_appointments,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_appointments
            FROM appointments
            {where_clause}
        """
        
        result = self.db.execute_query(query, tuple(params) if params else None, fetch_one=True)
        
        total_revenue = result['total_revenue'] or Decimal('0')
        completed = result['completed_appointments'] or 0
        
        avg_revenue = total_revenue / completed if completed > 0 else Decimal('0')
        
        return {
            "total_revenue": total_revenue,
            "total_appointments": result['total_appointments'] or 0,
            "completed_appointments": completed,
            "cancelled_appointments": result['cancelled_appointments'] or 0,
            "average_revenue_per_appointment": round(avg_revenue, 2),
            "period_start": start_date,
            "period_end": end_date
        }
    
    def get_daily_revenue(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30
    ) -> List[Dict]:
        """
        Get daily revenue breakdown
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of days to return
        
        Returns:
            List of daily revenue data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                DATE(appointment_datetime) as date,
                COALESCE(SUM(CASE WHEN status = 'completed' THEN service_price ELSE 0 END), 0) as revenue,
                COUNT(*) as appointment_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM appointments
            {where_clause}
            GROUP BY DATE(appointment_datetime)
            ORDER BY date DESC
            LIMIT %s
        """
        
        params.append(limit)
        return self.db.execute_query(query, tuple(params))
    
    def get_monthly_revenue(
        self,
        year: Optional[int] = None,
        limit: int = 12
    ) -> List[Dict]:
        """
        Get monthly revenue breakdown
        
        Args:
            year: Filter by specific year
            limit: Number of months to return
        
        Returns:
            List of monthly revenue data
        """
        conditions = []
        params = []
        
        if year:
            conditions.append("YEAR(appointment_datetime) = %s")
            params.append(year)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                YEAR(appointment_datetime) as year,
                MONTH(appointment_datetime) as month,
                COALESCE(SUM(CASE WHEN status = 'completed' THEN service_price ELSE 0 END), 0) as revenue,
                COUNT(*) as appointment_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM appointments
            {where_clause}
            GROUP BY YEAR(appointment_datetime), MONTH(appointment_datetime)
            ORDER BY year DESC, month DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Add month names
        for result in results:
            result['month_name'] = calendar.month_name[result['month']]
        
        return results
    
    def get_revenue_by_service(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get revenue grouped by service
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of services to return
        
        Returns:
            List of service revenue data
        """
        conditions = ["a.status = 'completed'"]
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions)
        
        # First get total revenue for percentage calculation
        total_query = f"""
            SELECT COALESCE(SUM(service_price), 0) as total
            FROM appointments a
            {where_clause}
        """
        total_result = self.db.execute_query(total_query, tuple(params) if params else None, fetch_one=True)
        total_revenue = total_result['total'] or Decimal('1')  # Avoid division by zero
        
        query = f"""
            SELECT 
                a.service_id,
                s.name as service_name,
                s.category,
                COALESCE(SUM(a.service_price), 0) as total_revenue,
                COUNT(*) as booking_count,
                COALESCE(AVG(a.service_price), 0) as average_price
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            {where_clause}
            GROUP BY a.service_id, s.name, s.category
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Calculate percentage
        for result in results:
            result['percentage_of_total'] = round(
                float(result['total_revenue'] / total_revenue * 100), 2
            )
        
        return results
    
    def get_revenue_by_staff(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get revenue grouped by staff member
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of staff to return
        
        Returns:
            List of staff revenue data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # First get total revenue for percentage calculation
        total_query = f"""
            SELECT COALESCE(SUM(CASE WHEN status = 'completed' THEN service_price ELSE 0 END), 0) as total
            FROM appointments a
            {where_clause}
        """
        total_result = self.db.execute_query(total_query, tuple(params) if params else None, fetch_one=True)
        total_revenue = total_result['total'] or Decimal('1')
        
        query = f"""
            SELECT 
                a.staff_id,
                u.full_name as staff_name,
                st.position,
                COALESCE(SUM(CASE WHEN a.status = 'completed' THEN a.service_price ELSE 0 END), 0) as total_revenue,
                COUNT(*) as booking_count,
                SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM appointments a
            LEFT JOIN staff st ON a.staff_id = st.id
            LEFT JOIN users u ON st.user_id = u.id
            {where_clause}
            GROUP BY a.staff_id, u.full_name, st.position
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Calculate percentage and average
        for result in results:
            result['percentage_of_total'] = round(
                float(result['total_revenue'] / total_revenue * 100), 2
            )
            completed = result['completed_count'] or 1
            result['average_revenue_per_booking'] = round(
                result['total_revenue'] / completed, 2
            )
        
        return results
    
    # ========================================================================
    # Service Analytics
    # ========================================================================
    
    def get_service_popularity(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get service popularity rankings
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of services to return
        
        Returns:
            List of service popularity data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                a.service_id,
                s.name as service_name,
                s.category,
                COUNT(*) as booking_count,
                SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN a.status = 'cancelled' THEN 1 ELSE 0 END) as cancellation_count
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            {where_clause}
            GROUP BY a.service_id, s.name, s.category
            ORDER BY booking_count DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Add rank and completion rate
        for i, result in enumerate(results, 1):
            result['rank'] = i
            total = result['booking_count'] or 1
            result['completion_rate'] = round(
                result['completed_count'] / total * 100, 2
            )
        
        return results
    
    def get_service_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get service performance metrics
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            List of service performance data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                a.service_id,
                s.name as service_name,
                s.category,
                COALESCE(SUM(CASE WHEN a.status = 'completed' THEN a.service_price ELSE 0 END), 0) as total_revenue,
                COUNT(*) as booking_count,
                COALESCE(AVG(a.service_price), 0) as average_price,
                COALESCE(AVG(a.duration_minutes), 0) as average_duration,
                SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_count
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            {where_clause}
            GROUP BY a.service_id, s.name, s.category
            ORDER BY total_revenue DESC
        """
        
        results = self.db.execute_query(query, tuple(params) if params else None)
        
        # Add completion rate
        for result in results:
            total = result['booking_count'] or 1
            result['completion_rate'] = round(
                result['completed_count'] / total * 100, 2
            )
            result['average_duration'] = int(result['average_duration'])
            del result['completed_count']  # Remove intermediate field
        
        return results
    
    # ========================================================================
    # Staff Analytics
    # ========================================================================
    
    def get_staff_performance(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get staff performance metrics
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of staff to return
        
        Returns:
            List of staff performance data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                a.staff_id,
                u.full_name as staff_name,
                st.position,
                COUNT(*) as total_appointments,
                SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_appointments,
                SUM(CASE WHEN a.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_appointments,
                SUM(CASE WHEN a.status = 'no-show' THEN 1 ELSE 0 END) as no_show_appointments,
                COALESCE(SUM(CASE WHEN a.status = 'completed' THEN a.service_price ELSE 0 END), 0) as total_revenue
            FROM appointments a
            LEFT JOIN staff st ON a.staff_id = st.id
            LEFT JOIN users u ON st.user_id = u.id
            {where_clause}
            GROUP BY a.staff_id, u.full_name, st.position
            ORDER BY total_revenue DESC
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Calculate rates
        for result in results:
            total = result['total_appointments'] or 1
            completed = result['completed_appointments'] or 1
            result['completion_rate'] = round(
                result['completed_appointments'] / total * 100, 2
            )
            result['average_revenue_per_appointment'] = round(
                result['total_revenue'] / completed, 2
            )
        
        return results
    
    def get_staff_stats(self, staff_id: int) -> Optional[Dict]:
        """
        Get detailed statistics for a specific staff member
        
        Args:
            staff_id: Staff ID
        
        Returns:
            Staff statistics dictionary or None
        """
        # Get basic stats
        query = """
            SELECT 
                a.staff_id,
                u.full_name as staff_name,
                st.position,
                COUNT(*) as total_appointments,
                SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_appointments,
                SUM(CASE WHEN a.status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_appointments,
                SUM(CASE WHEN a.status = 'no-show' THEN 1 ELSE 0 END) as no_show_appointments,
                SUM(CASE WHEN a.status = 'pending' THEN 1 ELSE 0 END) as pending_appointments,
                COALESCE(SUM(CASE WHEN a.status = 'completed' THEN a.service_price ELSE 0 END), 0) as total_revenue
            FROM appointments a
            LEFT JOIN staff st ON a.staff_id = st.id
            LEFT JOIN users u ON st.user_id = u.id
            WHERE a.staff_id = %s
            GROUP BY a.staff_id, u.full_name, st.position
        """
        
        result = self.db.execute_query(query, (staff_id,), fetch_one=True)
        
        if not result:
            return None
        
        # Get top services for this staff
        top_services_query = """
            SELECT 
                s.name as service_name,
                COUNT(*) as count
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
            WHERE a.staff_id = %s
            GROUP BY a.service_id, s.name
            ORDER BY count DESC
            LIMIT 5
        """
        top_services = self.db.execute_query(top_services_query, (staff_id,))
        result['top_services'] = top_services
        
        # Get busiest day
        busiest_day_query = """
            SELECT 
                DAYNAME(appointment_datetime) as day_name,
                COUNT(*) as count
            FROM appointments
            WHERE staff_id = %s
            GROUP BY DAYNAME(appointment_datetime)
            ORDER BY count DESC
            LIMIT 1
        """
        busiest_day = self.db.execute_query(busiest_day_query, (staff_id,), fetch_one=True)
        result['busiest_day'] = busiest_day['day_name'] if busiest_day else None
        
        # Get busiest hour
        busiest_hour_query = """
            SELECT 
                HOUR(appointment_datetime) as hour,
                COUNT(*) as count
            FROM appointments
            WHERE staff_id = %s
            GROUP BY HOUR(appointment_datetime)
            ORDER BY count DESC
            LIMIT 1
        """
        busiest_hour = self.db.execute_query(busiest_hour_query, (staff_id,), fetch_one=True)
        result['busiest_hour'] = busiest_hour['hour'] if busiest_hour else None
        
        result['average_rating'] = None  # Placeholder if ratings are added
        
        return result
    
    # ========================================================================
    # Appointment Analytics
    # ========================================================================
    
    def get_appointment_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get appointment status summary
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            Appointment summary dictionary
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                COUNT(*) as total_appointments,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                SUM(CASE WHEN status = 'no-show' THEN 1 ELSE 0 END) as no_show
            FROM appointments
            {where_clause}
        """
        
        result = self.db.execute_query(query, tuple(params) if params else None, fetch_one=True)
        
        total = result['total_appointments'] or 1
        
        result['completion_rate'] = round(result['completed'] / total * 100, 2)
        result['cancellation_rate'] = round(result['cancelled'] / total * 100, 2)
        result['no_show_rate'] = round(result['no_show'] / total * 100, 2)
        
        return result
    
    def get_booking_trends(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30
    ) -> List[Dict]:
        """
        Get booking trends over time
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of days to return
        
        Returns:
            List of booking trend data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT 
                DATE(appointment_datetime) as date,
                COUNT(*) as booking_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count
            FROM appointments
            {where_clause}
            GROUP BY DATE(appointment_datetime)
            ORDER BY date DESC
            LIMIT %s
        """
        
        params.append(limit)
        return self.db.execute_query(query, tuple(params))
    
    def get_peak_hours(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get peak booking hours
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            List of peak hour data
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("DATE(appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Get total for percentage
        total_query = f"SELECT COUNT(*) as total FROM appointments {where_clause}"
        total_result = self.db.execute_query(total_query, tuple(params) if params else None, fetch_one=True)
        total = total_result['total'] or 1
        
        query = f"""
            SELECT 
                HOUR(appointment_datetime) as hour,
                COUNT(*) as booking_count
            FROM appointments
            {where_clause}
            GROUP BY HOUR(appointment_datetime)
            ORDER BY booking_count DESC
        """
        
        results = self.db.execute_query(query, tuple(params) if params else None)
        
        # Add hour label and percentage
        for result in results:
            hour = result['hour']
            result['hour_label'] = f"{hour:02d}:00 - {hour:02d}:59"
            result['percentage'] = round(result['booking_count'] / total * 100, 2)
        
        return results
    
    # ========================================================================
    # Customer Analytics
    # ========================================================================
    
    def get_top_customers(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
        sort_by: str = "spending"  # "spending" or "visits"
    ) -> List[Dict]:
        """
        Get top customers by spending or visits
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            limit: Number of customers to return
            sort_by: Sort by 'spending' or 'visits'
        
        Returns:
            List of top customer data
        """
        conditions = ["a.status = 'completed'"]
        params = []
        
        if start_date:
            conditions.append("DATE(a.appointment_datetime) >= %s")
            params.append(start_date)
        
        if end_date:
            conditions.append("DATE(a.appointment_datetime) <= %s")
            params.append(end_date)
        
        where_clause = "WHERE " + " AND ".join(conditions)
        
        order_by = "total_spent DESC" if sort_by == "spending" else "visit_count DESC"
        
        query = f"""
            SELECT 
                a.user_id,
                u.full_name as customer_name,
                u.email,
                COALESCE(SUM(a.service_price), 0) as total_spent,
                COUNT(*) as visit_count,
                MAX(a.appointment_datetime) as last_visit
            FROM appointments a
            LEFT JOIN users u ON a.user_id = u.id
            {where_clause}
            GROUP BY a.user_id, u.full_name, u.email
            ORDER BY {order_by}
            LIMIT %s
        """
        
        params.append(limit)
        results = self.db.execute_query(query, tuple(params))
        
        # Add rank and average
        for i, result in enumerate(results, 1):
            result['rank'] = i
            visits = result['visit_count'] or 1
            result['average_spent_per_visit'] = round(
                result['total_spent'] / visits, 2
            )
        
        return results
    
    def get_customer_retention(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get customer retention metrics
        
        Args:
            start_date: Start date filter
            end_date: End date filter
        
        Returns:
            Customer retention dictionary
        """
        # Total unique customers
        total_query = """
            SELECT COUNT(DISTINCT user_id) as total_customers
            FROM appointments
            WHERE status = 'completed'
        """
        total_result = self.db.execute_query(total_query, fetch_one=True)
        total_customers = total_result['total_customers'] or 0
        
        # New customers this month
        current_month_start = date.today().replace(day=1)
        new_query = """
            SELECT COUNT(DISTINCT a.user_id) as new_customers
            FROM appointments a
            WHERE a.status = 'completed'
            AND a.user_id NOT IN (
                SELECT DISTINCT user_id 
                FROM appointments 
                WHERE status = 'completed' 
                AND DATE(appointment_datetime) < %s
            )
            AND DATE(a.appointment_datetime) >= %s
        """
        new_result = self.db.execute_query(new_query, (current_month_start, current_month_start), fetch_one=True)
        new_customers = new_result['new_customers'] or 0
        
        # Returning customers (more than 1 visit)
        returning_query = """
            SELECT COUNT(*) as returning_customers
            FROM (
                SELECT user_id, COUNT(*) as visit_count
                FROM appointments
                WHERE status = 'completed'
                GROUP BY user_id
                HAVING visit_count > 1
            ) as returning
        """
        returning_result = self.db.execute_query(returning_query, fetch_one=True)
        returning_customers = returning_result['returning_customers'] or 0
        
        # Average visits per customer
        avg_visits_query = """
            SELECT AVG(visit_count) as avg_visits
            FROM (
                SELECT user_id, COUNT(*) as visit_count
                FROM appointments
                WHERE status = 'completed'
                GROUP BY user_id
            ) as visits
        """
        avg_result = self.db.execute_query(avg_visits_query, fetch_one=True)
        avg_visits = avg_result['avg_visits'] or 0
        
        # Average lifetime value
        ltv_query = """
            SELECT AVG(total_spent) as avg_ltv
            FROM (
                SELECT user_id, SUM(service_price) as total_spent
                FROM appointments
                WHERE status = 'completed'
                GROUP BY user_id
            ) as ltv
        """
        ltv_result = self.db.execute_query(ltv_query, fetch_one=True)
        avg_ltv = ltv_result['avg_ltv'] or Decimal('0')
        
        retention_rate = round(returning_customers / total_customers * 100, 2) if total_customers > 0 else 0
        
        return {
            "total_customers": total_customers,
            "new_customers_this_month": new_customers,
            "returning_customers": returning_customers,
            "retention_rate": retention_rate,
            "average_visits_per_customer": round(float(avg_visits), 2),
            "average_lifetime_value": round(avg_ltv, 2)
        }
    
    # ========================================================================
    # Dashboard
    # ========================================================================
    
    def get_dashboard_data(self) -> Dict:
        """
        Get combined dashboard data for overview
        
        Returns:
            Dashboard data dictionary
        """
        # Get data for last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        return {
            "revenue_summary": self.get_revenue_summary(start_date, end_date),
            "appointment_summary": self.get_appointment_summary(start_date, end_date),
            "top_services": self.get_service_popularity(start_date, end_date, limit=5),
            "top_staff": self.get_staff_performance(start_date, end_date, limit=5),
            "recent_revenue": self.get_daily_revenue(start_date, end_date, limit=7)
        }