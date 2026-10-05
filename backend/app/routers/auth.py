import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    UserBasicInfo,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.utils.dependencies import get_current_user, get_current_admin

logger = logging.getLogger("app.routers.auth")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a regular user with role 'user'. Storing passwords as salted bcrypt hashes.",
)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db),
):
    # Check if email is already in use
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        logger.warning(f"Registration failed: Email '{user_in.email}' is already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Hash the password securely with bcrypt
    hashed_password = get_password_hash(user_in.password)

    # Create new regular user
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hashed_password,
        role=UserRole.USER.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"User registered successfully: {new_user.email} (id={new_user.id}, role={new_user.role})")
    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT token",
    description="Authenticates user credentials and returns a signed JWT bearer token.",
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: '{credentials.email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"User authenticated successfully: {user.email} (id={user.id}, role={user.role})")

    # Generate JWT containing user id (sub), email, and role
    token_payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
    access_token = create_access_token(data=token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
    description="Requires a valid JWT Bearer token and returns authenticated user profile.",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/admin-only",
    summary="Test admin role authorization",
    description="Protected endpoint accessible only by users with the 'admin' role.",
)
def admin_only_check(
    current_admin: User = Depends(get_current_admin),
):
    return {
        "message": "Admin authorization verified successfully.",
        "admin": {
            "id": current_admin.id,
            "name": current_admin.name,
            "email": current_admin.email,
            "role": current_admin.role,
        },
    }
