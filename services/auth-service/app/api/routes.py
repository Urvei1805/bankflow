"""
BankFlow Auth Service — API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.auth import (
    APIKeyCreateRequest,
    APIKeyResponse,
    ErrorDetail,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_tokens,
    create_user_api_key,
    refresh_access_token,
    register_user,
    verify_token,
)

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorDetail}},
)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user or TPP (Third-Party Provider)."""
    try:
        user = await register_user(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            full_name=request.full_name,
            role=request.role,
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "type": "https://bankflow.dev/errors/conflict",
                "title": "Conflict",
                "status": 409,
                "detail": str(e),
            },
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorDetail}},
)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return JWT tokens."""
    user = await authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "https://bankflow.dev/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Invalid username or password",
            },
        )
    return await create_tokens(db, user)


@router.post(
    "/token/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorDetail}},
)
async def refresh_token(
    request: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh an access token using a valid refresh token."""
    try:
        return await refresh_access_token(db, request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "type": "https://bankflow.dev/errors/unauthorized",
                "title": "Unauthorized",
                "status": 401,
                "detail": str(e),
            },
        )


@router.post(
    "/api-key",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key for the authenticated user."""
    result = await create_user_api_key(
        db=db,
        user_id=current_user["user_id"],
        name=request.name,
    )
    return result


@router.get(
    "/verify",
    response_model=VerifyResponse,
)
async def verify(
    request: Request,
):
    """Verify a JWT access token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return VerifyResponse(valid=False, message="Missing Bearer token")
    token = auth_header.replace("Bearer ", "")
    result = await verify_token(token)
    return VerifyResponse(**result)
