"""
StockPrice SQLAlchemy model - represents historical stock price data.
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class StockPrice(Base):
    """
    StockPrice model representing daily stock price data.
    
    Attributes:
        id: Primary key
        stock_id: Foreign key to Stock
        date: Trading date
        open_price: Opening price
        high_price: Day's high price
        low_price: Day's low price
        close_price: Closing price
        adj_close: Adjusted closing price
        volume: Trading volume
        created_at: Record creation timestamp
    """
    
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=False)
    adj_close = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to stock
    stock = relationship("Stock", back_populates="prices")
    
    # Unique constraint: one price record per stock per date
    __table_args__ = (
        UniqueConstraint("stock_id", "date", name="uix_stock_date"),
    )
    
    def __repr__(self):
        return f"<StockPrice(stock_id={self.stock_id}, date='{self.date}', close={self.close_price})>"
