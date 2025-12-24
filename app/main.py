"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import create_tables
from app.controllers import stock_controller, stock_price_controller

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - runs on startup and shutdown."""
    # Startup: Create database tables
    create_tables()
    yield
    # Shutdown: Cleanup if needed


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Stock Market Finance Application API
    
    This API provides endpoints for:
    - **Stocks**: Manage stock entities (CRUD operations)
    - **Stock Prices**: Fetch and store historical stock price data
    - **Projections**: Calculate future projections based on historical data
    
    ### Data Sources
    - Yahoo Finance (yfinance)
    - Alpha Vantage (optional, requires API key)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    stock_controller.router,
    prefix="/api/v1/stocks",
    tags=["Stocks"],
)

app.include_router(
    stock_price_controller.router,
    prefix="/api/v1/prices",
    tags=["Stock Prices"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check."""
    return {
        "message": "Stock Market Finance API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
