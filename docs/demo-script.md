# BankFlow Demo Script

## Setup (2 minutes)
```bash
git clone https://github.com/yourusername/bankflow.git
cd bankflow
cp .env.example .env
docker compose up --build -d
```

Wait for all services to be healthy (~30 seconds).

## Demo Flow (5 minutes)

### 1. Show Architecture
- Open the README and explain the microservices design
- Show the Docker Compose file briefly

### 2. Health Checks
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### 3. Register & Login
```bash
# Register
curl -X POST http://localhost:8001/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@bankflow.dev","username":"demouser","password":"DemoPass123!"}'

# Login
curl -X POST http://localhost:8001/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"DemoPass123!"}'
```

### 4. Seed Demo Data
Use the access_token from login:
```bash
curl -X POST http://localhost:8002/v1/demo/seed \
  -H "Authorization: Bearer <TOKEN>"
```

### 5. Show Dashboard
Open http://localhost:3000 — show:
- Stats cards with real-time data
- Fraud distribution pie chart
- Spend by category bar chart
- Live transaction feed (WebSocket)

### 6. Show Swagger Docs
Open http://localhost:8001/docs — show interactive API documentation.

### 7. Show PySpark Pipeline (bonus)
```bash
cd data-pipeline/data-generator
python generate_transactions.py
cd ../batch
python batch_pipeline.py
```

## Cleanup
```bash
docker compose down -v
```
