"""
Service Management Business Logic Layer
Handles all salon service-related operations
"""
from typing import Optional, Dict, List, Tuple
from decimal import Decimal
import logging
import mysql.connector

from app.database import DatabaseManager

logger = logging.getLogger(__name__)


class ServiceManagementService:
    """Service class for salon service operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ========================================================================
    # Service CRUD Methods
    # ========================================================================
    
    def create_service(
        self,
        name: str,
        price: Decimal,
        duration_minutes: int,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Create a new salon service
        
        Args:
            name: Service name
            price: Service price
            duration_minutes: Duration in minutes
            description: Service description
            category: Service category
        
        Returns:
            Dictionary with service details
        
        Raises:
            ValueError: If service name already exists
        """
        # Check if service name already exists
        check_query = "SELECT id FROM services WHERE name = %s"
        existing = self.db.execute_query(check_query, (name,), fetch_one=True)
        
        if existing:
            raise ValueError(f"Service with name '{name}' already exists")
        
        # Insert new service
        insert_query = """
            INSERT INTO services (name, description, category, price, duration_minutes)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        try:
            service_id = self.db.execute_update(
                insert_query,
                (name, description, category, price, duration_minutes)
            )
            
            return self.get_service_by_id(service_id)
        
        except mysql.connector.IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise ValueError(f"Service with name '{name}' already exists")
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict]:
        """
        Get service by ID
        
        Args:
            service_id: Service ID
        
        Returns:
            Service dictionary or None
        """
        query = """
            SELECT id, name, description, category, price, duration_minutes,
                   is_active, created_at, updated_at
            FROM services
            WHERE id = %s
        """
        
        return self.db.execute_query(query, (service_id,), fetch_one=True)
    
    def get_all_services(
        self,
        active_only: bool = False,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all services with optional filters
        
        Args:
            active_only: Filter for active services only
            category: Filter by category
        
        Returns:
            List of service dictionaries
        """
        # Build query conditions
        conditions = []
        params = []
        
        if active_only:
            conditions.append("is_active = 1")
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
            SELECT id, name, description, category, price, duration_minutes,
                   is_active, created_at, updated_at
            FROM services
            {where_clause}
            ORDER BY category, name
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def update_service(
        self,
        service_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        price: Optional[Decimal] = None,
        duration_minutes: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict]:
        """
        Update service information
        
        Args:
            service_id: Service ID
            name: New name
            description: New description
            category: New category
            price: New price
            duration_minutes: New duration
            is_active: New active status
        
        Returns:
            Updated service dictionary or None if not found
        """
        # Check if service exists
        existing = self.get_service_by_id(service_id)
        if not existing:
            return None
        
        # Check if new name conflicts with another service
        if name and name != existing['name']:
            check_query = "SELECT id FROM services WHERE name = %s AND id != %s"
            conflict = self.db.execute_query(check_query, (name, service_id), fetch_one=True)
            if conflict:
                raise ValueError(f"Service with name '{name}' already exists")
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = %s")
            params.append(name)
        
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        
        if category is not None:
            update_fields.append("category = %s")
            params.append(category)
        
        if price is not None:
            update_fields.append("price = %s")
            params.append(price)
        
        if duration_minutes is not None:
            update_fields.append("duration_minutes = %s")
            params.append(duration_minutes)
        
        if is_active is not None:
            update_fields.append("is_active = %s")
            params.append(1 if is_active else 0)
        
        if not update_fields:
            # Nothing to update
            return existing
        
        params.append(service_id)
        update_query = f"UPDATE services SET {', '.join(update_fields)} WHERE id = %s"
        
        self.db.execute_update(update_query, tuple(params))
        
        return self.get_service_by_id(service_id)
    
    def delete_service(self, service_id: int) -> bool:
        """
        Deactivate a service (soft delete)
        
        Args:
            service_id: Service ID
        
        Returns:
            True if successful, False if not found
        """
        query = "UPDATE services SET is_active = 0 WHERE id = %s"
        affected_rows = self.db.execute_update(query, (service_id,))
        return affected_rows > 0
    
    def get_services_by_category(self, category: str) -> List[Dict]:
        """
        Get all active services in a specific category
        
        Args:
            category: Category name
        
        Returns:
            List of service dictionaries
        """
        query = """
            SELECT id, name, description, category, price, duration_minutes,
                   is_active, created_at, updated_at
            FROM services
            WHERE category = %s AND is_active = 1
            ORDER BY name
        """
        
        return self.db.execute_query(query, (category,))
    
    def get_services_by_price_range(
        self,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ) -> List[Dict]:
        """
        Get services within a price range
        
        Args:
            min_price: Minimum price (optional)
            max_price: Maximum price (optional)
        
        Returns:
            List of service dictionaries
        """
        conditions = ["is_active = 1"]
        params = []
        
        if min_price is not None:
            conditions.append("price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= %s")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT id, name, description, category, price, duration_minutes,
                   is_active, created_at, updated_at
            FROM services
            WHERE {where_clause}
            ORDER BY price
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_categories(self) -> List[str]:
        """
        Get list of all unique categories
        
        Returns:
            List of category names
        """
        query = """
            SELECT DISTINCT category
            FROM services
            WHERE category IS NOT NULL AND is_active = 1
            ORDER BY category
        """
        
        results = self.db.execute_query(query)
        print(results)
        return [row['category'] for row in results if row['category']]