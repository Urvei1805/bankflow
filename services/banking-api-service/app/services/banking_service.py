"""
BankFlow Banking API Service — Business Logic
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banking import Account, Consent, Payment, Transaction


async def create_payment(
    db: AsyncSession,
    user_id: str,
    debtor_account_id: uuid.UUID,
    creditor_account_id: str,
    creditor_name: str,
    amount: float,
    currency: str = "GBP",
    payment_reference: Optional[str] = None,
    end_to_end_id: Optional[str] = None,
    remittance_info: Optional[str] = None,
) -> Payment:
    """Create a new payment initiation. Includes BOLA check."""
    # BOLA: Verify debtor account belongs to user
    result = await db.execute(
        select(Account).where(Account.id == debtor_account_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise ValueError("Debtor account not found")
    if str(account.user_id) != user_id:
        raise PermissionError("You do not own this account (BOLA protection)")

    payment = Payment(
        debtor_account_id=debtor_account_id,
        creditor_account_id=creditor_account_id,
        creditor_name=creditor_name,
        amount=amount,
        currency=currency,
        payment_reference=payment_reference,
        end_to_end_id=end_to_end_id or str(uuid.uuid4())[:35],
        instruction_id=str(uuid.uuid4())[:35],
        remittance_info=remittance_info,
        initiated_by=uuid.UUID(user_id),
        status="pending",
    )
    db.add(payment)
    await db.flush()
    await db.refresh(payment)
    return payment


async def get_account_transactions(
    db: AsyncSession,
    account_id: uuid.UUID,
    user_id: str,
    limit: int = 20,
    cursor: Optional[str] = None,
) -> tuple[list[Transaction], Optional[str], bool]:
    """
    Get paginated transactions for an account.
    Returns (transactions, next_cursor, has_more).
    BOLA: Ensures user owns the account.
    """
    # BOLA check
    result = await db.execute(
        select(Account).where(Account.id == account_id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise ValueError("Account not found")
    if str(account.user_id) != user_id:
        raise PermissionError("You do not own this account (BOLA protection)")

    query = (
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit + 1)
    )

    if cursor:
        try:
            cursor_dt = datetime.fromisoformat(cursor)
            query = query.where(Transaction.created_at < cursor_dt)
        except ValueError:
            pass

    result = await db.execute(query)
    transactions = list(result.scalars().all())

    has_more = len(transactions) > limit
    if has_more:
        transactions = transactions[:limit]

    next_cursor = None
    if has_more and transactions:
        next_cursor = transactions[-1].created_at.isoformat()

    return transactions, next_cursor, has_more


async def create_consent(
    db: AsyncSession,
    user_id: str,
    tpp_id: uuid.UUID,
    permissions: list[str],
    expires_in_days: int = 90,
) -> Consent:
    """Create a new consent record."""
    consent = Consent(
        user_id=uuid.UUID(user_id),
        tpp_id=tpp_id,
        permissions=permissions,
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        status="awaiting_authorization",
    )
    db.add(consent)
    await db.flush()
    await db.refresh(consent)
    return consent


async def get_consent(
    db: AsyncSession,
    consent_id: uuid.UUID,
    user_id: str,
) -> Optional[Consent]:
    """Get consent by ID with BOLA check."""
    result = await db.execute(
        select(Consent).where(Consent.id == consent_id)
    )
    consent = result.scalar_one_or_none()
    if consent and str(consent.user_id) != user_id:
        raise PermissionError("You do not own this consent (BOLA protection)")
    return consent


async def update_payment_status(
    db: AsyncSession,
    payment_id: uuid.UUID,
    new_status: str,
) -> Optional[Payment]:
    """Update payment status (webhook handler)."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        return None
    payment.status = new_status
    await db.flush()
    await db.refresh(payment)
    return payment


async def ensure_demo_data(db: AsyncSession, user_id: str):
    """Create demo account and transactions for a new user if none exist."""
    result = await db.execute(
        select(Account).where(Account.user_id == uuid.UUID(user_id))
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    import random
    import string

    account = Account(
        user_id=uuid.UUID(user_id),
        account_number="".join(random.choices(string.digits, k=8)),
        sort_code="12-34-56",
        currency="GBP",
        balance=25000.00,
        account_type="current",
        status="active",
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)

    # Create sample transactions
    categories = [
        "groceries", "restaurants", "transport", "entertainment",
        "utilities", "healthcare", "shopping", "travel",
    ]
    countries = ["GB", "US", "FR", "DE", "JP", "NG", "BR", "IN"]
    balance = 25000.0

    for i in range(50):
        amount = round(random.uniform(5.0, 500.0), 2)
        txn_type = random.choice(["debit", "credit"])
        if txn_type == "debit":
            balance -= amount
        else:
            balance += amount

        country = random.choice(countries)
        hour = random.randint(0, 23)
        is_foreign = country != "GB"
        is_night = hour < 6 or hour > 22
        is_high_amount = amount > 300

        # Fraud scoring
        risk_score = 0.0
        if is_high_amount:
            risk_score += 0.3
        if is_foreign:
            risk_score += 0.3
        if is_night:
            risk_score += 0.2

        risk_level = "LOW"
        if risk_score >= 0.6:
            risk_level = "HIGH"
        elif risk_score >= 0.3:
            risk_level = "MEDIUM"

        txn = Transaction(
            account_id=account.id,
            amount=amount,
            currency="GBP",
            merchant_category=random.choice(categories),
            merchant_name=f"Merchant_{i}",
            transaction_type=txn_type,
            status="completed",
            country=country,
            fraud_score=round(risk_score, 2),
            fraud_risk_level=risk_level,
            description=f"Sample transaction {i}",
            balance_after=round(balance, 2),
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 90)),
        )
        db.add(txn)

    await db.flush()
    return account
