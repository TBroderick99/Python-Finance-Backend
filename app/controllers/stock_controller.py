"""
Stock controller - API endpoints for stock operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.stock import StockCreate, StockResponse, StockUpdate
from app.services.stock_service import StockService

router = APIRouter()


@router.get("/", response_model=list[StockResponse])
async def get_stocks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Return only active stocks"),
    db: Session = Depends(get_db),
):
    """
    Get all stocks with pagination.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **active_only**: Filter to return only active stocks
    """
    service = StockService(db)
    return service.get_all_stocks(skip=skip, limit=limit, active_only=active_only)


@router.get("/search", response_model=list[StockResponse])
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db),
):
    """
    Search stocks by symbol or name.
    
    - **q**: Search query string
    """
    service = StockService(db)
    return service.search_stocks(q)


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock(
    stock_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific stock by ID.
    
    - **stock_id**: The unique identifier of the stock
    """
    service = StockService(db)
    stock = service.get_stock_by_id(stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.get("/symbol/{symbol}", response_model=StockResponse)
async def get_stock_by_symbol(
    symbol: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific stock by ticker symbol.
    
    - **symbol**: The stock ticker symbol (e.g., AAPL, GOOGL)
    """
    service = StockService(db)
    stock = service.get_stock_by_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("/", response_model=StockResponse, status_code=201)
async def create_stock(
    stock_data: StockCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new stock manually.
    
    - **symbol**: Stock ticker symbol
    - **name**: Company name
    - **sector**: Business sector (optional)
    - **industry**: Industry (optional)
    - **exchange**: Stock exchange (optional)
    """
    service = StockService(db)
    
    # Check if already exists
    existing = service.get_stock_by_symbol(stock_data.symbol)
    if existing:
        raise HTTPException(status_code=400, detail="Stock with this symbol already exists")
    
    return service.create_stock(stock_data)


@router.post("/fetch/{symbol}", response_model=StockResponse)
async def fetch_and_add_stock(
    symbol: str,
    db: Session = Depends(get_db),
):
    """
    Fetch stock info from external source and add to database.
    
    - **symbol**: Stock ticker symbol to fetch
    """
    service = StockService(db)
    stock = service.add_stock_from_symbol(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found in external sources")
    return stock


@router.put("/{stock_id}", response_model=StockResponse)
async def update_stock(
    stock_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing stock.
    
    - **stock_id**: The unique identifier of the stock
    """
    service = StockService(db)
    stock = service.update_stock(stock_id, stock_data)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.delete("/{stock_id}", status_code=204)
async def delete_stock(
    stock_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a stock.
    
    - **stock_id**: The unique identifier of the stock
    """
    service = StockService(db)
    if not service.delete_stock(stock_id):
        raise HTTPException(status_code=404, detail="Stock not found")
    return None
