"""
Authentication endpoints
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Organization, OrganizationMember, UserRole
from app.schemas.auth import (
    Token,
    TokenData,
    UserCreate,
    UserLogin,
    UserResponse,
    GoogleAuthRequest,
    MicrosoftAuthRequest,
)
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=Dict[str, Any])
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and organization"""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_verified=True,  # For demo purposes
    )
    
    db.add(user)
    await db.flush()  # Flush to get user.id
    
    # Create organization if provided
    if user_data.organization_name:
        organization = Organization(
            name=user_data.organization_name,
            slug=user_data.organization_name.lower().replace(" ", "-"),
        )
        db.add(organization)
        await db.flush()  # Flush to get organization.id
        
        # Add user as organization owner
        membership = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=UserRole.OWNER,
        )
        db.add(membership)
    
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
        "message": "User registered successfully"
    }


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with email/password"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/google", response_model=Token)
async def google_auth(
    auth_data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate with Google OAuth"""
    
    # TODO: Verify Google token with Google's API
    # For demo purposes, we'll create a mock response
    
    # Extract user info from token (in real implementation, get from Google API)
    user_info = {
        "email": "demo@example.com",
        "first_name": "Demo",
        "last_name": "User",
        "google_id": "google_123456",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_info["email"]))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            google_id=user_info["google_id"],
            avatar_url=user_info["avatar_url"],
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/microsoft", response_model=Token)
async def microsoft_auth(
    auth_data: MicrosoftAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate with Microsoft OAuth"""
    
    # TODO: Verify Microsoft token with Microsoft's API
    # For demo purposes, we'll create a mock response
    
    user_info = {
        "email": "demo@example.com",
        "first_name": "Demo",
        "last_name": "User",
        "microsoft_id": "microsoft_123456",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    
    # Similar logic to Google auth...
    result = await db.execute(select(User).where(User.email == user_info["email"]))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            microsoft_id=user_info["microsoft_id"],
            avatar_url=user_info["avatar_url"],
            is_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    user.last_login = datetime.utcnow()
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Dict[str, str])
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """Refresh access token"""
    access_token = create_access_token(data={"sub": current_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
