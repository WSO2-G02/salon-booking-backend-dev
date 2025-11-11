from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from common.database import get_db
from app import models  
import os


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

#custom authentication Error
class AuthenticationError(Exception):
    """Raised when any authentication or session validation fails."""
    pass



async def verify_access_token(token: str = Depends(oauth2_scheme)) -> str:

    #Validates the JWT access token and extracts `sub` (username).
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise AuthenticationError("Invalid access token. No subject found.")

        return username

    except JWTError:
        raise AuthenticationError("Access token is invalid or expired.")
    


async def verify_user_session(
    username: str = Depends(verify_access_token),
    db: AsyncSession = Depends(get_db)
) -> int:
    """
    Validates session (refresh token) of the authenticated user.
    Ensures user is still logged-in in the User Service.
    """

    query = """
    SELECT s.user_id, s.refresh_token, s.expires_at
    FROM session AS s
    INNER JOIN [user] AS u ON u.id = s.user_id
    WHERE u.username = :username
    """

    result = await db.execute(query, {"username": username})
    session = result.fetchone()

    if not session:
        raise AuthenticationError("Active session not found. Please login again.")

    # check expiry
    if session.expires_at and session.expires_at < datetime.now(timezone.utc):
        raise AuthenticationError("Session expired. Please login again.")

    # Return authenticated user's ID (to use in staff service)
    return session.user_id