"""
BankFlow Auth Service — Pydantic Schemas
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Request Schemas ───────────────────────────────────────────
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = Field("user", pattern="^(user|tpp|admin)$")


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


# ── Response Schemas ──────────────────────────────────────────
class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class APIKeyResponse(BaseModel):
    id: uuid.UUID
    api_key: str  # Only returned once on creation
    key_prefix: str
    name: str
    created_at: datetime


class VerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    role: Optional[str] = None
    message: str


class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "auth-service"
    version: str = "1.0.0"


# ── RFC 7807 Error Response ───────────────────────────────────
class ErrorDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
