"""
BankFlow Banking API Service — WebSocket Real-Time Transaction Feed
Streams mock transaction events for the dashboard.
"""
import asyncio
import json
import random
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])

# Connected clients
connected_clients: set[WebSocket] = set()


def _generate_mock_transaction() -> dict:
    """Generate a single mock transaction event."""
    categories = [
        "groceries", "restaurants", "transport", "entertainment",
        "utilities", "healthcare", "shopping", "travel",
    ]
    countries = ["GB", "US", "FR", "DE", "JP", "NG", "BR", "IN"]
    statuses = ["completed", "pending", "completed", "completed"]

    amount = round(random.uniform(2.0, 800.0), 2)
    country = random.choice(countries)
    hour = datetime.now(timezone.utc).hour

    # Fraud scoring
    is_foreign = country != "GB"
    is_night = hour < 6 or hour > 22
    is_high = amount > 300

    risk_score = 0.0
    if is_high:
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

    return {
        "transaction_id": str(uuid.uuid4()),
        "account_id": str(uuid.uuid4()),
        "amount": amount,
        "currency": "GBP",
        "merchant_category": random.choice(categories),
        "merchant_name": f"Merchant_{random.randint(1, 100)}",
        "transaction_type": random.choice(["debit", "credit"]),
        "status": random.choice(statuses),
        "country": country,
        "fraud_score": round(risk_score, 2),
        "fraud_risk_level": risk_level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.websocket("/ws/transactions")
async def transaction_feed(websocket: WebSocket):
    """WebSocket endpoint for real-time transaction streaming."""
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            # Generate and send a mock transaction every 1-3 seconds
            txn = _generate_mock_transaction()
            await websocket.send_text(json.dumps(txn))
            await asyncio.sleep(random.uniform(1.0, 3.0))
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception:
        connected_clients.discard(websocket)
