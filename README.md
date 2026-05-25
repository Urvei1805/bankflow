# 🏦 BankFlow — Cloud-Native Open Banking Analytics Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-3.5-E25A1C?logo=apachespark&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform&logoColor=white)

**A production-grade open banking ecosystem with microservices, real-time analytics, fraud detection, and cloud deployment.**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Data Pipeline](#-data-pipeline)
- [Testing](#-testing)
- [Security](#-security)
- [AWS Deployment](#-aws-deployment)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)

---

## 🔍 Overview

BankFlow is a **cloud-native open banking analytics platform** that simulates real-world banking operations including:

- 💳 **Payment initiation** (ISO 20022 pain.001 style)
- 🏦 **Account & transaction management**
- 📄 **Consent management** (Open Banking standard)
- 🛡️ **Fraud detection & risk scoring**
- 📊 **Financial analytics** with PySpark batch processing
- 🔴 **Real-time transaction streaming** via WebSocket
- 🔐 **OAuth2/JWT authentication** with RS256

Built as a **microservices architecture** with Docker Compose for local development and Terraform for AWS deployment.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Dashboard (:3000)               │
│              Recharts · WebSocket · Axios                │
└─────────┬──────────────┬──────────────┬─────────────────┘
          │              │              │
    ┌─────▼─────┐  ┌─────▼──────┐  ┌───▼────────┐
    │   Auth    │  │  Banking   │  │ Analytics  │
    │ Service   │  │ API Service│  │  Service   │
    │  :8001    │  │   :8002    │  │   :8003    │
    │ FastAPI   │  │  FastAPI   │  │  FastAPI   │
    └─────┬─────┘  └─────┬──────┘  └───┬────────┘
          │              │              │
    ┌─────▼──────────────▼──────────────▼─────┐
    │           PostgreSQL (:5432)             │
    │          Redis (:6379)                   │
    └─────────────────────────────────────────┘
          │
    ┌─────▼─────────────────────────┐
    │     PySpark Data Pipeline     │
    │  Generator → Batch → Stream  │
    └───────────────────────────────┘
```

> See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

---

## ✨ Features

| Feature | Status | Description |
|---------|--------|-------------|
| User Registration & Login | ✅ | OAuth2/JWT with RS256/HS256 |
| API Key Management | ✅ | Generate & validate API keys |
| Role-Based Access Control | ✅ | user/tpp/admin roles |
| Payment Initiation | ✅ | ISO 20022 pain.001 style |
| Transaction Listing | ✅ | Cursor-based pagination |
| Consent Management | ✅ | Create/retrieve consents |
| BOLA Protection | ✅ | Users can only access their own data |
| Fraud Risk Scoring | ✅ | Rule-based: amount + country + time |
| Analytics Dashboard | ✅ | Fraud, spend, latency charts |
| Real-Time WebSocket Feed | ✅ | Live transaction streaming |
| PySpark Batch Pipeline | ✅ | 100K+ transaction processing |
| Streaming Simulation | ✅ | File-based micro-batches |
| Redis Caching | ✅ | 60s TTL for analytics |
| Docker Compose | ✅ | Full local deployment |
| CI/CD Pipeline | ✅ | GitHub Actions |
| AWS Infrastructure | ✅ | Terraform (VPC, ECS, RDS, etc.) |
| Security Headers | ✅ | HSTS, X-Frame-Options, etc. |
| Rate Limiting | ✅ | 100 req/min per IP |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Frontend** | React 18, Vite 5, Recharts, Axios |
| **Database** | PostgreSQL 15, Redis 7 |
| **Auth** | JWT (RS256/HS256), bcrypt, OAuth2 |
| **Data** | PySpark 3.5, Faker, Parquet |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Cloud** | Terraform, AWS (ECS, RDS, ElastiCache, S3, ALB) |
| **Security** | slowapi, Bandit, Trivy, CORS, HSTS |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone & Configure

```bash
git clone https://github.com/yourusername/bankflow.git
cd bankflow
cp .env.example .env
```

### 2. Start All Services

```bash
docker compose up --build
```

### 3. Access the Platform

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000 |
| **Auth API** | http://localhost:8001/docs |
| **Banking API** | http://localhost:8002/docs |
| **Analytics API** | http://localhost:8003/docs |

### 4. Test the APIs

```bash
# Register a user
curl -X POST http://localhost:8001/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@bankflow.dev","username":"testuser","password":"SecurePass123!","role":"user"}'

# Login
curl -X POST http://localhost:8001/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123!"}'

# Seed demo data (use the access_token from login)
curl -X POST http://localhost:8002/v1/demo/seed \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Get analytics
curl http://localhost:8003/v1/analytics/summary
```

---

## 🔧 Environment Variables

See [.env.example](.env.example) for all variables. Key ones:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | Database host | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `change_me_in_production` |
| `JWT_SECRET_KEY` | JWT signing secret (HS256 fallback) | Must change |
| `REDIS_HOST` | Redis host | `redis` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `100` |
| `ANALYTICS_CACHE_TTL` | Redis cache TTL (seconds) | `60` |

---

## 📖 API Documentation

Interactive Swagger docs are available at `/docs` for each service.

See [docs/api-design.md](docs/api-design.md) for full API documentation.

### Response Format (JSON:API)

```json
{
  "data": {
    "type": "payment",
    "id": "uuid",
    "attributes": { ... },
    "links": { "self": "/v1/payments/uuid" }
  }
}
```

### Error Format (RFC 7807)

```json
{
  "type": "https://bankflow.dev/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid username or password"
}
```

---

## 📊 Data Pipeline

### Generate Mock Data

```bash
cd data-pipeline/data-generator
pip install -r requirements.txt
python generate_transactions.py
```

### Run PySpark Batch Pipeline

```bash
cd data-pipeline/batch
pip install -r requirements.txt
python batch_pipeline.py
```

### Run Streaming Simulation

```bash
cd data-pipeline/streaming
python streaming_simulation.py
```

---

## 🧪 Testing

```bash
# Auth Service
cd services/auth-service
pip install -r requirements.txt pytest pytest-asyncio httpx
pytest app/tests/ -v

# Banking Service
cd services/banking-api-service
pip install -r requirements.txt pytest pytest-asyncio httpx
pytest app/tests/ -v

# Analytics Service
cd services/analytics-service
pip install -r requirements.txt pytest pytest-asyncio httpx
pytest app/tests/ -v
```

---

## 🔐 Security

See [docs/security.md](docs/security.md) for full details.

- JWT RS256 token signing (with HS256 fallback)
- bcrypt password hashing
- BOLA protection on all user-scoped endpoints
- Rate limiting (100 req/min)
- Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)
- API key hashing for storage
- No hardcoded secrets

---

## ☁️ AWS Deployment

See [docs/aws-deployment.md](docs/aws-deployment.md) for full guide.

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

> ⚠️ AWS deployment is **optional**. The project works fully with Docker Compose locally.

---

## 📁 Project Structure

```
bankflow/
├── services/
│   ├── auth-service/           # OAuth2/JWT authentication
│   │   └── app/ (main, api, core, models, schemas, services, db, tests)
│   ├── banking-api-service/    # Payments, transactions, consent
│   │   └── app/ (main, api, core, models, schemas, services, db, tests)
│   └── analytics-service/     # Financial analytics
│       └── app/ (main, api, core, models, schemas, services, db, tests)
├── data-pipeline/
│   ├── batch/                  # PySpark batch processing
│   ├── streaming/              # Streaming simulation
│   └── data-generator/         # Mock data generation
├── frontend/                   # React dashboard
├── infra/
│   ├── terraform/              # AWS infrastructure
│   ├── aws-cdk/                # CDK placeholder
│   └── postgres/               # DB init scripts
├── postman/                    # API collection
├── docs/                       # Documentation
├── .github/workflows/          # CI/CD
├── docker-compose.yml          # Local deployment
├── .env.example                # Environment template
└── README.md
```

---

## 🔮 Future Improvements

- [x] Alembic database migrations
- [ ] Kafka/Redpanda real streaming integration
- [ ] API Gateway (Kong/Tyk)
- [ ] OpenTelemetry distributed tracing
- [ ] gRPC inter-service communication
- [ ] GraphQL API gateway
- [ ] Kubernetes Helm charts
- [ ] Prometheus + Grafana monitoring
- [ ] PySpark → PostgreSQL loader (automated)
- [ ] Email verification flow
- [ ] Password reset flow
- [ ] Admin dashboard panel
- [ ] Multi-tenant support
- [ ] Compliance reporting (PSD2/GDPR)

---

<div align="center">

**Built with ❤️ for the FinTech/Cloud/Cybersecurity community**

</div>
## ?? Environment Variables and Secrets

BankFlow uses environment variables for configuration. All sensitive values are designed to be injected via AWS Secrets Manager in production.

### Local Development Variables
For local Docker Compose, use the .env file (copy from .env.example).
Safe defaults are provided. You do not need to configure AWS Secrets Manager locally.
- ENV (default: development)
- LOG_LEVEL (default: INFO)
- CORS_ORIGINS (default: http://localhost:3000,http://localhost:5173)

### AWS ECS Variables (Non-Sensitive)
In AWS, the following can be injected directly as standard ECS Environment Variables via Terraform/CDK:
- ENV: production
- LOG_LEVEL: INFO
- AUTH_SERVICE_URL, BANKING_API_URL, ANALYTICS_SERVICE_URL (Internal ALB endpoints)
- CORS_ORIGINS: Your CloudFront frontend domain
- POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER
- REDIS_HOST, REDIS_PORT

### AWS Secrets Manager Variables
In AWS, all sensitive values MUST be stored in AWS Secrets Manager and injected into the ECS Task Definition as secrets. **NEVER** hardcode these in Terraform or standard ECS env vars.
- POSTGRES_PASSWORD: RDS password
- DATABASE_URL (Optional): Full postgresql connection string if preferred
- JWT_PRIVATE_KEY_PATH / JWT_PUBLIC_KEY_PATH (or injected as raw keys if modified)
- JWT_SECRET_KEY: HS256 fallback secret
- API_KEY_SECRET: Secret used to hash internal API keys
