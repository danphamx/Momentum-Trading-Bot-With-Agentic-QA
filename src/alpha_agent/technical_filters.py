"""
Technical filters - SMA and RSI checks
"""

import pandas as pd
import numpy as np
from src.utils.constants import SMA_200_PERIOD, SMA_60_PERIOD, RSI_PERIOD, MAX_RSI
from src.utils.logging import get_logger

logger = get_logger("alpha_agent.technical_filters")


class TechnicalFilters:
    """Apply moving average and RSI filters"""
    
    def __init__(self):
        self.logger = logger
        self.sma_200 = SMA_200_PERIOD
        self.sma_60 = SMA_60_PERIOD
        self.rsi_period = RSI_PERIOD
        self.max_rsi = MAX_RSI
    
    def calculate_sma(self, data, period):
        """
        Calculate Simple Moving Average
        
        Args:
            data: pd.Series with price data
            period: int, window size
        
        Returns:
            pd.Series with SMA values
        """
        return data.rolling(window=period).mean()
    
    def calculate_rsi(self, data, period=14):
        """
        Calculate Relative Strength Index
        
        Args:
            data: pd.Series with price data (typically Close)
            period: int, RSI window
        
        Returns:
            pd.Series with RSI values
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_all_technicals(self, data):
        """
        Calculate all technical indicators for a given stock
        
        Args:
            data: pd.DataFrame with 'Adj Close' column
        
        Returns:
            pd.DataFrame with original data + SMA_200, SMA_60, RSI columns
        """
        if data.empty:
            return data
        
        result = data.copy()
        result['SMA_200'] = self.calculate_sma(result['Adj Close'], self.sma_200)
        result['SMA_60'] = self.calculate_sma(result['Adj Close'], self.sma_60)
        result['RSI'] = self.calculate_rsi(result['Adj Close'], self.rsi_period)
        
        return result
    
    def is_above_200d_sma(self, price, sma_200):
        """
        Check if price is above 200-day SMA (Bullish Floor)
        
        Args:
            price: float, current price
            sma_200: float, 200-day SMA value
        
        Returns:
            bool
        """
        if pd.isna(sma_200):
            return False
        return price > sma_200
    
    def is_above_60d_sma(self, price, sma_60):
        """
        Check if price is above 60-day SMA (Momentum Trigger)
        
        Args:
            price: float, current price
            sma_60: float, 60-day SMA value
        
        Returns:
            bool
        """
        if pd.isna(sma_60):
            return False
        return price > sma_60
    
    def is_rsi_not_overbought(self, rsi):
        """
        Check if RSI is not overbought (< 80)
        
        Args:
            rsi: float, RSI value
        
        Returns:
            bool
        """
        if pd.isna(rsi):
            return False
        return rsi < self.max_rsi
    
    def get_latest_technicals(self, data):
        """
        Get the most recent technical indicator values
        
        Args:
            data: pd.DataFrame with technical indicators
        
        Returns:
            dict with latest values
        """
        latest = data.iloc[-1]
        return {
            "price": latest.get('Adj Close', np.nan),
            "sma_200": latest.get('SMA_200', np.nan),
            "sma_60": latest.get('SMA_60', np.nan),
            "rsi": latest.get('RSI', np.nan),
        }


if __name__ == "__main__":
    filters = TechnicalFilters()
    
    # Test with synthetic data
    dates = pd.date_range(end='2024-01-01', periods=300, freq='D')
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    test_data = pd.DataFrame({
        'Adj Close': prices
    }, index=dates)
    
    test_data = filters.calculate_all_technicals(test_data)
    latest = filters.get_latest_technicals(test_data)
    
    print(f"✓ Latest price: ${latest['price']:.2f}")
    print(f"✓ SMA_200: ${latest['sma_200']:.2f}")
    print(f"✓ SMA_60: ${latest['sma_60']:.2f}")
    print(f"✓ RSI: {latest['rsi']:.2f}")
