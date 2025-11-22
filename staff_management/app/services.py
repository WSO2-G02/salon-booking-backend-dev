"""
Staff Service Business Logic Layer
Handles all staff-related operations
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date, time, timedelta
import logging
import mysql.connector
from app.notification_client import get_notification_client
import asyncio
from app.database import DatabaseManager

logger = logging.getLogger(__name__)


class StaffService:
    """Service class for staff operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ========================================================================
    # Staff Management Methods
    # ========================================================================
    
    def create_staff_member(
        self,
        user_id: int,
        employee_id: str,
        position: str,
        specialties: Optional[str] = None,
        experience_years: Optional[int] = None,
        hire_date: Optional[date] = None
    ) -> Dict:
        """
        Create a new staff member
        
        Args:
            user_id: Reference to user in user_db
            employee_id: Unique employee identifier
            position: Job position
            specialties: Comma-separated specialties
            experience_years: Years of experience
            hire_date: Date of hire
        
        Returns:
            Dictionary with staff details
        
        Raises:
            ValueError: If user_id or employee_id already exists
        """
        # Check if user_id already exists
        check_query = "SELECT id FROM staff WHERE user_id = %s OR employee_id = %s"
        existing = self.db.execute_query(check_query, (user_id, employee_id), fetch_one=True)
        
        if existing:
            raise ValueError("User ID or Employee ID already exists")
        
        # Insert new staff member
        insert_query = """
            INSERT INTO staff (user_id, employee_id, position, specialties, 
                             experience_years, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            # Insert the staff record
            staff_id = self.db.execute_update(
                insert_query,
                (user_id, employee_id, position, specialties, experience_years, hire_date)
            )
            
            # --- START: Send staff welcome email notification ---
            try:
                # Get the notification client instance
                notification = get_notification_client()
                
                # Get user email and name from the linked 'users' table using user_id
                user_query = "SELECT email, full_name, username FROM users WHERE id = %s"
                user = self.db.execute_query(user_query, (user_id,), fetch_one=True)
                
                if user and user.get('email'):
                    # Create an asynchronous task to send the welcome email
                    asyncio.create_task(
                        notification.send_create_staff_email(
                            email=user['email'],
                            full_name=user.get('full_name'), # Use .get() for safety
                            position=position,
                            username=user.get('username'), # Use .get() for safety
                            token=None  # Called internally, no token needed
                        )
                    )
            except Exception as e:
                # Log a warning if the email sending fails, but don't stop the function
                logger.warning(f"Failed to send staff welcome email: {e}")
            # --- END: Send staff welcome email notification ---
            
            # Fetch and return the newly created staff member details
            return self.get_staff_by_id(staff_id)
        
        except mysql.connector.IntegrityError:
            # Catch potential duplicate keys that slipped past the initial check
            raise ValueError("User ID or Employee ID already exists")
    
    def get_staff_by_id(self, staff_id: int) -> Optional[Dict]:
        """
        Get staff member by internal ID
        
        Args:
            staff_id: Internal staff ID
        
        Returns:
            Staff dictionary or None
        """
        query = """
            SELECT id, user_id, employee_id, position, specialties, 
                   experience_years, hire_date, is_active, created_at, updated_at
            FROM staff
            WHERE id = %s
        """
        
        return self.db.execute_query(query, (staff_id,), fetch_one=True)
    
    def get_staff_by_user_id(self, user_id: int) -> Optional[Dict]:
        """
        Get staff member by user_id
        
        Args:
            user_id: User ID from user service
        
        Returns:
            Staff dictionary or None
        """
        query = """
            SELECT id, user_id, employee_id, position, specialties, 
                   experience_years, hire_date, is_active, created_at, updated_at
            FROM staff
            WHERE user_id = %s
        """
        
        return self.db.execute_query(query, (user_id,), fetch_one=True)
    
    def get_staff_by_employee_id(self, employee_id: str) -> Optional[Dict]:
        """
        Get staff member by employee_id
        
        Args:
            employee_id: Employee identifier
        
        Returns:
            Staff dictionary or None
        """
        query = """
            SELECT id, user_id, employee_id, position, specialties, 
                   experience_years, hire_date, is_active, created_at, updated_at
            FROM staff
            WHERE employee_id = %s
        """
        
        return self.db.execute_query(query, (employee_id,), fetch_one=True)
    
    def get_all_staff(
        self,
        page: int = 1,
        limit: int = 10,
        active_only: bool = True,
        position: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """
        Get paginated list of all staff members
        
        Args:
            page: Page number (1-indexed)
            limit: Number of staff per page
            active_only: Filter for active staff only
            position: Filter by position
        
        Returns:
            Tuple of (staff list, total count)
        """
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = []
        params = []
        
        if active_only:
            conditions.append("is_active = 1")
        
        if position:
            conditions.append("position = %s")
            params.append(position)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM staff {where_clause}"
        count_result = self.db.execute_query(count_query, tuple(params), fetch_one=True)
        total = count_result['total']
        
        # Get paginated staff
        query = f"""
            SELECT id, user_id, employee_id, position, specialties, 
                   experience_years, hire_date, is_active, created_at, updated_at
            FROM staff
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        staff_list = self.db.execute_query(query, tuple(params))
        
        return staff_list, total
    
    def update_staff_member(
        self,
        staff_id: int,
        position: Optional[str] = None,
        specialties: Optional[str] = None,
        experience_years: Optional[int] = None,
        hire_date: Optional[date] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict]:
        """
        Update staff member information
        
        Args:
            staff_id: Internal staff ID
            position: New position
            specialties: New specialties
            experience_years: New experience years
            hire_date: New hire date
            is_active: New active status
        
        Returns:
            Updated staff dictionary or None
        """
        # Build dynamic update query
        update_fields = []
        params = []
        
        if position is not None:
            update_fields.append("position = %s")
            params.append(position)
        
        if specialties is not None:
            update_fields.append("specialties = %s")
            params.append(specialties)
        
        if experience_years is not None:
            update_fields.append("experience_years = %s")
            params.append(experience_years)
        
        if hire_date is not None:
            update_fields.append("hire_date = %s")
            params.append(hire_date)
        
        if is_active is not None:
            update_fields.append("is_active = %s")
            params.append(1 if is_active else 0)
        
        if not update_fields:
            # Nothing to update
            return self.get_staff_by_id(staff_id)
        
        params.append(staff_id)
        update_query = f"UPDATE staff SET {', '.join(update_fields)} WHERE id = %s"
        
        self.db.execute_update(update_query, tuple(params))
        
        return self.get_staff_by_id(staff_id)
    
    def delete_staff_member(self, staff_id: int) -> bool:
        """
        Delete staff member (soft delete by setting is_active = 0)
        
        Args:
            staff_id: Internal staff ID
        
        Returns:
            True if successful, False if not found
        """
        query = "UPDATE staff SET is_active = 0 WHERE id = %s"
        affected_rows = self.db.execute_update(query, (staff_id,))
        return affected_rows > 0
    
    def get_staff_by_specialty(self, specialty: str) -> List[Dict]:
        """
        Get staff members by specialty
        
        Args:
            specialty: Specialty to search for
        
        Returns:
            List of staff dictionaries
        """
        query = """
            SELECT id, user_id, employee_id, position, specialties, 
                   experience_years, hire_date, is_active, created_at, updated_at
            FROM staff
            WHERE specialties LIKE %s AND is_active = 1
        """
        
        return self.db.execute_query(query, (f"%{specialty}%",))
    
    # ========================================================================
    # Staff Availability Methods
    # ========================================================================
    
    def create_availability(
        self,
        staff_id: int,
        slot_date: date,
        start_time: time,
        end_time: time,
        availability_type: str = "work"
    ) -> Dict:
        """
        Create a new availability slot for a staff member
        
        Args:
            staff_id: Internal staff ID
            slot_date: Date of availability
            start_time: Start time
            end_time: End time
            availability_type: Type of availability (work, break, unavailable)
        
        Returns:
            Created availability dictionary
        """
        insert_query = """
            INSERT INTO staff_availability (staff_id, slot_date, start_time, end_time, availability_type)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        availability_id = self.db.execute_update(
            insert_query,
            (staff_id, slot_date, start_time, end_time, availability_type)
        )
        
        return self.get_availability_by_id(availability_id)
    
    def get_availability_by_id(self, availability_id: int) -> Optional[Dict]:
        """Get availability slot by ID"""
        query = """
            SELECT id, staff_id, slot_date, start_time, end_time, availability_type
            FROM staff_availability
            WHERE id = %s
        """
        
        result = self.db.execute_query(query, (availability_id,), fetch_one=True)
        
        if result:
            # Convert timedelta to time objects
            from datetime import time as dt_time, timedelta
            if isinstance(result['start_time'], timedelta):
                total_seconds = int(result['start_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                result['start_time'] = dt_time(hours, minutes, seconds)
            
            if isinstance(result['end_time'], timedelta):
                total_seconds = int(result['end_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                result['end_time'] = dt_time(hours, minutes, seconds)
        
        return result
    
    def get_staff_availability(
        self,
        staff_id: int,
        slot_date: date
    ) -> List[Dict]:
        """
        Get all availability slots for a staff member on a specific date
        
        Args:
            staff_id: Internal staff ID
            slot_date: Date to check
        
        Returns:
            List of availability dictionaries
        """
        query = """
            SELECT id, staff_id, slot_date, start_time, end_time, availability_type
            FROM staff_availability
            WHERE staff_id = %s AND slot_date = %s
            ORDER BY start_time
        """
        
        results = self.db.execute_query(query, (staff_id, slot_date))
        
        # Convert timedelta to time objects
        from datetime import time as dt_time, timedelta
        for result in results:
            if isinstance(result['start_time'], timedelta):
                total_seconds = int(result['start_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                result['start_time'] = dt_time(hours, minutes, seconds)
            
            if isinstance(result['end_time'], timedelta):
                total_seconds = int(result['end_time'].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                result['end_time'] = dt_time(hours, minutes, seconds)
        
        return results
    
    def calculate_available_time_slots(
        self,
        staff_id: int,
        slot_date: date,
        service_duration_minutes: int = 60
    ) -> Dict:
        """
        Calculate available booking slots for a staff member
        
        Args:
            staff_id: Internal staff ID
            slot_date: Date to check
            service_duration_minutes: Duration of service in minutes
        
        Returns:
            Dictionary with available slots and total minutes
        """
        availability_slots = self.get_staff_availability(staff_id, slot_date)
        
        if not availability_slots:
            return {
                "staff_id": staff_id,
                "slot_date": slot_date,
                "available_slots": [],
                "total_available_minutes": 0
            }
        
        available_slots = []
        total_minutes = 0
        
        for availability in availability_slots:
            if availability['availability_type'] != 'work':
                continue  # Skip breaks and unavailable slots
            
            start_dt = datetime.combine(slot_date, availability['start_time'])
            end_dt = datetime.combine(slot_date, availability['end_time'])
            current = start_dt
            
            # Generate 30-minute increment slots
            while current + timedelta(minutes=service_duration_minutes) <= end_dt:
                slot_end = current + timedelta(minutes=service_duration_minutes)
                
                available_slots.append({
                    "start_time": current.time(),
                    "end_time": slot_end.time(),
                    "duration_minutes": service_duration_minutes
                })
                total_minutes += service_duration_minutes
                
                current += timedelta(minutes=30)
        
        return {
            "staff_id": staff_id,
            "slot_date": slot_date,
            "available_slots": available_slots,
            "total_available_minutes": total_minutes
        }