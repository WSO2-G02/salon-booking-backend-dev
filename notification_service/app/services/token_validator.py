from fastapi import Header, HTTPException, status
from app.database import get_db_connection

def validate_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    access_token = authorization.split(" ")[1]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, refresh_token FROM dbo.sessions WHERE access_token = ?", (access_token,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return {"user_id": row.user_id}
