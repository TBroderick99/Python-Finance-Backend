"""
StockPrice repository - Database operations for StockPrice entity.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import date
from typing import Optional

from app.models.stock_price import StockPrice
from app.schemas.stock_price import StockPriceCreate


class StockPriceRepository:
    """Repository for StockPrice database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_stock_id(
        self, 
        stock_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000
    ) -> list[StockPrice]:
        """Get stock prices for a specific stock with optional date range."""
        query = select(StockPrice).where(StockPrice.stock_id == stock_id)
        
        if start_date:
            query = query.where(StockPrice.date >= start_date)
        if end_date:
            query = query.where(StockPrice.date <= end_date)
        
        query = query.order_by(StockPrice.date.desc()).limit(limit)
        return list(self.db.execute(query).scalars().all())
    
    def get_latest(self, stock_id: int) -> Optional[StockPrice]:
        """Get the most recent price for a stock."""
        query = (
            select(StockPrice)
            .where(StockPrice.stock_id == stock_id)
            .order_by(StockPrice.date.desc())
            .limit(1)
        )
        return self.db.execute(query).scalar_one_or_none()
    
    def get_by_date(self, stock_id: int, price_date: date) -> Optional[StockPrice]:
        """Get stock price for a specific date."""
        query = select(StockPrice).where(
            and_(StockPrice.stock_id == stock_id, StockPrice.date == price_date)
        )
        return self.db.execute(query).scalar_one_or_none()
    
    def create(self, price_data: StockPriceCreate) -> StockPrice:
        """Create a new stock price record."""
        price = StockPrice(**price_data.model_dump())
        self.db.add(price)
        self.db.commit()
        self.db.refresh(price)
        return price
    
    def bulk_create(self, prices: list[dict]) -> int:
        """Bulk create stock price records. Returns count of created records."""
        created = 0
        for price_data in prices:
            # Check if record exists
            existing = self.get_by_date(price_data["stock_id"], price_data["date"])
            if not existing:
                price = StockPrice(**price_data)
                self.db.add(price)
                created += 1
        
        self.db.commit()
        return created
    
    def get_stats(self, stock_id: int) -> dict:
        """Get statistics for stock prices."""
        query = select(
            func.min(StockPrice.close_price).label("min_price"),
            func.max(StockPrice.close_price).label("max_price"),
            func.avg(StockPrice.close_price).label("avg_price"),
            func.count(StockPrice.id).label("total_records"),
            func.min(StockPrice.date).label("date_range_start"),
            func.max(StockPrice.date).label("date_range_end"),
        ).where(StockPrice.stock_id == stock_id)
        
        result = self.db.execute(query).one()
        return {
            "min_price": result.min_price,
            "max_price": result.max_price,
            "avg_price": result.avg_price,
            "total_records": result.total_records,
            "date_range_start": result.date_range_start,
            "date_range_end": result.date_range_end,
        }
    
    def delete_by_stock_id(self, stock_id: int) -> int:
        """Delete all prices for a stock. Returns count of deleted records."""
        query = select(StockPrice).where(StockPrice.stock_id == stock_id)
        prices = self.db.execute(query).scalars().all()
        count = len(prices)
        for price in prices:
            self.db.delete(price)
        self.db.commit()
        return count
