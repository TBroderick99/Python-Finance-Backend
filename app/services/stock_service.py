"""
Stock service - Business logic for stock operations.
"""
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
import logging

from app.models.stock import Stock
from app.schemas.stock import StockCreate, StockUpdate
from app.repositories.stock_repository import StockRepository
from app.repositories.stock_price_repository import StockPriceRepository
from app.services.stock_data_fetcher import StockDataFetcher

logger = logging.getLogger(__name__)


class StockService:
    """Service for managing stocks."""
    
    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.price_repo = StockPriceRepository(db)
        self.data_fetcher = StockDataFetcher()
    
    def get_all_stocks(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> list[Stock]:
        """Get all stocks."""
        return self.stock_repo.get_all(skip=skip, limit=limit, active_only=active_only)
    
    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """Get stock by ID."""
        return self.stock_repo.get_by_id(stock_id)
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Get stock by symbol."""
        return self.stock_repo.get_by_symbol(symbol)
    
    def create_stock(self, stock_data: StockCreate) -> Stock:
        """Create a new stock."""
        return self.stock_repo.create(stock_data)
    
    def update_stock(self, stock_id: int, stock_data: StockUpdate) -> Optional[Stock]:
        """Update an existing stock."""
        stock = self.stock_repo.get_by_id(stock_id)
        if not stock:
            return None
        return self.stock_repo.update(stock, stock_data)
    
    def delete_stock(self, stock_id: int) -> bool:
        """Delete a stock."""
        stock = self.stock_repo.get_by_id(stock_id)
        if not stock:
            return False
        self.stock_repo.delete(stock)
        return True
    
    def search_stocks(self, query: str) -> list[Stock]:
        """Search stocks by symbol or name."""
        return self.stock_repo.search(query)
    
    def add_stock_from_symbol(self, symbol: str) -> Optional[Stock]:
        """
        Add a new stock by fetching its info from external source.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Created Stock or None if not found
        """
        # Check if already exists
        existing = self.stock_repo.get_by_symbol(symbol)
        if existing:
            return existing
        
        # Fetch info from external source
        info = self.data_fetcher.get_stock_info(symbol)
        if not info:
            return None
        
        # Create stock
        stock_data = StockCreate(**info)
        return self.stock_repo.create(stock_data)
    
    def fetch_and_store_prices(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "1mo"
    ) -> dict:
        """
        Fetch historical prices and store them in database.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Optional start date
            end_date: Optional end date
            period: Period string if dates not provided
            
        Returns:
            Dictionary with fetch results
        """
        # Ensure stock exists
        stock = self.add_stock_from_symbol(symbol)
        if not stock:
            return {"success": False, "error": f"Stock {symbol} not found"}
        
        # Fetch prices
        prices = self.data_fetcher.get_historical_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        
        if not prices:
            return {"success": False, "error": "No price data found"}
        
        # Add stock_id to each price record
        for price in prices:
            price["stock_id"] = stock.id
        
        # Store prices
        created_count = self.price_repo.bulk_create(prices)
        
        return {
            "success": True,
            "stock_id": stock.id,
            "symbol": symbol,
            "total_fetched": len(prices),
            "new_records": created_count,
        }
