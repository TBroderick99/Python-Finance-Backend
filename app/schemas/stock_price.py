"""
Pydantic schemas for StockPrice entity.
"""
from pydantic import BaseModel, Field
from datetime import date as date_type, datetime
from typing import Optional


class StockPriceBase(BaseModel):
    """Base schema with common stock price attributes."""
    date: date_type = Field(..., description="Trading date")
    open_price: Optional[float] = Field(None, ge=0, description="Opening price")
    high_price: Optional[float] = Field(None, ge=0, description="Day's high price")
    low_price: Optional[float] = Field(None, ge=0, description="Day's low price")
    close_price: float = Field(..., ge=0, description="Closing price")
    adj_close: Optional[float] = Field(None, ge=0, description="Adjusted closing price")
    volume: Optional[int] = Field(None, ge=0, description="Trading volume")


class StockPriceCreate(StockPriceBase):
    """Schema for creating a new stock price record."""
    stock_id: int = Field(..., description="Stock ID")


class StockPriceResponse(StockPriceBase):
    """Schema for stock price response."""
    id: int
    stock_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class StockPriceFetchRequest(BaseModel):
    """Schema for requesting stock price data fetch."""
    symbol: str = Field(..., description="Stock ticker symbol")
    start_date: Optional[date_type] = Field(None, description="Start date for historical data")
    end_date: Optional[date_type] = Field(None, description="End date for historical data")
    period: Optional[str] = Field("1mo", description="Period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")


class StockPriceStats(BaseModel):
    """Statistics for stock price data."""
    symbol: str
    min_price: float
    max_price: float
    avg_price: float
    total_records: int
    date_range_start: date_type
    date_range_end: date_type
