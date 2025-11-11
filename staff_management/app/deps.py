from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import requests

# Token retrieval system
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Replace this with your actual User Service URL
USER_SERVICE_URL = "http://127.0.0.1:8001/api/v1/auth/verify-token"


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verify the token by calling the User Service.
    Returns user info if valid; raises HTTPException otherwise.
    """
    try:
        response = requests.post(USER_SERVICE_URL, json={"token": token})
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return response.json()  # Expected: { "user_id": 1, "role": "admin" }
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service not reachable",
        )


def admin_required(user=Depends(verify_token)):
    """Allow access only for Admin users"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user


def authenticated_user(user=Depends(verify_token)):
    """Allow access for any authenticated (valid token) user"""
    return user
