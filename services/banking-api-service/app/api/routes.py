"""
BankFlow Banking API Service — API Routes
Payments, Transactions, Consent, Webhooks with JSON:API responses.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.banking import (
    ConsentCreateRequest,
    JSONAPIResource,
    JSONAPIResponse,
    PaymentCreateRequest,
    WebhookPaymentStatus,
)
from app.services.banking_service import (
    create_consent,
    create_payment,
    ensure_demo_data,
    get_account_transactions,
    get_consent,
    update_payment_status,
)

router = APIRouter(prefix="/v1", tags=["Banking"])


def _to_jsonapi(resource_type: str, obj, attributes_keys: list[str]) -> JSONAPIResource:
    """Convert an ORM object to JSON:API resource."""
    attrs = {}
    for key in attributes_keys:
        val = getattr(obj, key, None)
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        elif isinstance(val, uuid.UUID):
            val = str(val)
        attrs[key] = val

    return JSONAPIResource(
        type=resource_type,
        id=str(obj.id),
        attributes=attrs,
        links={"self": f"/v1/{resource_type}s/{obj.id}"},
    )


# ── Payments ──────────────────────────────────────────────────
@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    request: PaymentCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initiate a payment (ISO 20022 pain.001 style)."""
    try:
        payment = await create_payment(
            db=db,
            user_id=current_user["user_id"],
            debtor_account_id=request.debtor_account_id,
            creditor_account_id=request.creditor_account_id,
            creditor_name=request.creditor_name,
            amount=request.amount,
            currency=request.currency,
            payment_reference=request.payment_reference,
            end_to_end_id=request.end_to_end_id,
            remittance_info=request.remittance_info,
        )
        resource = _to_jsonapi(
            "payment",
            payment,
            [
                "debtor_account_id", "creditor_account_id", "creditor_name",
                "amount", "currency", "status", "payment_reference",
                "end_to_end_id", "created_at",
            ],
        )
        return JSONAPIResponse(data=resource)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"type": "https://bankflow.dev/errors/not-found", "title": "Not Found", "status": 404, "detail": str(e)},
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"type": "https://bankflow.dev/errors/bola", "title": "BOLA Protection", "status": 403, "detail": str(e)},
        )


# ── Transactions ──────────────────────────────────────────────
@router.get("/accounts/{account_id}/transactions")
async def list_transactions(
    account_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    cursor: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List transactions for an account with cursor-based pagination."""
    try:
        transactions, next_cursor, has_more = await get_account_transactions(
            db=db,
            account_id=account_id,
            user_id=current_user["user_id"],
            limit=limit,
            cursor=cursor,
        )

        resources = [
            _to_jsonapi(
                "transaction",
                txn,
                [
                    "amount", "currency", "merchant_category", "merchant_name",
                    "transaction_type", "status", "country", "fraud_score",
                    "fraud_risk_level", "description", "balance_after", "created_at",
                ],
            )
            for txn in transactions
        ]

        return JSONAPIResponse(
            data=resources,
            meta={"cursor": next_cursor, "limit": limit, "has_more": has_more},
            links={
                "self": f"/v1/accounts/{account_id}/transactions?limit={limit}",
                **({"next": f"/v1/accounts/{account_id}/transactions?limit={limit}&cursor={next_cursor}"} if next_cursor else {}),
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── Consent ───────────────────────────────────────────────────
@router.post("/consent", status_code=status.HTTP_201_CREATED)
async def create_consent_endpoint(
    request: ConsentCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new Open Banking consent."""
    consent = await create_consent(
        db=db,
        user_id=current_user["user_id"],
        tpp_id=request.tpp_id,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days,
    )
    resource = _to_jsonapi(
        "consent",
        consent,
        ["user_id", "tpp_id", "permissions", "status", "expires_at", "created_at"],
    )
    return JSONAPIResponse(data=resource)


@router.get("/consent/{consent_id}")
async def get_consent_endpoint(
    consent_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consent status by ID."""
    try:
        consent = await get_consent(db, consent_id, current_user["user_id"])
        if not consent:
            raise HTTPException(status_code=404, detail="Consent not found")
        resource = _to_jsonapi(
            "consent",
            consent,
            ["user_id", "tpp_id", "permissions", "status", "expires_at", "created_at"],
        )
        return JSONAPIResponse(data=resource)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── Webhooks ──────────────────────────────────────────────────
@router.post("/webhooks/payment-status")
async def webhook_payment_status(
    request: WebhookPaymentStatus,
    db: AsyncSession = Depends(get_db),
):
    """Receive payment status webhook updates."""
    payment = await update_payment_status(db, request.payment_id, request.new_status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"status": "received", "payment_id": str(payment.id), "new_status": payment.status}


# ── Demo Data ─────────────────────────────────────────────────
@router.post("/demo/seed", tags=["Demo"])
async def seed_demo_data(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Seed demo account and transactions for the authenticated user."""
    account = await ensure_demo_data(db, current_user["user_id"])
    return {
        "message": "Demo data seeded",
        "account_id": str(account.id),
        "account_number": account.account_number,
    }
