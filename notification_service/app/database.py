"""
Database Connection Manager for MySQL
Handles connection pooling and database operations
Used for token validation
"""
import mysql.connector
from mysql.connector import errorcode, pooling
from typing import Optional
from contextlib import contextmanager
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MySQL database connections with connection pooling"""
    
    def __init__(self):
        self.pool: Optional[pooling.MySQLConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize MySQL connection pool"""
        try:
            dbconfig = {
                "host": settings.DB_HOST,
                "port": settings.DB_PORT,
                "database": settings.DB_NAME,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "raise_on_warnings": True,
                "autocommit": False,
            }
            
            self.pool = pooling.MySQLConnectionPool(
                pool_name="notification_service_pool",
                pool_size=5,
                pool_reset_session=True,
                **dbconfig
            )
            
            logger.info(f"Database ({settings.DB_NAME}) connection pool initialized successfully")
            
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Database access denied: Invalid credentials")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.error(f"Database '{settings.DB_NAME}' does not exist")
            else:
                logger.error(f"Database error: {err}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.pool.get_connection()
            yield connection
        except mysql.connector.Error as err:
            logger.error(f"Database connection error: {err}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    @contextmanager
    def get_cursor(self, dictionary=True):
        """Context manager for database cursor"""
        with self.get_connection() as connection:
            cursor = connection.cursor(dictionary=dictionary)
            try:
                yield cursor
                connection.commit()
            except mysql.connector.Error as err:
                connection.rollback()
                logger.error(f"Database operation error: {err}")
                raise
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """Execute a SELECT query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone() if fetch_one else cursor.fetchall()
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """Dependency injection for database manager"""
    return db_manager