"""
Authentication routes for user registration and login
"""
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.models.user import UserCreate, UserLogin, UserResponse, PasswordReset
from app.services.auth_service import AuthService
from db.connection import get_database
from app.middleware.auth import get_current_user_id


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_auth_service() -> AuthService:
    """Dependency to get AuthService instance with database"""
    return AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    Args:
        user_data: User registration data with username and password
        auth_service: Authentication service instance
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException 400: If username already exists
        HTTPException 422: If validation fails
    """
    try:
        user = auth_service.register_user(user_data)
        return UserResponse(
            _id=user.id,
            username=user.username,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )


@router.post("/login")
def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return JWT token
    
    Args:
        credentials: User login credentials with username and password
        auth_service: Authentication service instance
        
    Returns:
        JWT access token and user information
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        user = auth_service.authenticate_user(credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        access_token = auth_service.create_access_token(user_id=user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "_id": user.id,
                "username": user.username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    password_data: PasswordReset,
    user_id: str = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reset user password using old password verification
    
    Args:
        password_data: Password reset data with old and new passwords
        user_id: Current authenticated user ID
        auth_service: Authentication service instance
        
    Returns:
        Success message
        
    Raises:
        HTTPException 400: If old password is incorrect
        HTTPException 401: If user is not authenticated
    """
    try:
        # Get user from database
        db = get_database()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not auth_service.reset_password(user_id, password_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password or user not found"
            )
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
