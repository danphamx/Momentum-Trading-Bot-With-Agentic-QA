"""
Data fetcher for market data from yfinance
"""

import pandas as pd
import yfinance as yf
from src.utils.logging import get_logger

logger = get_logger("data.fetcher")


class DataFetcher:
    """Wrapper around yfinance for consistent data retrieval"""
    
    def __init__(self):
        self.logger = logger
    
    def fetch_historical_data(self, ticker, period="5y", interval="1d"):
        """
        Fetch historical OHLCV data for a ticker
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            period: Data period ('1y', '5y', etc.)
            interval: Candle interval ('1d', '1h', etc.)
        
        Returns:
            pd.DataFrame with columns: Open, High, Low, Close, Volume, Adj Close
        """
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if data.empty:
                self.logger.warning(f"No data returned for {ticker}")
                return pd.DataFrame()
            
            self.logger.debug(f"Fetched {len(data)} candles for {ticker}")
            return data
        
        except Exception as e:
            self.logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_ticker_info(self, ticker):
        """
        Fetch ticker metadata (market cap, volume, etc.)
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            dict with metadata
        """
        try:
            tick = yf.Ticker(ticker)
            info = tick.info
            
            return {
                "ticker": ticker,
                "market_cap": info.get("marketCap", 0),
                "avg_volume": info.get("averageVolume", 0),
                "avg_volume_10d": info.get("averageVolume10days", 0),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            }
        
        except Exception as e:
            self.logger.error(f"Failed to fetch info for {ticker}: {str(e)}")
            return {}
    
    def fetch_multiple_tickers(self, tickers, period="5y"):
        """
        Fetch data for multiple tickers efficiently
        
        Args:
            tickers: List of ticker symbols
            period: Data period
        
        Returns:
            dict with {ticker: DataFrame}
        """
        data_dict = {}
        for ticker in tickers:
            data_dict[ticker] = self.fetch_historical_data(ticker, period=period)
        
        self.logger.info(f"Fetched data for {len(data_dict)} tickers")
        return data_dict


if __name__ == "__main__":
    fetcher = DataFetcher()
    data = fetcher.fetch_historical_data("AAPL", period="1y")
    print(f"✓ Fetched {len(data)} rows for AAPL")
