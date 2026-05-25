"""
BankFlow Banking API Service — Auth Dependencies
Verifies JWT or API key for incoming requests.
"""
import os

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()
security_scheme = HTTPBearer(auto_error=False)


def _get_decode_key() -> str:
    """Get the key for decoding JWTs."""
    path = settings.JWT_PUBLIC_KEY_PATH
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return settings.JWT_SECRET_KEY


def _get_algorithm() -> str:
    path = settings.JWT_PUBLIC_KEY_PATH
    if os.path.exists(path):
        return "RS256"
    return "HS256"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
) -> dict:
    """Extract and validate user from JWT bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "https://bankflow.dev/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Missing authentication credentials",
            },
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            _get_decode_key(),
            algorithms=[_get_algorithm()],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not an access token",
            )
        return {
            "user_id": payload["sub"],
            "username": payload.get("username"),
            "role": payload.get("role", "user"),
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "https://bankflow.dev/errors/invalid-token",
                "title": "Invalid Token",
                "status": 401,
                "detail": "Could not validate credentials",
            },
        )
