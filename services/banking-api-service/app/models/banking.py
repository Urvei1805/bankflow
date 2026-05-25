"""
BankFlow Banking API Service — ORM Models
Accounts, Payments, Transactions, and Consent records.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, JSON,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Account(Base):
    """Bank account model."""
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    account_number = Column(String(34), unique=True, nullable=False)
    sort_code = Column(String(10), nullable=True)
    currency = Column(String(3), default="GBP", nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    account_type = Column(
        Enum("current", "savings", "business", name="account_type"),
        default="current",
    )
    status = Column(
        Enum("active", "frozen", "closed", name="account_status"),
        default="active",
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Payment(Base):
    """Payment initiation record (ISO 20022 pain.001 style)."""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debtor_account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creditor_account_id = Column(String(34), nullable=False)
    creditor_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="GBP", nullable=False)
    status = Column(
        Enum(
            "pending", "accepted", "rejected", "completed", "failed",
            name="payment_status",
        ),
        default="pending",
    )
    payment_reference = Column(String(35), nullable=True)
    end_to_end_id = Column(String(35), nullable=True)
    instruction_id = Column(String(35), nullable=True)
    remittance_info = Column(Text, nullable=True)
    initiated_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Transaction(Base):
    """Transaction record."""
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="GBP", nullable=False)
    merchant_category = Column(String(100), nullable=True)
    merchant_name = Column(String(255), nullable=True)
    transaction_type = Column(
        Enum("debit", "credit", name="txn_type"),
        nullable=False,
    )
    status = Column(
        Enum("pending", "completed", "failed", "reversed", name="txn_status"),
        default="completed",
    )
    country = Column(String(3), nullable=True)
    fraud_score = Column(Float, default=0.0)
    fraud_risk_level = Column(
        Enum("LOW", "MEDIUM", "HIGH", name="fraud_risk"),
        default="LOW",
    )
    description = Column(Text, nullable=True)
    balance_after = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class Consent(Base):
    """Open Banking consent record."""
    __tablename__ = "consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tpp_id = Column(UUID(as_uuid=True), nullable=False)
    permissions = Column(JSON, nullable=False)
    status = Column(
        Enum(
            "awaiting_authorization", "authorized", "rejected", "revoked",
            name="consent_status",
        ),
        default="awaiting_authorization",
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
