"""
Pydantic schemas for Stock entity.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    """Base schema with common stock attributes."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    sector: Optional[str] = Field(None, max_length=100, description="Business sector")
    industry: Optional[str] = Field(None, max_length=100, description="Specific industry")
    exchange: Optional[str] = Field(None, max_length=50, description="Stock exchange")


class StockCreate(StockBase):
    """Schema for creating a new stock."""
    pass


class StockUpdate(BaseModel):
    """Schema for updating an existing stock."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    exchange: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class StockResponse(StockBase):
    """Schema for stock response with all fields."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockWithPrices(StockResponse):
    """Stock response including recent prices."""
    prices: list["StockPriceResponse"] = []
    
    class Config:
        from_attributes = True


# Import here to avoid circular imports
from app.schemas.stock_price import StockPriceResponse
StockWithPrices.model_rebuild()
