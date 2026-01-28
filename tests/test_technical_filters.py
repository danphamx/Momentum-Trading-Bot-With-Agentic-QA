"""
Unit tests for Technical Filters
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.alpha_agent.technical_filters import TechnicalFilters


@pytest.fixture
def filters():
    """Initialize filters"""
    return TechnicalFilters()


@pytest.fixture
def sample_data():
    """Create sample price data"""
    dates = pd.date_range(end=datetime.now(), periods=300, freq='D')
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    return pd.DataFrame({'Adj Close': prices}, index=dates)


def test_calculate_sma(filters, sample_data):
    """Test SMA calculation"""
    sma = filters.calculate_sma(sample_data['Adj Close'], 20)
    
    assert len(sma) == len(sample_data)
    assert sma.isna().sum() == 19  # First 19 values are NaN


def test_calculate_rsi(filters, sample_data):
    """Test RSI calculation"""
    rsi = filters.calculate_rsi(sample_data['Adj Close'])
    
    assert len(rsi) == len(sample_data)
    assert rsi.dropna().min() >= 0
    assert rsi.dropna().max() <= 100


def test_is_above_200d_sma(filters):
    """Test 200d SMA check"""
    assert filters.is_above_200d_sma(105, 100) == True
    assert filters.is_above_200d_sma(95, 100) == False
    assert filters.is_above_200d_sma(105, np.nan) == False


def test_is_rsi_not_overbought(filters):
    """Test RSI overbought check"""
    assert filters.is_rsi_not_overbought(75) == True
    assert filters.is_rsi_not_overbought(85) == False
    assert filters.is_rsi_not_overbought(np.nan) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
