"""
Authentication helpers for ShareYourSales API
Provides authentication dependencies for endpoint routers
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv
from db_helpers import get_user_by_id

# Load environment variables
load_dotenv()

# JWT Configuration
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "fallback-secret-please-set-env-variable")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify JWT token and return payload

    Raises:
        HTTPException: If token is invalid or expired

    Returns:
        dict: Token payload with user_id in 'sub' field
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


async def get_current_user(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user

    Dependency for endpoints that require authentication

    Returns:
        dict: User data (without password_hash)

    Raises:
        HTTPException: If user not found
    """
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data


async def get_current_admin(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user and verify admin role

    Dependency for admin-only endpoints

    Returns:
        dict: User data (admin only)

    Raises:
        HTTPException: If user not found or not admin
    """
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data


async def get_current_merchant(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user and verify merchant role

    Dependency for merchant-only endpoints

    Returns:
        dict: User data (merchant only)

    Raises:
        HTTPException: If user not found or not merchant
    """
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.get("role") != "merchant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant access required"
        )

    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data


async def get_current_influencer(payload: dict = Depends(verify_token)):
    """
    Get current authenticated user and verify influencer role

    Dependency for influencer-only endpoints

    Returns:
        dict: User data (influencer only)

    Raises:
        HTTPException: If user not found or not influencer
    """
    user = get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.get("role") != "influencer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Influencer access required"
        )

    # Remove sensitive data
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    return user_data
