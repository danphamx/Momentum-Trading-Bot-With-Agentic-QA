"""
Unit tests for Backtest Engine
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.qa_agent.backtest_engine import BacktestEngine


@pytest.fixture
def engine():
    """Initialize backtest engine"""
    return BacktestEngine()


@pytest.fixture
def sample_data():
    """Create sample price data with technicals"""
    dates = pd.date_range(end=datetime.now(), periods=300, freq='D')
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    
    data = pd.DataFrame({'Adj Close': prices}, index=dates)
    data['SMA_200'] = data['Adj Close'].rolling(200).mean()
    data['SMA_60'] = data['Adj Close'].rolling(60).mean()
    
    return data


def test_analyze_trades(engine):
    """Test trade analysis"""
    trades = [
        {"entry_price": 100, "exit_price": 110, "return": 0.10},
        {"entry_price": 100, "exit_price": 95, "return": -0.05},
        {"entry_price": 100, "exit_price": 105, "return": 0.05},
    ]
    
    analysis = engine.analyze_trades(trades)
    
    assert analysis['total_trades'] == 3
    assert analysis['winning_trades'] == 2
    assert analysis['losing_trades'] == 1


def test_empty_trades(engine):
    """Test with no trades"""
    analysis = engine.analyze_trades([])
    
    assert analysis['total_trades'] == 0
    assert analysis['win_rate'] == 0.0


def test_backtest_sma_crossover(engine, sample_data):
    """Test SMA crossover backtest"""
    trades = engine.backtest_sma_crossover(sample_data)
    
    # Should have some trades
    assert isinstance(trades, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
