"""
Stock SQLAlchemy model - represents a stock entity.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Stock(Base):
    """
    Stock model representing a tradeable stock.
    
    Attributes:
        id: Primary key
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL)
        name: Company name
        sector: Business sector
        industry: Specific industry
        exchange: Stock exchange (e.g., NYSE, NASDAQ)
        is_active: Whether the stock is actively tracked
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    exchange = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to stock prices
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"
