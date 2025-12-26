# Stock Market Finance Application

Backend of application for fetching, storing, and analyzing stock market data.

## Architecture

### Backend (FastAPI)
- **MVC Pattern** with Repository layer for clean separation of concerns
- **Swagger/OpenAPI** documentation at `/docs`
- **SQLite** database for development (easily switchable to PostgreSQL)

```
backend/
├── app/
│   ├── core/           # Configuration, database setup
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic validation schemas
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic
│   ├── controllers/    # API route handlers
│   └── main.py         # FastAPI application entry
└── requirements.txt
```

## Setup

### Backend Setup

```bash
# IMPORTANT: USE PYTHON 3.12 IN THE VENV

cd backend

# Create virtual environment
py -3.12 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Data Sources

- **Yahoo Finance** (via yfinance) - Primary data source for stock information and prices
- **Alpha Vantage** (optional) - Can be integrated for additional market data

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, yfinance
- **Database**: SQLite (development)
