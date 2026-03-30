# Real-Time Portfolio Tracker with AI Insights

A full-stack portfolio tracking application that connects to real brokerage accounts via Plaid, displays real-time market data, and provides ML-powered insights including price predictions and sentiment analysis.

## Features

- **Brokerage Integration** — Connect real investment accounts through Plaid (Limited Production access)
- **Real-Time Market Data** — Live stock prices via Yahoo Finance
- **Portfolio Dashboard** — View holdings, total value, gain/loss calculations, and allocation charts
- **ML Price Predictions** — Next-day price forecasts using a Random Forest model with technical indicators (SMA, EMA, RSI) and confidence scoring based on inter-tree variance
- **Sentiment Analysis** — FinBERT-powered news sentiment for each holding, sourced from NewsAPI
- **Expandable Insights** — Click any holding to reveal AI predictions and sentiment inline

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, Python  
**Frontend:** React 18, TypeScript  
**Data:** Yahoo Finance (yfinance), Plaid API, NewsAPI  
**ML:** scikit-learn (Random Forest), Hugging Face Transformers (FinBERT), pandas, ta (technical analysis)  
**Database:** SQLite (dev) / PostgreSQL via Supabase (production)

## Project Structure

```
portfolio-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── database.py          # SQLAlchemy engine & session config
│   │   ├── models/
│   │   │   └── user.py          # User and Holding ORM models
│   │   ├── routes/
│   │   │   └── plaid.py         # All API endpoints (Plaid, portfolio, ML)
│   │   └── services/
│   │       ├── plaid_service.py      # Plaid Link & holdings integration
│   │       ├── market_data.py        # Yahoo Finance price fetching
│   │       ├── ml_predictor.py       # Random Forest stock predictor
│   │       └── sentiment_analyzer.py # FinBERT sentiment analysis
│   ├── requirements.txt
│   ├── test_ml.py               # ML prediction test script
│   ├── test_sentiment.py        # Sentiment analysis test script
│   └── test_prices.py           # Live price update test script
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root component with auth flow
│   │   ├── components/
│   │   │   ├── Dashboard.tsx    # Main portfolio dashboard
│   │   │   ├── PlaidLink.tsx    # Plaid Link connection button
│   │   │   ├── AllocationChart.tsx  # Portfolio allocation pie chart
│   │   │   └── MLInsights.tsx   # Expandable AI insights per holding
│   │   ├── services/
│   │   │   └── api.ts           # API client functions
│   │   └── styles/
│   │       └── MLInsights.css   # ML insights styling
│   └── package.json
└── .gitignore
```

## Prerequisites

- **Python 3.9+**
- **Node.js 16+** and npm
- **API Keys** (see Environment Variables below)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/portfolio-tracker.git
cd portfolio-tracker
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Plaid
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox               # sandbox | production

# News API (for sentiment analysis)
NEWSAPI_KEY=your_newsapi_key

# Database (optional — defaults to SQLite)
DATABASE_URL=sqlite:///./portfolio.db
```

**Where to get keys:**
- **Plaid** — Sign up at [dashboard.plaid.com](https://dashboard.plaid.com). Enable the "Investments" product under Allowed Use Cases in your team settings.
- **NewsAPI** — Register at [newsapi.org](https://newsapi.org) for a free developer key.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

Optionally create a `.env` file in `frontend/` if the backend runs on a non-default host:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 5. Start the Application

**Start the backend** (from the `backend/` directory):

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger documentation.

**Start the frontend** (from the `frontend/` directory, in a separate terminal):

```bash
npm start
```

The app will open at `http://localhost:3000`.

## Usage

1. **Connect an account** — Click "Connect Your Account" to link a brokerage through Plaid, or click "Use Test Portfolio" to load sample data (AAPL, GOOGL, MSFT, TSLA).
2. **View your dashboard** — See total portfolio value, gain/loss, and an allocation chart.
3. **Explore AI insights** — Click on any holding row to expand ML predictions and sentiment analysis.
4. **Refresh** — Hit the "Refresh Portfolio" button to pull the latest prices.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/plaid/create_link_token` | Generate a Plaid Link token |
| `POST` | `/plaid/exchange_public_token` | Exchange Plaid public token for access token |
| `POST` | `/plaid/sync_portfolio?user_id={id}` | Sync holdings from Plaid |
| `POST` | `/plaid/update_prices/{user_id}` | Update current prices from Yahoo Finance |
| `GET` | `/plaid/portfolio/{user_id}` | Get portfolio with calculated values |
| `GET` | `/plaid/portfolio/{user_id}/holdings` | Get raw holdings data |
| `POST` | `/plaid/create_test_portfolio` | Create a test user with sample holdings |
| `GET` | `/plaid/ml/predict/{symbol}` | Get ML price prediction for a stock |
| `GET` | `/plaid/ml/sentiment/{symbol}` | Get FinBERT sentiment analysis for a stock |
| `GET` | `/plaid/ml/portfolio-predictions/{user_id}` | Get predictions for all holdings |
| `GET` | `/plaid/ml/portfolio-insights/{user_id}` | Get predictions + sentiment for all holdings |

## Running Tests

The project includes standalone test scripts you can run against a live backend:

```bash
cd backend

# Test live price updates
python test_prices.py

# Test ML predictions
python test_ml.py

# Test sentiment analysis
python test_sentiment.py
```

Make sure the backend server is running before executing the tests.

## Deployment

**Frontend (Netlify):**

```bash
cd frontend
npm run build
# Deploy the build/ folder to Netlify
```

Set the `REACT_APP_API_URL` environment variable in Netlify to point to your deployed backend.

**Backend (Render / Railway):**

Deploy the `backend/` directory with the start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set all `.env` variables in the hosting platform's environment settings. For production, switch `DATABASE_URL` to a hosted PostgreSQL instance (e.g., Supabase) since container-based hosts reset local files between deploys.