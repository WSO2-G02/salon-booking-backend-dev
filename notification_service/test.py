import pyodbc

# replace with values you were given
DB_URL      = "testdb20251014.database.windows.net"       # can include port like host:1433 or host,1433
DB_NAME     = "test-db"
DB_USER     = "admin123"
DB_PASSWORD = "user@2025"


conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={DB_URL};"                # or "SERVER=tcp:your.db.host.com,1433;"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};PWD={DB_PASSWORD};"
    "Encrypt=yes;TrustServerCertificate=yes;"
)

print("Connecting...")
try:
    conn = pyodbc.connect(conn_str, timeout=5)
    print("✅ Connected successfully")
    cur = conn.cursor()
    cur.execute("SELECT DB_NAME()")
    print("Current DB:", cur.fetchone()[0])
    conn.close()
except Exception as e:
    print("❌ Error:", e)