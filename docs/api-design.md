# BankFlow API Design

## Overview
All BankFlow APIs follow REST conventions with JSON:API response format and RFC 7807 error responses.

## Base URLs
| Service | Local URL |
|---------|-----------|
| Auth | `http://localhost:8001` |
| Banking | `http://localhost:8002` |
| Analytics | `http://localhost:8003` |

## Authentication
All protected endpoints require a `Bearer` token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

## Auth Service Endpoints

### POST /v1/auth/register
Register a new user or TPP.
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "user"
}
```

### POST /v1/auth/login
Authenticate and receive JWT tokens.
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```
Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### POST /v1/auth/token/refresh
Refresh an access token.

### POST /v1/auth/api-key
Generate a new API key (requires auth).

### GET /v1/auth/verify
Verify a JWT token validity.

## Banking API Endpoints

### POST /v1/payments
Initiate a payment (ISO 20022 pain.001 style).

### GET /v1/accounts/{account_id}/transactions
List transactions with cursor-based pagination.
Query params: `limit` (1-100), `cursor` (ISO timestamp)

### POST /v1/consent
Create an Open Banking consent.

### GET /v1/consent/{consent_id}
Get consent details.

### POST /v1/webhooks/payment-status
Receive payment status webhook updates.

### WS /ws/transactions
WebSocket endpoint for real-time transaction streaming.

## Analytics Endpoints

### GET /v1/analytics/summary
Overall analytics: total transactions, volume, fraud counts.

### GET /v1/analytics/fraud-distribution
Fraud risk level breakdown.

### GET /v1/analytics/spend-by-category
Spend grouped by merchant category.

## Pagination
Cursor-based pagination using `limit` and `cursor` query params.

## Rate Limiting
- 100 requests per minute per IP
- Rate limit headers included in responses
