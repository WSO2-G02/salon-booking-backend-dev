"""
User Service Business Logic Layer
Handles all user-related operations
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import logging
import mysql.connector

from app.database import DatabaseManager
from app.auth import password_hasher, jwt_manager
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class UserService:
    """Service class for user operations"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    # ========================================================================
    # Authentication Methods
    # ========================================================================
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict:
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            full_name: User's full name
            phone: User's phone number
        
        Returns:
            Dictionary with user details (excluding password)
        
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        existing = self.db.execute_query(check_query, (username, email), fetch_one=True)
        
        if existing:
            raise ValueError("Username or email already exists")
        
        # Hash password
        password_hash = password_hasher.hash_password(password)
        
        # Insert new user
        insert_query = """
            INSERT INTO users (username, email, password_hash, full_name, phone, user_type)
            VALUES (%s, %s, %s, %s, %s, 'user')
        """
        
        try:
            user_id = self.db.execute_update(
                insert_query,
                (username, email, password_hash, full_name, phone)
            )
            
            # Fetch and return created user
            return self.get_user_by_id(user_id)
        
        except mysql.connector.IntegrityError as e:
            logger.error(f"Database integrity error during registration: {e}")
            raise ValueError("Username or email already exists")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user with username and password
        
        Args:
            username: User's username
            password: Plain text password
        
        Returns:
            User dictionary if authenticated, None otherwise
        """
        query = """
            SELECT id, username, email, password_hash, full_name, phone, 
                   user_type, is_active
            FROM users
            WHERE username = %s AND is_active = 1
        """
        
        user = self.db.execute_query(query, (username,), fetch_one=True)
        
        if not user:
            return None
        
        # Verify password
        if not password_hasher.verify_password(password, user['password_hash']):
            return None
        
        # Remove password hash from returned data
        del user['password_hash']
        return user
    
    def create_session(self, user_id: int, refresh_token: str) -> int:
        """
        Create a new session for a user
        
        Args:
            user_id: User's ID
            refresh_token: Refresh token to store
        
        Returns:
            Session ID
        """
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        insert_query = """
            INSERT INTO sessions (user_id, refresh_token, expires_at)
            VALUES (%s, %s, %s)
        """
        
        session_id = self.db.execute_update(
            insert_query,
            (user_id, refresh_token, expires_at)
        )
        
        return session_id
    
    def validate_refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Validate a refresh token and return associated user
        
        Args:
            refresh_token: Refresh token to validate
        
        Returns:
            User dictionary if valid, None otherwise
        """
        # Decode JWT token
        payload = jwt_manager.decode_token(refresh_token)
        if not payload or not jwt_manager.verify_token_type(payload, "refresh"):
            return None
        
        # Check if token exists in database and is not expired
        query = """
            SELECT s.user_id, u.username, u.email, u.user_type, u.is_active
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.refresh_token = %s 
              AND s.expires_at > NOW()
              AND u.is_active = 1
        """
        
        user = self.db.execute_query(query, (refresh_token,), fetch_one=True)
        return user
    
    def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token
        
        Args:
            refresh_token: Refresh token to invalidate
        
        Returns:
            True if successful, False otherwise
        """
        delete_query = "DELETE FROM sessions WHERE refresh_token = %s"
        affected_rows = self.db.execute_update(delete_query, (refresh_token,))
        return affected_rows > 0
    
    # ========================================================================
    # User Profile Methods
    # ========================================================================
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID
        
        Args:
            user_id: User's ID
        
        Returns:
            User dictionary (excluding password) or None
        """
        query = """
            SELECT id, username, email, full_name, phone, user_type, 
                   is_active, created_at, updated_at
            FROM users
            WHERE id = %s
        """
        
        return self.db.execute_query(query, (user_id,), fetch_one=True)
    
    def update_user_profile(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict:
        """
        Update user profile information
        
        Args:
            user_id: User's ID
            full_name: New full name
            phone: New phone number
            email: New email address
        
        Returns:
            Updated user dictionary
        
        Raises:
            ValueError: If email already exists for another user
        """
        # Build dynamic update query
        update_fields = []
        params = []
        
        if full_name is not None:
            update_fields.append("full_name = %s")
            params.append(full_name)
        
        if phone is not None:
            update_fields.append("phone = %s")
            params.append(phone)
        
        if email is not None:
            # Check if email is taken by another user
            check_query = "SELECT id FROM users WHERE email = %s AND id != %s"
            existing = self.db.execute_query(check_query, (email, user_id), fetch_one=True)
            if existing:
                raise ValueError("Email already exists")
            
            update_fields.append("email = %s")
            params.append(email)
        
        if not update_fields:
            # Nothing to update
            return self.get_user_by_id(user_id)
        
        params.append(user_id)
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        self.db.execute_update(update_query, tuple(params))
        
        return self.get_user_by_id(user_id)
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User's ID
            current_password: Current password for verification
            new_password: New password to set
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If current password is incorrect
        """
        # Get current password hash
        query = "SELECT password_hash FROM users WHERE id = %s"
        user = self.db.execute_query(query, (user_id,), fetch_one=True)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not password_hasher.verify_password(current_password, user['password_hash']):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = password_hasher.hash_password(new_password)
        
        # Update password
        update_query = "UPDATE users SET password_hash = %s WHERE id = %s"
        self.db.execute_update(update_query, (new_password_hash, user_id))
        
        return True
    
    # ========================================================================
    # Admin Methods
    # ========================================================================
    
    def create_user_as_admin(
        self,
        username: str,
        email: str,
        password: str,
        user_type: str = 'user',
        full_name: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Dict:
        """
        Create a new user (admin function, can set user_type)
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            user_type: 'user' or 'admin'
            full_name: User's full name
            phone: User's phone number
        
        Returns:
            Dictionary with user details
        
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        check_query = "SELECT id FROM users WHERE username = %s OR email = %s"
        existing = self.db.execute_query(check_query, (username, email), fetch_one=True)
        
        if existing:
            raise ValueError("Username or email already exists")
        
        # Hash password
        password_hash = password_hasher.hash_password(password)
        
        # Insert new user
        insert_query = """
            INSERT INTO users (username, email, password_hash, full_name, phone, user_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            user_id = self.db.execute_update(
                insert_query,
                (username, email, password_hash, full_name, phone, user_type)
            )
            
            return self.get_user_by_id(user_id)
        
        except mysql.connector.IntegrityError:
            raise ValueError("Username or email already exists")
    
    def get_all_users(self, page: int = 1, limit: int = 10) -> Tuple[List[Dict], int]:
        """
        Get paginated list of all users
        
        Args:
            page: Page number (1-indexed)
            limit: Number of users per page
        
        Returns:
            Tuple of (user list, total count)
        """
        offset = (page - 1) * limit
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM users"
        count_result = self.db.execute_query(count_query, fetch_one=True)
        total = count_result['total']
        
        # Get paginated users
        query = """
            SELECT id, username, email, full_name, user_type, is_active, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        users = self.db.execute_query(query, (limit, offset))
        
        return users, total
    
    def clean_expired_sessions(self) -> int:
        """
        Clean up expired refresh tokens from database
        Should be called periodically
        
        Returns:
            Number of sessions deleted
        """
        delete_query = "DELETE FROM sessions WHERE expires_at < NOW()"
        return self.db.execute_update(delete_query)