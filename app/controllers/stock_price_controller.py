"""
Stock Price controller - API endpoints for stock price operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.schemas.stock_price import (
    StockPriceResponse,
    StockPriceFetchRequest,
    StockPriceStats,
)
from app.services.stock_service import StockService
from app.services.projection_service import ProjectionService
from app.repositories.stock_price_repository import StockPriceRepository
from app.repositories.stock_repository import StockRepository

router = APIRouter()


@router.get("/{stock_id}", response_model=list[StockPriceResponse])
async def get_stock_prices(
    stock_id: int,
    start_date: Optional[date] = Query(None, description="Start date for price range"),
    end_date: Optional[date] = Query(None, description="End date for price range"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """
    Get historical prices for a stock.
    
    - **stock_id**: The unique identifier of the stock
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    - **limit**: Maximum number of records to return
    """
    stock_repo = StockRepository(db)
    stock = stock_repo.get_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    price_repo = StockPriceRepository(db)
    return price_repo.get_by_stock_id(
        stock_id=stock_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.get("/symbol/{symbol}", response_model=list[StockPriceResponse])
async def get_stock_prices_by_symbol(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date for price range"),
    end_date: Optional[date] = Query(None, description="End date for price range"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """
    Get historical prices for a stock by symbol.
    
    - **symbol**: Stock ticker symbol
    - **start_date**: Optional start date filter
    - **end_date**: Optional end date filter
    - **limit**: Maximum number of records to return
    """
    stock_repo = StockRepository(db)
    stock = stock_repo.get_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    price_repo = StockPriceRepository(db)
    return price_repo.get_by_stock_id(
        stock_id=stock.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.post("/fetch")
async def fetch_stock_prices(
    request: StockPriceFetchRequest,
    db: Session = Depends(get_db),
):
    """
    Fetch stock prices from external source and store in database.
    
    - **symbol**: Stock ticker symbol
    - **start_date**: Optional start date for historical data
    - **end_date**: Optional end date for historical data
    - **period**: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    """
    service = StockService(db)
    result = service.fetch_and_store_prices(
        symbol=request.symbol,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period or "1mo",
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch prices"))
    
    return result


@router.get("/{stock_id}/stats", response_model=StockPriceStats)
async def get_stock_price_stats(
    stock_id: int,
    db: Session = Depends(get_db),
):
    """
    Get statistics for stock prices.
    
    - **stock_id**: The unique identifier of the stock
    """
    stock_repo = StockRepository(db)
    stock = stock_repo.get_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    price_repo = StockPriceRepository(db)
    stats = price_repo.get_stats(stock_id)
    
    if not stats.get("total_records"):
        raise HTTPException(status_code=404, detail="No price data found for this stock")
    
    return StockPriceStats(symbol=stock.symbol, **stats)


@router.get("/{stock_id}/moving-average")
async def get_moving_average(
    stock_id: int,
    window: int = Query(20, ge=5, le=200, description="Moving average window"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
):
    """
    Calculate moving average for a stock.
    
    - **stock_id**: The unique identifier of the stock
    - **window**: Moving average window (default 20 days)
    - **start_date**: Optional start date
    - **end_date**: Optional end date
    """
    projection_service = ProjectionService(db)
    result = projection_service.calculate_moving_average(
        stock_id=stock_id,
        window=window,
        start_date=start_date,
        end_date=end_date,
    )
    
    if not result:
        raise HTTPException(status_code=400, detail="Insufficient data for moving average calculation")
    
    return result


@router.get("/{stock_id}/projection")
async def get_price_projection(
    stock_id: int,
    days_ahead: int = Query(30, ge=1, le=365, description="Days to project"),
    lookback_days: int = Query(90, ge=10, le=365, description="Historical days for trend"),
    db: Session = Depends(get_db),
):
    """
    Calculate simple price projection based on historical trend.
    
    - **stock_id**: The unique identifier of the stock
    - **days_ahead**: Number of days to project into the future
    - **lookback_days**: Number of historical days to use for trend calculation
    """
    projection_service = ProjectionService(db)
    result = projection_service.calculate_simple_projection(
        stock_id=stock_id,
        days_ahead=days_ahead,
        lookback_days=lookback_days,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/{stock_id}/volatility")
async def get_volatility(
    stock_id: int,
    lookback_days: int = Query(30, ge=5, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
):
    """
    Calculate price volatility for a stock.
    
    - **stock_id**: The unique identifier of the stock
    - **lookback_days**: Number of days to analyze
    """
    projection_service = ProjectionService(db)
    result = projection_service.calculate_volatility(
        stock_id=stock_id,
        lookback_days=lookback_days,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
