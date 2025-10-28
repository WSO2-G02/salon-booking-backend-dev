import pyodbc
from app.config import settings

def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=testdb20251014.database.windows.net;"
        f"DATABASE=test-db;"
        f"UID=admin123;"
        f"PWD=user@2025;"
        "Encrypt=yes;TrustServerCertificate=no;"
    )
    return conn
