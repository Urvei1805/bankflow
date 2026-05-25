# BankFlow Architecture

## System Overview

BankFlow follows a **microservices architecture** with three core services, a data pipeline layer, and a React frontend — all orchestrated via Docker Compose locally and ECS Fargate on AWS.

## Service Boundaries

### Auth Service (port 8001)
**Responsibility:** Identity, authentication, and authorization.
- User/TPP registration
- JWT token issuance (RS256)
- Refresh token management
- API key generation
- RBAC enforcement

### Banking API Service (port 8002)
**Responsibility:** Core banking operations.
- Payment initiation (ISO 20022)
- Transaction listing with cursor-pagination
- Consent management (Open Banking)
- WebSocket real-time transaction feed
- BOLA protection

### Analytics Service (port 8003)
**Responsibility:** Read-only analytical queries.
- Summary statistics
- Fraud risk distribution
- Spend by category
- Redis caching (60s TTL)

## Data Flow

```
User → Frontend → Auth Service → JWT → Banking API → PostgreSQL
                                         ↓
                               WebSocket (live feed)
                                         ↓
                              Analytics Service → Redis Cache
                                         ↓
                              PySpark Pipeline → Parquet → PostgreSQL
```

## Inter-Service Communication
- Services share a PostgreSQL database (acceptable for MVP)
- Auth verification uses shared JWT keys (via Docker volumes)
- Future: API Gateway + service mesh for production

## Technology Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI | Async-first, auto-docs, Pydantic validation |
| SQLAlchemy 2.0 | Async support, mature ORM |
| RS256 JWT | Asymmetric signing, banking-grade security |
| JSON:API format | Industry standard for REST APIs |
| PySpark | Scalable batch processing, window functions |
| Recharts | Lightweight, composable React charts |
| Docker Compose | Single-command local deployment |
| Terraform | Declarative, version-controlled infrastructure |
