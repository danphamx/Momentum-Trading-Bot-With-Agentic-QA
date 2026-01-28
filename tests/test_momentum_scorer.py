"""
Unit tests for Momentum Scorer
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.alpha_agent.momentum_scorer import MomentumScorer


@pytest.fixture
def scorer():
    """Initialize scorer"""
    return MomentumScorer()


@pytest.fixture
def sample_data():
    """Create sample price data"""
    dates = pd.date_range(end=datetime.now(), periods=36, freq='ME')
    prices = 100 + np.cumsum(np.random.randn(36) * 0.5)
    return pd.DataFrame({'Adj Close': prices}, index=dates)


def test_calculate_monthly_returns(scorer, sample_data):
    """Test monthly return calculation"""
    returns = scorer.calculate_monthly_returns(sample_data)
    
    assert len(returns) == len(sample_data)
    assert returns.isna().sum() == 1  # First month is NaN


def test_calculate_12_1_momentum(scorer, sample_data):
    """Test 12-1 momentum calculation"""
    momentum = scorer.calculate_12_1_momentum(sample_data)
    
    assert isinstance(momentum, float)
    assert -1 < momentum < 2  # Reasonable bounds


def test_empty_data(scorer):
    """Test handling of empty data"""
    empty_df = pd.DataFrame()
    momentum = scorer.calculate_12_1_momentum(empty_df)
    
    assert momentum == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
