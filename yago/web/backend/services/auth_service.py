"""
YAGO v8.3 - Authentication Service
JWT-based authentication with secure password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import sys

# Import get_db
try:
    from ..database import get_db
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings - Secure configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Check if we're in development mode
    if os.getenv("ENV", "development") == "production":
        raise ValueError(
            "CRITICAL SECURITY ERROR: JWT_SECRET_KEY must be set in production environment! "
            "Generate a secure key with: openssl rand -hex 32"
        )
    else:
        # Development fallback with warning
        SECRET_KEY = "dev-secret-key-DO-NOT-USE-IN-PRODUCTION"
        print("⚠️  WARNING: Using development JWT secret key. Set JWT_SECRET_KEY in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    """Handle authentication operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        """Authenticate a user with email and password"""
        try:
            from ..models import User
        except ImportError:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from models import User

        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: str = None):
        """Create a new user"""
        try:
            from ..models import User
        except ImportError:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from models import User

        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("User with this email already exists")

        # Create user
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_last_login(db: Session, user_id: str):
        """Update user's last login timestamp"""
        try:
            from ..models import User
        except ImportError:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from models import User

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = AuthService.verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        from ..models import User
    except ImportError:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from models import User

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Optional: Require verified email
def get_current_verified_user(current_user = Depends(get_current_user)):
    """Dependency to get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please verify your email to access this resource."
        )
    return current_user
