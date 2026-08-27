# Quick Commerce AI Platform — Backend

AI-Driven Quick Commerce Promotion, Inventory and Retail Intelligence Platform.

## Project Purpose

A production-quality FastAPI backend powering a retailer-facing dashboard for:
- Real-time inventory monitoring with expiry/overstock/stockout alerts
- Deterministic promotion recommendation engine (no LLM required)
- SQL-based demand analytics and sales trends
- Multi-store, multi-city retailer management
- AI chatbot (demo mode + LLM integration ready)

---

## Architecture

```
HTTP Request
    │
    ▼
FastAPI Router (app/api/v1/)
    │
    ▼
Service Layer (app/services/)      ← business logic lives here
    │                 │
    ▼                 ▼
SQLAlchemy ORM    Promotion Engine (deterministic)
    │
    ▼
PostgreSQL (prod) / SQLite (test/demo)
```

**Key principle:** The LLM sits *after* the deterministic pipeline, not inside it.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI 0.100+ |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL (prod), SQLite (test) |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Migrations | Alembic |
| Tests | pytest + httpx |

---

## Quick Start

### 1. Clone / open project

```bash
cd e:\Hackathon\backend
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL and SECRET_KEY
```

### 5. Start PostgreSQL

```bash
# Option A: Docker
docker run -d --name qc-postgres \
  -e POSTGRES_DB=quickcommerce \
  -e POSTGRES_USER=qcuser \
  -e POSTGRES_PASSWORD=qcpass \
  -p 5432:5432 postgres:15

# Option B: local PostgreSQL — create database manually
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Seed demo data

```bash
python scripts/seed_demo.py
```

Demo credentials after seeding:
- `admin@freshmart.in` / `Demo@1234`
- `admin@quickbasket.in` / `Demo@1234`

### 8. Start FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

### 9. Open Swagger

```
http://localhost:8000/docs
```

### 10. Run tests

```bash
pytest tests/ -v
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://...` | Database connection string |
| `SECRET_KEY` | `change-me` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token TTL |
| `APP_ENV` | `development` | `development` / `production` |
| `DEMO_MODE` | `true` | Enables demo mode chatbot |
| `GEMINI_API_KEY` | _(optional)_ | Enables full LLM chatbot |
| `OPENAI_API_KEY` | _(optional)_ | Alternative LLM provider |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins |

---

## API Endpoints

### Auth
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register retailer + admin user |
| POST | `/api/v1/auth/login` | Login → JWT |
| GET | `/api/v1/auth/me` | Current user profile |

### Inventory
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/inventory` | All inventory (retailer-scoped) |
| GET | `/api/v1/inventory/alerts` | Active alerts (sorted by urgency) |
| GET | `/api/v1/inventory/{id}` | Single inventory record |
| PATCH | `/api/v1/inventory/{id}` | Update quantities |
| GET | `/api/v1/stores/{id}/inventory` | Store-specific inventory |

### Analytics
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/analytics/sales` | Sales trend over time |
| GET | `/api/v1/analytics/demand` | Demand forecast (7-day) |
| GET | `/api/v1/analytics/trends` | Product demand trends |
| GET | `/api/v1/analytics/customers` | Customer funnel metrics |
| GET | `/api/v1/analytics/stores` | Store comparison |
| GET | `/api/v1/analytics/top-products` | Top selling products |

### Promotions
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/promotions/recommend` | Promotion recommendation |
| POST | `/api/v1/promotions/simulate` | Simulate a specific discount |
| POST | `/api/v1/promotions/compare` | Compare N discount levels |
| GET | `/api/v1/promotions/history` | Past recommendations |

### Chat
| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/chat` | AI chatbot (demo / LLM) |

---

## Promotion Engine

The engine is **100% deterministic** — no LLM, no randomness.

### Inputs
- Product: MRP, cost price, shelf life, SKU
- Inventory: available quantity, reserved, max stock, reorder point, expiry date
- Sales: 30-day sales velocity (units/day)
- Context: trend score, weather, upcoming festivals, competitor prices
- Customer funnel: views, searches, cart additions, purchases

### Algorithm

For each candidate discount `d ∈ {10%, 20%, 30%}` (chosen by context):

```
sell_price        = mrp × (1 - d/100)
demand_factor     = 1 + (d/100) × 1.5        # elasticity = 1.5
expected_units    = base_demand × demand_factor × duration_days
expected_units    = min(expected_units, effective_stock)
expected_revenue  = expected_units × sell_price
expected_profit   = expected_units × (sell_price - cost_price)
inv_reduction_pct = expected_units / effective_stock × 100
stockout_risk_pct = max(0, (expected_raw - effective_stock) / effective_stock × 100)
```

Score is weighted by **objective**:
- `MAXIMIZE_PROFIT` → score = expected_profit
- `MAXIMIZE_SALES` → score = expected_units
- `CLEAR_INVENTORY` / `REDUCE_EXPIRY_WASTE` → score = inv_reduction_pct
- `BALANCED` → 50% profit + 30% units + 20% reduction

**Safety rule:** Negative-profit options are *shown* but only *recommended* for clearance/expiry objectives, always clearly flagged.

### Risk Flags
- `EXPIRY_CRITICAL` — product expires ≤ 0 days
- `OVERSTOCK_RISK` — quantity > max_stock × 1.1
- `STOCKOUT_RISK` — effective stock below reorder point
- `MARGIN_TOO_LOW` — discount would create negative margin

---

## Demo Mode

Without a database or API key, the chatbot runs in **demo mode**:
- Calls real backend services (inventory alerts, promotions, analytics)
- Parses user intent from keywords
- Returns structured, data-driven answers

Configure `GEMINI_API_KEY` or `OPENAI_API_KEY` in `.env` for full LLM responses.

---

## Testing

```bash
pytest tests/ -v                           # all tests
pytest tests/unit/ -v                      # unit tests only
pytest tests/integration/ -v               # integration tests only
pytest -k "test_promotion" -v              # filter by name
pytest --tb=short -q                       # compact output
```

---

## Project Structure

```
backend/
├── app/
│   ├── api/v1/           # Route handlers (thin)
│   │   ├── auth.py
│   │   ├── inventory.py
│   │   ├── stores.py
│   │   ├── analytics.py
│   │   ├── promotions.py
│   │   ├── chat.py
│   │   └── deps.py       # JWT guard
│   ├── core/             # Config, DB, logging, security
│   ├── models/           # 16 SQLAlchemy ORM models
│   ├── schemas/          # 10 Pydantic v2 schema sets
│   ├── services/         # Business logic
│   │   ├── auth.py
│   │   ├── inventory.py  # Expiry, alerts, stock calculations
│   │   ├── promotion.py  # Deterministic engine
│   │   ├── analytics.py  # SQL-based analytics
│   │   └── chat.py       # Demo + LLM chatbot
│   └── utils/enums.py    # Shared enumerations
├── alembic/              # Migrations
├── scripts/
│   └── seed_demo.py      # Demo data seeder
├── tests/
│   ├── unit/             # Models, schemas, security
│   └── integration/      # Auth API
├── requirements.txt
└── .env.example
```

---

## Implementation Status

| Phase | Feature | Status |
|---|---|---|
| 0 | Project scaffolding, config, security, DB | ✅ Done |
| 1 | 16 ORM models, 10 schemas, JWT auth | ✅ Done |
| 2 | Inventory service, alerts, expiry monitoring | ✅ Done |
| 3 | SQL analytics (sales, trends, customers, stores) | ✅ Done |
| 4 | Deterministic promotion engine | ✅ Done |
| 5 | Demo chatbot + LLM integration stub | ✅ Done |

### Future Work
- Real-time WebSocket alerts
- LLM tool-use integration (Gemini / GPT-4)
- ML demand forecasting (Prophet / XGBoost)
- Approval workflow for promotions
- Push notification system
- Frontend dashboard (React + Recharts)
