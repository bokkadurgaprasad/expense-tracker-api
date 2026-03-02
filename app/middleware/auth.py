"""
JWT Authentication Middleware for FastAPI

This module provides a dependency function to extract and verify JWT tokens
from the Authorization header for route authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import AuthService
from app.config import settings


# HTTP Bearer token scheme for extracting Authorization header
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and verify JWT from Authorization header.
    
    This function:
    1. Extracts the JWT token from the Authorization: Bearer <token> header
    2. Verifies the token signature and expiration
    3. Extracts the user_id from the valid token
    4. Returns 401 for invalid or expired tokens
    
    Args:
        credentials: HTTP Bearer credentials automatically extracted by FastAPI
        
    Returns:
        user_id: The user ID extracted from the valid JWT token
        
    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or missing
        
    Usage:
        @app.get("/protected-route")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            # user_id is now available for authorization
            return {"user_id": user_id}
    """
    # Extract the token from credentials
    token = credentials.credentials
    
    # Initialize auth service for token verification
    auth_service = AuthService()
    
    # Verify token and extract user_id
    user_id = auth_service.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id
