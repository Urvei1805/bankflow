# BankFlow — Local Testing Guide

This guide walks you through the steps to successfully test BankFlow locally using Docker Compose, and debug any common issues.

## 1. Prerequisites
- Docker Desktop (must be running)
- PowerShell or bash terminal
- Curl or Postman for API testing

## 2. Start Docker Desktop
Ensure Docker Desktop is open and the daemon is running. You can verify it by running:
```bash
docker --version
docker compose version
```

## 3. Run Project Locally
To bring up all the microservices, frontend, and databases:
```bash
docker compose up -d
```

## 4. Rebuild Without Cache
If you changed Python requirements or Dockerfiles, a clean build is recommended:
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 5. Check Container Status
Check if all containers are running successfully:
```bash
docker compose ps -a
```
Expected output should list 6 containers (postgres, redis, auth, banking, analytics, frontend) with status `Up` or `Up (healthy)`.

## 6. View Logs
If a container crashes or you want to monitor requests, check its logs:
```bash
docker compose logs -f auth-service
docker compose logs -f banking-api-service
docker compose logs -f analytics-service
```

## 7. Health Check Commands
Check if each backend service is fully started and ready:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## 8. Auth Testing Commands
### Register
```bash
curl -X POST http://localhost:8001/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"TestPassword123!","role":"user"}'
```
### Login
```bash
curl -X POST http://localhost:8001/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPassword123!"}'
```
Save the `access_token` returned from the login step.

## 9. Banking API Testing Commands
### Seed Demo Data
```bash
curl -X POST http://localhost:8002/v1/demo/seed \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### Create Payment
```bash
curl -X POST http://localhost:8002/v1/payments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -d '{"debtor_account_id":"<YOUR_ACCOUNT_ID>","creditor_account_id":"ACC002","creditor_name":"Jane Smith","amount":150.00,"currency":"GBP"}'
```

### Get Transactions
```bash
curl "http://localhost:8002/v1/accounts/<YOUR_ACCOUNT_ID>/transactions?limit=10" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

## 10. Analytics Testing Commands
```bash
curl http://localhost:8003/v1/analytics/summary
curl http://localhost:8003/v1/analytics/fraud-distribution
curl http://localhost:8003/v1/analytics/spend-by-category
```

## 11. Frontend Testing Steps
Open your browser and navigate to:
```
http://localhost:3000
```
- Verify the dashboard loads.
- Ensure charts render without crashing.
- Live Transaction WebSocket feed should display "Live Feed Active".

## 12. Common Errors and Fixes

**Error:** `No module named email_validator`
**Fix:** Add `email-validator` to `auth-service/requirements.txt` and rebuild without cache. (This is already patched in the current repo).

**Error:** `Failed to connect to localhost port 8001`
**Fix:** Check if auth-service is running using `docker compose ps -a`. Inspect logs using `docker compose logs auth-service`. The structlog config might have crashed or syntax errors might be present.

**Error:** `DATABASE_URL connection refused`
**Fix:** Ensure the database URL uses `postgres` as the hostname inside Docker, not `localhost`. Example: `postgresql+asyncpg://bankflow_user:password@postgres:5432/bankflow`.

**Error:** CORS blocked frontend
**Fix:** Add the frontend local origin (`http://localhost:3000`) in the FastAPI CORS middleware `allow_origins` array. Currently, the project is configured with `allow_origins=["*"]` to prevent this locally.

**Error:** Missing RSA Keys (`private.pem` not found)
**Fix:** Ensure the Dockerfile generates the RSA keys at **runtime** using an `entrypoint.sh` script, instead of during the image build process, so they persist in the mapped Docker volume.

## 13. Database Migrations (Alembic)

BankFlow uses Alembic for database migrations. By default in local development (`ENVIRONMENT=development`), the FastAPI lifecycle will automatically create tables (`create_all()`).

For production or to test migrations manually, run them via Docker:

```bash
# Apply migrations for Auth Service
docker compose exec auth-service alembic upgrade head

# Apply migrations for Banking API Service
docker compose exec banking-api-service alembic upgrade head
```

To generate a new migration after modifying models:
```bash
docker compose exec auth-service alembic revision --autogenerate -m "description"
```
