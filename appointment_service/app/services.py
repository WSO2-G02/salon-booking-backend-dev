"""
Appointment Service Business Logic Layer
Handles all appointment-related operations
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import logging
import mysql.connector

from app.database import DatabaseManager

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service class for appointment operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ========================================================================
    # Appointment CRUD Methods
    # ========================================================================
    
    def create_appointment(
        self,
        user_id: int,
        staff_id: int,
        service_id: int,
        appointment_datetime: datetime,
        customer_notes: Optional[str] = None
    ) -> Dict:
        """
        Create a new appointment
        
        Args:
            user_id: Customer user ID
            staff_id: Staff member ID
            service_id: Service ID
            appointment_datetime: Date and time of appointment
            customer_notes: Customer notes
        
        Returns:
            Dictionary with appointment details
        
        Raises:
            ValueError: If validation fails
        """
        # Verify user exists
        user_query = "SELECT id FROM users WHERE id = %s AND is_active = 1"
        user = self.db.execute_query(user_query, (user_id,), fetch_one=True)
        if not user:
            raise ValueError("User not found or inactive")
        
        # Verify staff exists and is active
        staff_query = "SELECT id FROM staff WHERE id = %s AND is_active = 1"
        staff = self.db.execute_query(staff_query, (staff_id,), fetch_one=True)
        if not staff:
            raise ValueError("Staff member not found or inactive")
        
        # Verify service exists and get price and duration
        service_query = "SELECT id, price, duration_minutes FROM services WHERE id = %s AND is_active = 1"
        service = self.db.execute_query(service_query, (service_id,), fetch_one=True)
        if not service:
            raise ValueError("Service not found or inactive")
        
        service_price = service['price']
        duration_minutes = service['duration_minutes']
        
        # Check for conflicting appointments (same staff, overlapping time)
        # Check if there's an appointment within the service duration window
        conflict_query = """
            SELECT id FROM appointments
            WHERE staff_id = %s 
            AND appointment_datetime BETWEEN 
                DATE_SUB(%s, INTERVAL duration_minutes MINUTE) 
                AND DATE_ADD(%s, INTERVAL %s MINUTE)
            AND status NOT IN ('cancelled', 'no-show')
        """
        conflict = self.db.execute_query(
            conflict_query, 
            (staff_id, appointment_datetime, appointment_datetime, duration_minutes), 
            fetch_one=True
        )
        if conflict:
            raise ValueError("Staff member is not available at this time")
        
        # Insert new appointment
        insert_query = """
            INSERT INTO appointments 
            (user_id, staff_id, service_id, appointment_datetime, duration_minutes, service_price, customer_notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            appointment_id = self.db.execute_update(
                insert_query,
                (user_id, staff_id, service_id, appointment_datetime, duration_minutes, service_price, customer_notes)
            )
            
            return self.get_appointment_by_id(appointment_id)
        
        except mysql.connector.IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise ValueError("Failed to create appointment")
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict]:
        """
        Get appointment by ID
        
        Args:
            appointment_id: Appointment ID
        
        Returns:
            Appointment dictionary or None
        """
        query = """
            SELECT id, user_id, staff_id, service_id, appointment_datetime, 
                   duration_minutes, service_price, status, customer_notes, 
                   staff_notes, cancellation_reason, created_at, updated_at, completed_at
            FROM appointments
            WHERE id = %s
        """
        
        return self.db.execute_query(query, (appointment_id,), fetch_one=True)
    
    def get_appointment_details(self, appointment_id: int) -> Optional[Dict]:
        """
        Get detailed appointment information with related data
        
        Args:
            appointment_id: Appointment ID
        
        Returns:
            Detailed appointment dictionary or None
        """
        query = """
            SELECT 
                a.id, a.user_id, a.staff_id, a.service_id,
                a.appointment_datetime, a.duration_minutes, a.service_price, a.status, 
                a.customer_notes, a.staff_notes, a.cancellation_reason,
                a.created_at, a.updated_at, a.completed_at,
                u.full_name as user_name, u.email as user_email, u.phone as user_phone,
                s.position as staff_position,
                srv.name as service_name
            FROM appointments a
            LEFT JOIN users u ON a.user_id = u.id
            LEFT JOIN staff s ON a.staff_id = s.id
            LEFT JOIN services srv ON a.service_id = srv.id
            WHERE a.id = %s
        """
        
        result = self.db.execute_query(query, (appointment_id,), fetch_one=True)
        
        if result:
            # Get staff name from users table via staff.user_id
            if result.get('staff_id'):
                staff_query = """
                    SELECT u.full_name 
                    FROM staff s 
                    JOIN users u ON s.user_id = u.id 
                    WHERE s.id = %s
                """
                staff_info = self.db.execute_query(staff_query, (result['staff_id'],), fetch_one=True)
                result['staff_name'] = staff_info['full_name'] if staff_info else None
        
        return result
    
    def get_user_appointments(
        self,
        user_id: int,
        status: Optional[str] = None,
        from_datetime: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get all appointments for a specific user
        
        Args:
            user_id: User ID
            status: Filter by status (optional)
            from_datetime: Get appointments from this datetime onwards (optional)
        
        Returns:
            List of appointment dictionaries
        """
        conditions = ["user_id = %s"]
        params = [user_id]
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if from_datetime:
            conditions.append("appointment_datetime >= %s")
            params.append(from_datetime)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, user_id, staff_id, service_id, appointment_datetime, 
                   duration_minutes, service_price, status, customer_notes, 
                   staff_notes, cancellation_reason, created_at, updated_at, completed_at
            FROM appointments
            WHERE {where_clause}
            ORDER BY appointment_datetime DESC
        """
        
        return self.db.execute_query(query, tuple(params))
    
    def get_staff_appointments(
        self,
        staff_id: int,
        appointment_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all appointments for a specific staff member
        
        Args:
            staff_id: Staff ID
            appointment_date: Filter by specific date (optional)
            status: Filter by status (optional)
        
        Returns:
            List of appointment dictionaries
        """
        conditions = ["staff_id = %s"]
        params = [staff_id]
        
        if appointment_date:
            conditions.append("DATE(appointment_datetime) = %s")
            params.append(appointment_date)
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, user_id, staff_id, service_id, appointment_datetime, 
                   duration_minutes, service_price, status, customer_notes, 
                   staff_notes, cancellation_reason, created_at, updated_at, completed_at
            FROM appointments
            WHERE {where_clause}
            ORDER BY appointment_datetime
        """
        
        return self.db.execute_query(query, tuple(params))
    
    def get_all_appointments(
        self,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
        from_datetime: Optional[datetime] = None
    ) -> Tuple[List[Dict], int]:
        """
        Get paginated list of all appointments
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            status: Filter by status (optional)
            from_datetime: Get appointments from this datetime onwards (optional)
        
        Returns:
            Tuple of (appointment list, total count)
        """
        offset = (page - 1) * limit
        
        conditions = []
        params = []
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if from_datetime:
            conditions.append("appointment_datetime >= %s")
            params.append(from_datetime)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM appointments {where_clause}"
        count_result = self.db.execute_query(count_query, tuple(params) if params else None, fetch_one=True)
        total = count_result['total']
        
        # Get paginated appointments
        query = f"""
            SELECT id, user_id, staff_id, service_id, appointment_datetime, 
                   duration_minutes, service_price, status, customer_notes, 
                   staff_notes, cancellation_reason, created_at, updated_at, completed_at
            FROM appointments
            {where_clause}
            ORDER BY appointment_datetime DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        results = self.db.execute_query(query, tuple(params))
        
        return results, total
    
    def update_appointment(
        self,
        appointment_id: int,
        staff_id: Optional[int] = None,
        service_id: Optional[int] = None,
        appointment_datetime: Optional[datetime] = None,
        status: Optional[str] = None,
        customer_notes: Optional[str] = None,
        staff_notes: Optional[str] = None,
        cancellation_reason: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update an appointment
        
        Args:
            appointment_id: Appointment ID
            staff_id: New staff ID
            service_id: New service ID
            appointment_datetime: New datetime
            status: New status
            customer_notes: New customer notes
            staff_notes: New staff notes
            cancellation_reason: Cancellation reason
        
        Returns:
            Updated appointment dictionary or None if not found
        """
        # Check if appointment exists
        existing = self.get_appointment_by_id(appointment_id)
        if not existing:
            return None
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        if staff_id is not None:
            # Verify staff exists
            staff_query = "SELECT id FROM staff WHERE id = %s AND is_active = 1"
            staff = self.db.execute_query(staff_query, (staff_id,), fetch_one=True)
            if not staff:
                raise ValueError("Staff member not found or inactive")
            update_fields.append("staff_id = %s")
            params.append(staff_id)
        
        if service_id is not None:
            # Verify service exists and update price and duration
            service_query = "SELECT id, price, duration_minutes FROM services WHERE id = %s AND is_active = 1"
            service = self.db.execute_query(service_query, (service_id,), fetch_one=True)
            if not service:
                raise ValueError("Service not found or inactive")
            update_fields.append("service_id = %s")
            params.append(service_id)
            update_fields.append("service_price = %s")
            params.append(service['price'])
            update_fields.append("duration_minutes = %s")
            params.append(service['duration_minutes'])
        
        if appointment_datetime is not None:
            update_fields.append("appointment_datetime = %s")
            params.append(appointment_datetime)
        
        if status is not None:
            update_fields.append("status = %s")
            params.append(status)
            # If status is completed, set completed_at
            if status == 'completed':
                update_fields.append("completed_at = NOW()")
        
        if customer_notes is not None:
            update_fields.append("customer_notes = %s")
            params.append(customer_notes)
        
        if staff_notes is not None:
            update_fields.append("staff_notes = %s")
            params.append(staff_notes)
        
        if cancellation_reason is not None:
            update_fields.append("cancellation_reason = %s")
            params.append(cancellation_reason)
        
        if not update_fields:
            return existing
        
        params.append(appointment_id)
        update_query = f"UPDATE appointments SET {', '.join(update_fields)} WHERE id = %s"
        
        self.db.execute_update(update_query, tuple(params))
        
        return self.get_appointment_by_id(appointment_id)
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """
        Cancel an appointment
        
        Args:
            appointment_id: Appointment ID
        
        Returns:
            True if successful, False if not found
        """
        query = "UPDATE appointments SET status = 'cancelled' WHERE id = %s"
        affected_rows = self.db.execute_update(query, (appointment_id,))
        return affected_rows > 0
    
    def get_appointments_by_date(self, appointment_date: date) -> List[Dict]:
        """
        Get all appointments for a specific date
        
        Args:
            appointment_date: Date to query
        
        Returns:
            List of appointment dictionaries
        """
        query = """
            SELECT id, user_id, staff_id, service_id, appointment_datetime, 
                   duration_minutes, service_price, status, customer_notes, 
                   staff_notes, cancellation_reason, created_at, updated_at, completed_at
            FROM appointments
            WHERE DATE(appointment_datetime) = %s
            ORDER BY appointment_datetime
        """
        
        return self.db.execute_query(query, (appointment_date,))