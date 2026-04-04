# StockWise 📈

> A production-grade AI-powered paper trading platform that helps students learn investing using virtual money with real NSE market data.

[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-FF6B35?style=flat)](https://groq.com)

---

## 🎯 What is StockWise?

StockWise is a full-stack paper trading simulator built for students who want to learn stock market investing without financial risk. Users start with a virtual balance and trade real NSE-listed stocks at real market prices. Every trade, every gain, every loss — all simulated with real data.

The platform goes beyond a basic simulator. It features a live AI chatbot (FinBot) powered by LLaMA 3.3 70B, post-trade ML behavioral analysis, a competitive leaderboard, daily market stories, and a real-time 3D trading interface built with Three.js and Anime.js.

Built as a hackathon project in 48 hours. Fully deployed and production-ready.

---

## 🚀 Live Demo

- **Frontend:** [https://stockwise.netlify.app](https://stockwise.netlify.app)
- **Backend API:** [https://stockwise-backend.railway.app](https://stockwise-backend.railway.app)

---

## ✨ Features

### 🔐 Authentication & Wallets
- JWT-based authentication with access and refresh token rotation
- Atomic user creation — one request simultaneously creates the user account, wallet (with starting virtual balance), and portfolio using Django's atomic transactions
- Zero race conditions on account creation — if any step fails, everything rolls back

### 📊 Real-Time Market Data
- Live NSE stock prices fetched from **yfinance** and **Finnhub** APIs
- Three-layer caching with **Redis** — price data cached to avoid redundant API calls
- **WebSocket streaming** via Django Channels — frontend receives live price updates every 5 seconds
- Fallback mechanism between data sources — if one API fails, the other takes over
- Weekend/off-hours price simulation for continuous demo availability

### ⚡ Trading Engine
- Supports three order types:
  - **Market Orders** — execute immediately at current price
  - **Limit Orders** — execute only when stock hits target price
  - **Stop-Loss Orders** — automatically sell to prevent runaway losses
- Race condition prevention using `select_for_update()` database locking — multiple users buying the same stock simultaneously never causes balance corruption
- Full trade history with timestamps, P&L per trade, and order status tracking
- Celery-powered background worker processes pending limit and stop-loss orders continuously

### 💼 Portfolio Analytics
- Daily portfolio snapshots stored for historical performance tracking
- Comprehensive analytics: win rate, average win, average loss, expectancy, profit factor
- Per-stock breakdown showing which tickers the user performs best and worst on
- Platform-wide **leaderboard** ranking users by portfolio performance
- P&L history charts with full trade-by-trade breakdown

### 🤖 FinBot — AI Trading Assistant
- Powered by **Groq API** running **LLaMA 3.3 70B** — one of the fastest LLM inference providers
- Full conversation history maintained per user across sessions
- Real-time price enrichment — if you ask about TCS, FinBot automatically fetches the live price and includes it in context
- **Multi-layer prompt injection protection:**
  - Layer 1: Pattern-based injection detection (blocks jailbreak attempts, persona switching, override commands)
  - Layer 2: Finance topic validation — only finance-related queries reach the LLM
  - Layer 3: System prompt hardening with explicit security rules baked into every request
- Automatic model fallback — if primary model fails, system tries backup models automatically
- FinBot refuses to discuss anything outside finance, markets, and investing — no exceptions

### 🧠 ML Trading Insights
- Post-trade behavioral analysis triggered automatically after every completed trade
- Analyzes trading patterns including:
  - **Win rate** and confidence intervals
  - **Profit factor** (total wins / total losses)
  - **Expectancy** — average expected return per trade
  - **Holding time analysis** — compares how long the user holds winning vs losing positions
  - **Segmentation** by time of day, day of week, market direction, and volatility regime
- Generates a full natural language AI report using Groq, personalized to the user's specific trading patterns
- Detects behavioral biases like panic selling, holding losers too long, and overtrading

### 📰 Daily Market Stories
- Celery Beat scheduler automatically generates daily market stories
- AI-written summaries of market conditions, sector performance, and notable stock movements
- Delivered fresh every trading day

---

## 🏗️ Architecture

```
StockWise Backend
├── core/                  # Django project settings, URLs, Celery config
├── users/                 # Auth, JWT, user management
├── market/                # Price fetching, WebSocket, search, top movers
│   ├── tasks.py           # Celery tasks: price cache warming
│   └── consumers.py       # Django Channels WebSocket consumer
├── trading/               # Orders, portfolio, leaderboard, analytics
│   ├── views.py           # Buy, sell, portfolio, history, insights endpoints
│   └── tasks.py           # Celery tasks: limit/stop-loss order processing
├── chatbot/               # FinBot conversation management
├── stories/               # Daily AI market stories
└── services/
    ├── chatbot_services.py  # Groq integration, injection protection, ML prompts
    └── price_service.py     # yfinance + Finnhub with Redis caching
```

### Data Flow

```
Frontend (React/Vite)
    ↓ REST API calls (axios + JWT)
Django REST Framework
    ↓ Database operations
PostgreSQL (primary data store)
    ↓ Cache layer
Redis (price cache + Celery broker)
    ↓ Background tasks
Celery Worker (order processing, cache warming)
Celery Beat (scheduled stories, daily snapshots)
    ↓ External APIs
yfinance + Finnhub (market data)
Groq LLaMA 3.3 70B (AI responses)
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Django 5.2 + DRF | REST API framework |
| PostgreSQL | Primary database |
| Redis | Caching + Celery message broker |
| Celery | Background task processing |
| Celery Beat | Scheduled tasks |
| Django Channels | WebSocket support |
| SimpleJWT | JWT authentication |
| yfinance | NSE market data |
| Finnhub API | Backup market data source |
| Groq (LLaMA 3.3 70B) | AI chatbot + ML report generation |
| Gunicorn | Production WSGI server |
| Railway | Backend deployment |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 + TypeScript | UI framework |
| Vite | Build tool |
| Tailwind CSS | Styling |
| Three.js | 3D neural network animations |
| Anime.js | UI micro-animations |
| Recharts | Stock price charts |
| Axios | API communication |
| shadcn/ui | Component library |
| Netlify | Frontend deployment |

---

## 🔧 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/stockwise-backend.git
cd stockwise-backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Fill in your .env with the values below

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Environment Variables

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/stockwise
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=your_groq_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Start the Backend (4 terminals)

```bash
# Terminal 1 — Redis (start this first)
redis-server

# Terminal 2 — Django
python manage.py runserver

# Terminal 3 — Celery worker
celery -A core worker --pool=solo --loglevel=info

# Terminal 4 — Celery beat
celery -A core beat --loglevel=info
```

### Frontend Setup

```bash
# Clone the frontend repo
git clone https://github.com/yourusername/stockwise-frontend.git
cd stockwise-frontend

# Install dependencies
npm install

# Set environment variable
echo "VITE_API_URL=http://127.0.0.1:8000" > .env

# Start dev server
npm run dev
```

---

## 📡 API Endpoints

### Authentication
```
POST /api/users/signup/         — Register new user
POST /api/users/login/          — Login, returns JWT tokens
POST /api/users/token/refresh/  — Refresh access token
```

### Market Data
```
GET /api/market/price/<ticker>/   — Live stock price
GET /api/market/search/?q=<query> — Search NSE stocks
GET /api/market/top-movers/       — Top gainers and losers
```

### Trading
```
POST /api/trading/buy/            — Market buy order
POST /api/trading/sell/           — Market sell order
POST /api/trading/order/          — Place limit/stop-loss order
GET  /api/trading/portfolio/      — Current holdings + summary
GET  /api/trading/history/        — Trade history
GET  /api/trading/orders/         — Pending orders
DELETE /api/trading/order/<id>/   — Cancel pending order
GET  /api/trading/pnl-history/    — P&L over time
GET  /api/trading/insights/       — ML trading analysis
```

### Chatbot
```
POST /api/chatbot/message/        — Send message to FinBot
```

### Stories
```
GET /api/stories/                 — All market stories
GET /api/stories/today/           — Today's story
```

---

## 🔒 Security Highlights

- JWT tokens with short expiry + automatic refresh rotation
- `select_for_update()` database locking prevents race conditions in concurrent trades
- Atomic database transactions ensure wallet/portfolio consistency
- Multi-layer AI prompt injection protection in FinBot
- CORS configured to only allow whitelisted frontend origins
- Environment variables for all secrets — nothing hardcoded

---

## 👨‍💻 Built By

**Veer** — Backend Architecture, Django REST API, Database Design, AI/ML Integration, Deployment

Built at **Paradox Hacks** — 48 hours, fully deployed, production-ready.

---

## 📄 License

MIT License — feel free to use, modify, and build on this.
