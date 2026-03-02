"""
Service layer for authentication and user management
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt
from bson import ObjectId
from db.connection import get_database
from app.models.user import UserCreate, User, UserLogin, PasswordReset
from app.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt 72 byte limit handling"""
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self,
        user_id: Optional[str] = None,
        data: Optional[dict] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token. Pass user_id or data dict with 'sub' key."""
        to_encode = (data or {}).copy()
        if user_id is not None:
            to_encode["sub"] = user_id
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT and return user_id (sub) or None if invalid/expired."""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return payload.get("sub")
        except jwt.PyJWTError:
            return None
    
    def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if username already exists
        existing_user = self.users_collection.find_one({"username": user_data.username})
        if existing_user:
            raise ValueError("Username already exists")
        
        # Create new user document
        user_doc = {
            "_id": ObjectId(),
            "username": user_data.username,
            "password_hash": self.hash_password(user_data.password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        self.users_collection.insert_one(user_doc)
        
        return User(
            _id=str(user_doc["_id"]),
            username=user_doc["username"],
            password_hash=user_doc["password_hash"],
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user and return user object if valid"""
        user_doc = self.users_collection.find_one({"username": login_data.username})
        if not user_doc:
            return None
        
        if not self.verify_password(login_data.password, user_doc["password_hash"]):
            return None
        
        return User(
            _id=str(user_doc["_id"]),
            username=user_doc["username"],
            password_hash=user_doc["password_hash"],
            created_at=user_doc["created_at"],
            updated_at=user_doc["updated_at"]
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return None
            
            return User(
                _id=str(user_doc["_id"]),
                username=user_doc["username"],
                password_hash=user_doc["password_hash"],
                created_at=user_doc["created_at"],
                updated_at=user_doc["updated_at"]
            )
        except Exception:
            return None
    
    def reset_password(self, user_id: str, reset_data: PasswordReset) -> bool:
        """Reset user password"""
        try:
            # Get user document
            user_doc = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return False
            
            # Verify old password
            if not self.verify_password(reset_data.old_password, user_doc["password_hash"]):
                return False
            
            # Update password
            new_password_hash = self.hash_password(reset_data.new_password)
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return True
        except Exception:
            return False
