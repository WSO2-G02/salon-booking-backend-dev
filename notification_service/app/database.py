import pyodbc
from app.config import settings

def get_db_connection():
    try:
        conn = pyodbc.connect(settings.DATABASE_CONNECTION_STRING)
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        raise
