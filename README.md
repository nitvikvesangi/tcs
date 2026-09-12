# QuickAI — Quick Commerce Retail Intelligence Platform

AI-powered promotion planner, inventory intelligence, and retail analytics for quick-commerce dark-store networks.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![React](https://img.shields.io/badge/React-19-61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![Tailwind](https://img.shields.io/badge/Tailwind-4.0-38B2AC)

## What It Does

- **Dashboard** — KPI cards, inventory health charts, demand signal trends
- **AI Recommendations** — Deterministic promotion engine analyzes stock, margins, demand, competitor pricing, weather, and expiry to recommend actions
- **Inventory Intelligence** — Real-time alerts for stockout risk, overstock, and near-expiry products
- **Promotion Planner** — Compare discount scenarios with projected revenue, profit, and inventory impact
- **Analytics** — Sales trends, demand distribution, action breakdown charts
- **AI Chatbot** — Ask questions in plain English, get data-driven answers powered by Groq LLM with real inventory context

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite + Tailwind CSS 4 + Recharts |
| Backend | FastAPI + Uvicorn |
| AI / LLM | Groq (Qwen 3.8-27B) |
| Data | JSON dataset with 100+ products across 5 cities |

## Quick Start

### 1. Clone

```bash
git clone https://github.com/nitvikvesangi/tcs.git
cd tcs
```

### 2. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install fastapi uvicorn pydantic pydantic-settings groq
```

### 3. Install frontend & build

```bash
cd dashboard
npm install
npm run build
cd ..
```

### 4. Set environment variable

```bash
export GROQ_API_KEY="your-groq-api-key"   # free at console.groq.com/keys
```

### 5. Run

```bash
cd server
python main.py
```

Open **http://localhost:8000** — that's it. One URL, everything works.

## Project Structure

```
├── server/                  # FastAPI backend (unified server)
│   ├── main.py              # Entry point — serves API + React frontend
│   ├── services/
│   │   ├── recommendation_service.py   # Promotion engine
│   │   └── chat_service.py             # AI chatbot (Groq LLM)
│   ├── schemas/             # Pydantic models
│   ├── data/dataset.json    # Product & inventory dataset
│   ├── inventory_engine.py  # Stock alert calculations
│   ├── promotion_engine.py  # Discount scenario generator
│   └── ai_engine.py         # Explanation & risk flag generator
│
├── dashboard/               # React frontend
│   ├── src/
│   │   ├── pages/           # Dashboard, Inventory, Promotions, Analytics
│   │   ├── components/      # UI components + AI Chatbot
│   │   └── services/        # API client
│   ├── package.json
│   └── vite.config.js
│
└── .gitignore
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/recommendations` | AI promotion recommendations (filterable by city, category, store) |
| GET | `/inventory` | Inventory overview with alerts |
| GET | `/promotions` | Products recommended for promotion |
| POST | `/chat` | AI chatbot — ask anything about your inventory |
| GET | `/api/health` | Health check |
| GET | `/api/docs` | Swagger API documentation |

## Screenshots

The dashboard includes:
- 📊 KPI cards (total products, promotions, stockout risk, expiry alerts)
- 📈 Inventory health pie chart + demand signal line chart
- 🏷️ Promotion cards with discount scenarios and projected impact
- 🤖 AI chatbot that references real product data

## Team

Built for TCS Hackathon.
