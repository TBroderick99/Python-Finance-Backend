"""
Projection service - Business logic for stock price projections.
"""
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
import numpy as np
import logging

from app.repositories.stock_price_repository import StockPriceRepository
from app.repositories.stock_repository import StockRepository

logger = logging.getLogger(__name__)


class ProjectionService:
    """Service for calculating stock price projections."""
    
    def __init__(self, db: Session):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.price_repo = StockPriceRepository(db)
    
    def calculate_moving_average(
        self,
        stock_id: int,
        window: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> list[dict]:
        """
        Calculate moving average for a stock.
        
        Args:
            stock_id: Stock ID
            window: Moving average window (default 20 days)
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of dates with moving averages
        """
        prices = self.price_repo.get_by_stock_id(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        if len(prices) < window:
            return []
        
        # Sort by date ascending
        prices = sorted(prices, key=lambda x: x.date)
        close_prices = [p.close_price for p in prices]
        
        # Calculate moving average
        results = []
        for i in range(window - 1, len(prices)):
            window_prices = close_prices[i - window + 1:i + 1]
            ma = sum(window_prices) / window
            results.append({
                "date": prices[i].date,
                "close_price": prices[i].close_price,
                "moving_average": round(ma, 2),
            })
        
        return results
    
    def calculate_simple_projection(
        self,
        stock_id: int,
        days_ahead: int = 30,
        lookback_days: int = 90
    ) -> dict:
        """
        Calculate a simple linear projection based on recent trend.
        
        Args:
            stock_id: Stock ID
            days_ahead: Number of days to project
            lookback_days: Number of historical days to use for trend
            
        Returns:
            Dictionary with projection data
        """
        prices = self.price_repo.get_by_stock_id(
            stock_id=stock_id,
            limit=lookback_days
        )
        
        if len(prices) < 10:
            return {"error": "Insufficient historical data"}
        
        # Sort by date ascending
        prices = sorted(prices, key=lambda x: x.date)
        
        # Calculate linear regression
        x = np.arange(len(prices))
        y = np.array([p.close_price for p in prices])
        
        # Simple linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate projected prices
        last_date = prices[-1].date
        projections = []
        
        for i in range(1, days_ahead + 1):
            projected_date = last_date + timedelta(days=i)
            projected_price = intercept + slope * (len(prices) + i - 1)
            projections.append({
                "date": projected_date,
                "projected_price": round(max(0, projected_price), 2),
            })
        
        # Calculate confidence metrics
        y_predicted = intercept + slope * x
        r_squared = 1 - (np.sum((y - y_predicted) ** 2) / np.sum((y - np.mean(y)) ** 2))
        
        return {
            "stock_id": stock_id,
            "last_price": prices[-1].close_price,
            "last_date": last_date,
            "trend": "bullish" if slope > 0 else "bearish",
            "daily_change_rate": round(slope, 4),
            "r_squared": round(r_squared, 4),
            "projections": projections,
        }
    
    def calculate_volatility(self, stock_id: int, lookback_days: int = 30) -> dict:
        """
        Calculate price volatility.
        
        Args:
            stock_id: Stock ID
            lookback_days: Number of days to analyze
            
        Returns:
            Dictionary with volatility metrics
        """
        prices = self.price_repo.get_by_stock_id(stock_id=stock_id, limit=lookback_days)
        
        if len(prices) < 2:
            return {"error": "Insufficient data"}
        
        # Sort by date ascending
        prices = sorted(prices, key=lambda x: x.date)
        close_prices = np.array([p.close_price for p in prices])
        
        # Calculate daily returns
        returns = np.diff(close_prices) / close_prices[:-1]
        
        # Calculate metrics
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        avg_return = np.mean(returns)
        
        return {
            "stock_id": stock_id,
            "period_days": len(prices),
            "volatility": round(volatility * 100, 2),  # As percentage
            "avg_daily_return": round(avg_return * 100, 4),  # As percentage
            "min_price": round(min(close_prices), 2),
            "max_price": round(max(close_prices), 2),
            "price_range_pct": round((max(close_prices) - min(close_prices)) / min(close_prices) * 100, 2),
        }
