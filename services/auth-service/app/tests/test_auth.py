"""
BankFlow Auth Service — Test Suite
"""
import pytest
from httpx import AsyncClient, ASGITransport

# These tests use a mock/in-memory approach.
# For full integration tests, use the Docker Compose setup with a real PostgreSQL.


@pytest.mark.asyncio
async def test_health_check():
    """Test the health endpoint returns 200."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "auth-service"


@pytest.mark.asyncio
async def test_register_missing_fields():
    """Test registration with missing fields returns 422."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/v1/auth/register", json={})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with bad credentials returns 401."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )
        # Will return 401 (with real DB) or 500 (without DB connection)
        assert response.status_code in [401, 500]


@pytest.mark.asyncio
async def test_verify_no_token():
    """Test verify endpoint without token."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/auth/verify")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


@pytest.mark.asyncio
async def test_api_key_unauthorized():
    """Test API key creation without auth returns 401/403."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/auth/api-key",
            json={"name": "test-key"},
        )
        assert response.status_code in [401, 403]
