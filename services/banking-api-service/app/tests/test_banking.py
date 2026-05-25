"""
BankFlow Banking API Service — Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_health_check():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "banking-api-service"


@pytest.mark.asyncio
async def test_create_payment_unauthorized():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/payments", json={})
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_get_transactions_unauthorized():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/v1/accounts/00000000-0000-0000-0000-000000000000/transactions"
        )
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_create_consent_unauthorized():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/consent", json={})
        assert response.status_code in [401, 403, 422]


@pytest.mark.asyncio
async def test_webhook_invalid_payload():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/webhooks/payment-status", json={})
        assert response.status_code == 422
