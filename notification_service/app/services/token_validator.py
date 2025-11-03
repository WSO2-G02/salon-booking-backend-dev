import pyodbc
import jwt
import requests
from datetime import datetime, timezone
from fastapi import HTTPException, status, Request
from app.config import settings
from app.database import get_db_connection

def validate_access_token(token: str) -> int:
    """
    Validate the access token using JWT.
    Returns:
        user_id (int): extracted from token payload
    Raises:
        HTTPException: if token is expired or invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def refresh_access_token(user_id: int):
    """
    (Future use) Refresh the access token using User Service.
    Called only when the access token is expired.

    This is a stub for now — the User Service should expose:
        POST /api/v1/auth/refresh { "refresh_token": "<token>" }
    """
    USER_SERVICE_URL = "http://user-service:8000/api/v1/auth/refresh"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT refresh_token, expires_at FROM dbo.sessions WHERE user_id = ?",
        (user_id,)
    )
    session = cursor.fetchone()
    conn.close()

    if not session:
        raise HTTPException(status_code=401, detail="No refresh token found")

    refresh_token, expires_at = session

    # Handle timezone correctly
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Attempt refresh call (will only work once User Service is running)
    try:
        response = requests.post(USER_SERVICE_URL, json={"refresh_token": refresh_token})
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to refresh token via User Service"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {e}")


def validate_token(token: str) -> int:
    """
    Main validation entry point used by all endpoints.
    - Validates JWT access token
    - If expired, (future) tries refresh flow
    - Returns authenticated user_id
    """
    try:
        user_id = validate_access_token(token)
        return user_id

    except HTTPException as e:
        if e.detail == "Access token expired":
            # For now, just raise expired error.
            # When User Service is available, uncomment the next 2 lines:
            # new_token = refresh_access_token(user_id)
            # return validate_access_token(new_token)
            raise HTTPException(status_code=401, detail="Access token expired; refresh pending integration.")
        else:
            raise