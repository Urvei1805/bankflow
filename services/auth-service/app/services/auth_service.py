"""
BankFlow Auth Service — Auth Business Logic
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_password,
)
from app.models.user import APIKey, RefreshToken, User

settings = get_settings()


async def register_user(
    db: AsyncSession,
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    role: str = "user",
) -> User:
    """Register a new user. Raises ValueError if email/username already exists."""
    # Check existing
    result = await db.execute(
        select(User).where((User.email == email) | (User.username == username))
    )
    existing = result.scalar_one_or_none()
    if existing:
        if existing.email == email:
            raise ValueError("Email already registered")
        raise ValueError("Username already taken")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Authenticate user by username and password."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def create_tokens(db: AsyncSession, user: User) -> dict:
    """Create access + refresh token pair for a user."""
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token hash for revocation
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rt)
    await db.flush()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> dict:
    """Validate refresh token and issue new tokens."""
    try:
        payload = decode_token(refresh_token_str)
    except Exception:
        raise ValueError("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token")

    # Check if revoked
    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
        )
    )
    stored_rt = result.scalar_one_or_none()
    if not stored_rt:
        raise ValueError("Refresh token has been revoked")

    # Revoke old refresh token
    stored_rt.revoked = True

    # Get user
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    return await create_tokens(db, user)


async def create_user_api_key(
    db: AsyncSession, user_id: str, name: str
) -> dict:
    """Generate a new API key for a user."""
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    api_key = APIKey(
        user_id=user_id,
        key_hash=key_hash,
        key_prefix=raw_key[:10],
        name=name,
    )
    db.add(api_key)
    await db.flush()
    await db.refresh(api_key)

    return {
        "id": api_key.id,
        "api_key": raw_key,
        "key_prefix": api_key.key_prefix,
        "name": api_key.name,
        "created_at": api_key.created_at,
    }


async def verify_token(token: str) -> dict:
    """Verify a JWT access token and return payload."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return {"valid": False, "message": "Not an access token"}
        return {
            "valid": True,
            "user_id": payload["sub"],
            "role": payload.get("role", "user"),
            "message": "Token is valid",
        }
    except Exception as e:
        return {"valid": False, "message": str(e)}
