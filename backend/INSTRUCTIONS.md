# INSTRUCTIONS — Quick Commerce AI Platform Backend

Practical step-by-step setup guide.

---

## 1. Clone / Open Project

```
e:\Hackathon\backend\
```

---

## 2. Create Virtual Environment

```powershell
cd e:\Hackathon\backend
python -m venv .venv
.venv\Scripts\activate
```

Verify:
```powershell
python --version       # Python 3.11+
pip --version
```

---

## 3. Install Requirements

```powershell
pip install -r requirements.txt
```

If `pydantic[email]` is missing:
```powershell
pip install "pydantic[email]"
```

---

## 4. Configure `.env`

```powershell
cp .env.example .env
```

Edit `.env`:

```env
# Database
DATABASE_URL=postgresql+psycopg2://qcuser:qcpass@localhost:5432/quickcommerce

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# App
APP_NAME=QuickCommerce AI Platform
APP_ENV=development
DEMO_MODE=true

# Optional: LLM (enables full AI chatbot)
# GEMINI_API_KEY=your-gemini-api-key
# OPENAI_API_KEY=your-openai-api-key

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 5. Start PostgreSQL

**Option A — Docker (recommended):**
```powershell
docker run -d --name qc-postgres `
  -e POSTGRES_DB=quickcommerce `
  -e POSTGRES_USER=qcuser `
  -e POSTGRES_PASSWORD=qcpass `
  -p 5432:5432 `
  postgres:15
```

**Option B — Local PostgreSQL:**
```sql
CREATE DATABASE quickcommerce;
CREATE USER qcuser WITH PASSWORD 'qcpass';
GRANT ALL PRIVILEGES ON DATABASE quickcommerce TO qcuser;
```

**Wait for Postgres to be ready:**
```powershell
docker exec qc-postgres pg_isready -U qcuser -d quickcommerce
```

---

## 6. Run Migrations

```powershell
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> a1b2c3d4e5f6, Phase 1: Initial 16-table schema
```

To check current state:
```powershell
alembic current
```

---

## 7. Seed Demo Data

```powershell
python scripts/seed_demo.py
```

Expected output:
```
Tables created/verified
Clearing existing demo data...
Creating retailers and users...
...
Seed complete!
  Retailers: 2, Stores: 5, Products: 12
  Demo credentials: admin@freshmart.in / Demo@1234
```

**SQLite demo (no Postgres):**
```powershell
$env:DATABASE_URL="sqlite:///./demo.db"
python -X utf8 scripts/seed_demo.py
```

---

## 8. Start FastAPI

```powershell
uvicorn app.main:app --reload --port 8000
```

Expected:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## 9. Open Swagger

```
http://localhost:8000/docs
```

Also available:
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

---

## 10. Run Tests

```powershell
# All tests
python -X utf8 -m pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/integration/test_phases_2_5.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

---

## 11. Example curl Requests

### Register a new account
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo@1234","retailer_name":"DemoMart"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@freshmart.in","password":"Demo@1234"}'
```
Copy the `access_token` from the response. Use it as `TOKEN` below.

### Get inventory alerts
```bash
curl http://localhost:8000/api/v1/inventory/alerts \
  -H "Authorization: Bearer $TOKEN"
```

### Get promotion recommendation
```bash
curl -X POST http://localhost:8000/api/v1/promotions/recommend \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":11,"dark_store_id":1,"objective":"REDUCE_EXPIRY_WASTE"}'
```
*(Replace product_id and dark_store_id with actual IDs from seed data)*

### Simulate a discount
```bash
curl -X POST http://localhost:8000/api/v1/promotions/simulate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":3,"dark_store_id":1,"discount_pct":20,"duration_days":7}'
```

### Chat (demo mode)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Which products are expiring?"}]}'
```

### Sales analytics
```bash
curl "http://localhost:8000/api/v1/analytics/sales?days=30" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 12. PowerShell Example (Windows)

```powershell
# Login
$resp = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@freshmart.in","password":"Demo@1234"}'

$TOKEN = $resp.access_token
$HEADERS = @{Authorization = "Bearer $TOKEN"}

# Inventory alerts
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/inventory/alerts" -Headers $HEADERS

# Promotion recommendation
$body = @{product_id=11; dark_store_id=1; objective="BALANCED"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/promotions/recommend" `
  -Method POST -Headers $HEADERS -ContentType "application/json" -Body $body
```

---

## 13. Troubleshooting

### `psycopg2.OperationalError: Connection refused`
- PostgreSQL is not running.
- Start Docker container or local Postgres.
- Check `DATABASE_URL` in `.env`.

### `ImportError: No module named 'pydantic.email_validator'`
```powershell
pip install "pydantic[email]"
```

### `alembic.exc.CommandError: Can't locate revision`
```powershell
alembic stamp head    # mark current state as head
alembic upgrade head  # apply any new migrations
```

### `UnicodeEncodeError` when running scripts
```powershell
$env:PYTHONUTF8="1"
python -X utf8 scripts/seed_demo.py
```

### Test failures on unique constraints
Tests use SQLite with transactional rollback. If you see `already exists` errors, the DB fixture may not be cleaning up. Run:
```powershell
pytest tests/ --forked    # or just re-run
```

### FastAPI starts but routes return 422
- Check request body matches the expected Pydantic schema.
- Open `/docs` and use the Swagger UI to test interactively.

---

## Demo Scenarios After Seeding

| Product | Store | Scenario |
|---|---|---|
| P0059 Full Cream Milk 1L | DEL-DS1 | CRITICAL expiry (0 days) |
| P0007 Spinach 200g | DEL-DS1 | CRITICAL expiry + understock |
| P0005 Coca-Cola 1L | DEL-DS1 | STOCKOUT (0 units) |
| P0003 Basmati Rice 5kg | DEL-DS1 | OVERSTOCK (500 units, max 100) |
| P0006 Maggi Noodles | DEL-DS1 | OVERSTOCK + trending UP |
| P0010 Almonds 500g | DEL-DS1 | High views (80), low purchases |
| P0004 Lays Chips | All stores | Trending UP (score 78/100) |

Use the promotion recommend endpoint with these products to see the engine in action.
