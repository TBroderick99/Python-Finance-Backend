"""
Stock repository - Database operations for Stock entity.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from app.models.stock import Stock
from app.schemas.stock import StockCreate, StockUpdate


class StockRepository:
    """Repository for Stock database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> list[Stock]:
        """Get all stocks with pagination."""
        query = select(Stock)
        if active_only:
            query = query.where(Stock.is_active == True)
        query = query.offset(skip).limit(limit)
        return list(self.db.execute(query).scalars().all())
    
    def get_by_id(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID."""
        return self.db.get(Stock, stock_id)
    
    def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get stock by ticker symbol."""
        query = select(Stock).where(Stock.symbol == symbol.upper())
        return self.db.execute(query).scalar_one_or_none()
    
    def create(self, stock_data: StockCreate) -> Stock:
        """Create a new stock."""
        stock = Stock(
            symbol=stock_data.symbol.upper(),
            name=stock_data.name,
            sector=stock_data.sector,
            industry=stock_data.industry,
            exchange=stock_data.exchange,
        )
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock
    
    def update(self, stock: Stock, stock_data: StockUpdate) -> Stock:
        """Update an existing stock."""
        update_data = stock_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(stock, field, value)
        self.db.commit()
        self.db.refresh(stock)
        return stock
    
    def delete(self, stock: Stock) -> None:
        """Delete a stock."""
        self.db.delete(stock)
        self.db.commit()
    
    def search(self, query: str, limit: int = 20) -> list[Stock]:
        """Search stocks by symbol or name."""
        search_query = select(Stock).where(
            (Stock.symbol.ilike(f"%{query}%")) | 
            (Stock.name.ilike(f"%{query}%"))
        ).limit(limit)
        return list(self.db.execute(search_query).scalars().all())
