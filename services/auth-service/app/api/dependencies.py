"""
BankFlow Auth Service — Dependencies
Shared FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
) -> dict:
    """Extract and validate the current user from JWT bearer token."""
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
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "type": "https://bankflow.dev/errors/invalid-token",
                    "title": "Invalid Token",
                    "status": 401,
                    "detail": "Token is not an access token",
                },
            )
        return {
            "user_id": payload["sub"],
            "username": payload.get("username"),
            "role": payload.get("role", "user"),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "https://bankflow.dev/errors/invalid-token",
                "title": "Invalid Token",
                "status": 401,
                "detail": "Could not validate credentials",
            },
        )


def require_role(allowed_roles: list[str]):
    """Dependency factory: restrict access to certain roles."""

    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "type": "https://bankflow.dev/errors/forbidden",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": f"Role '{current_user['role']}' is not authorized",
                },
            )
        return current_user

    return role_checker
