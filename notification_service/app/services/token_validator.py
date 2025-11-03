import pyodbc
import jwt
from datetime import datetime, timezone
from fastapi import HTTPException, status, Request
from app.config import settings

def get_db_connection():
    return pyodbc.connect(settings.DATABASE_URL)

def validate_token(request: Request):
    """
    Validate the access token from Authorization header.
    Confirms that user has an active session (refresh_token) in the DB.
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")

        token = auth_header.split(" ")[1]

        # Decode JWT
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        # Check session table
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT refresh_token, expires_at FROM dbo.session WHERE user_id = ?
        """, (user_id,))
        session = cursor.fetchone()

        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session found")

        refresh_token, expires_at = session

        # Check expiry
        if expires_at and datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

        # Token is valid
        return {"user_id": user_id, "refresh_token": refresh_token}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        try:
            conn.close()
        except:
            pass

