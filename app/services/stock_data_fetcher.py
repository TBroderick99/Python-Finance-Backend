"""
Stock data fetcher service - Fetches stock data from external sources.
"""
import yfinance as yf
from datetime import date, datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Service for fetching stock data from external APIs."""
    
    def __init__(self):
        """Initialize the stock data fetcher."""
        pass
    
    def get_stock_info(self, symbol: str) -> Optional[dict]:
        """
        Get stock information (name, sector, industry, etc.).
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with stock info or None if not found
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or info.get("regularMarketPrice") is None:
                return None
            
            return {
                "symbol": symbol.upper(),
                "name": info.get("longName") or info.get("shortName") or symbol,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "exchange": info.get("exchange"),
            }
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def get_historical_prices(
        self,
        symbol: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "1mo"
    ) -> list[dict]:
        """
        Get historical stock prices.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            List of price dictionaries
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # If dates provided, use them; otherwise use period
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date)
            else:
                df = ticker.history(period=period)
            
            if df.empty:
                return []
            
            prices = []
            for idx, row in df.iterrows():
                prices.append({
                    "date": idx.date(),
                    "open_price": float(row["Open"]) if row["Open"] else None,
                    "high_price": float(row["High"]) if row["High"] else None,
                    "low_price": float(row["Low"]) if row["Low"] else None,
                    "close_price": float(row["Close"]),
                    "volume": int(row["Volume"]) if row["Volume"] else None,
                })
            
            return prices
        except Exception as e:
            logger.error(f"Error fetching historical prices for {symbol}: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> Optional[dict]:
        """
        Get current stock price.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with current price info or None
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            return {
                "symbol": symbol.upper(),
                "price": info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("regularMarketOpen"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
            }
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def search_symbols(self, query: str) -> list[dict]:
        """
        Search for stock symbols matching a query.
        
        Args:
            query: Search query (company name or symbol)
            
        Returns:
            List of matching stocks
        """
        try:
            # Use yfinance's search capability
            tickers = yf.Tickers(query)
            results = []
            
            for symbol in query.upper().split():
                info = self.get_stock_info(symbol)
                if info:
                    results.append(info)
            
            return results
        except Exception as e:
            logger.error(f"Error searching for symbols: {e}")
            return []
