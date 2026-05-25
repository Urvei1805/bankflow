"""
BankFlow Banking API Service — Pydantic Schemas
"""
import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Payment Schemas ───────────────────────────────────────────
class PaymentCreateRequest(BaseModel):
    """ISO 20022 pain.001 style payment initiation."""
    debtor_account_id: uuid.UUID
    creditor_account_id: str = Field(..., max_length=34)
    creditor_name: str = Field(..., max_length=255)
    amount: float = Field(..., gt=0, le=1_000_000)
    currency: str = Field("GBP", max_length=3)
    payment_reference: Optional[str] = Field(None, max_length=35)
    end_to_end_id: Optional[str] = Field(None, max_length=35)
    remittance_info: Optional[str] = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    debtor_account_id: uuid.UUID
    creditor_account_id: str
    creditor_name: str
    amount: float
    currency: str
    status: str
    payment_reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Transaction Schemas ───────────────────────────────────────
class TransactionResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    amount: float
    currency: str
    merchant_category: Optional[str]
    merchant_name: Optional[str]
    transaction_type: str
    status: str
    country: Optional[str]
    fraud_score: float
    fraud_risk_level: str
    description: Optional[str]
    balance_after: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Consent Schemas ───────────────────────────────────────────
class ConsentCreateRequest(BaseModel):
    tpp_id: uuid.UUID
    permissions: list[str] = Field(
        ...,
        description="e.g. ['ReadAccountsBasic', 'ReadTransactionsDetail']",
    )
    expires_in_days: int = Field(90, ge=1, le=365)


class ConsentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tpp_id: uuid.UUID
    permissions: list[str]
    status: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ── Webhook Schemas ───────────────────────────────────────────
class WebhookPaymentStatus(BaseModel):
    payment_id: uuid.UUID
    new_status: str = Field(..., pattern="^(accepted|rejected|completed|failed)$")


# ── JSON:API Wrapper ─────────────────────────────────────────
class JSONAPIResource(BaseModel):
    type: str
    id: str
    attributes: dict[str, Any]
    relationships: Optional[dict[str, Any]] = None
    links: Optional[dict[str, str]] = None


class JSONAPIResponse(BaseModel):
    data: JSONAPIResource | list[JSONAPIResource]
    meta: Optional[dict[str, Any]] = None
    links: Optional[dict[str, str]] = None


class JSONAPIErrorSource(BaseModel):
    pointer: Optional[str] = None
    parameter: Optional[str] = None


class JSONAPIError(BaseModel):
    """RFC 7807 compatible error in JSON:API format."""
    status: str
    title: str
    detail: str
    source: Optional[JSONAPIErrorSource] = None


# ── Pagination ────────────────────────────────────────────────
class PaginationMeta(BaseModel):
    cursor: Optional[str] = None
    limit: int
    has_more: bool
