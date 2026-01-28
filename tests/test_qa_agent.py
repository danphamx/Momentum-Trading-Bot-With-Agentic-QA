"""
Unit tests for QA Agent
"""

import pytest
from src.qa_agent.quality_checker import QualityChecker


@pytest.fixture
def checker():
    """Initialize quality checker"""
    return QualityChecker()


def test_check_drawdown_passes(checker):
    """Test drawdown check passes"""
    passes, detail = checker.check_drawdown(12.5)
    
    assert passes == True
    assert detail['passes'] == True


def test_check_drawdown_fails(checker):
    """Test drawdown check fails"""
    passes, detail = checker.check_drawdown(18.0)
    
    assert passes == False
    assert detail['passes'] == False


def test_check_win_rate_passes(checker):
    """Test win rate check passes"""
    passes, detail = checker.check_win_rate(65.0)
    
    assert passes == True


def test_check_win_rate_fails(checker):
    """Test win rate check fails"""
    passes, detail = checker.check_win_rate(45.0)
    
    assert passes == False


def test_evaluate_backtest(checker):
    """Test full backtest evaluation"""
    backtest_results = {
        "total_trades": 25,
        "win_rate": 62.5,
        "profit_factor": 1.8,
    }
    
    eval_result = checker.evaluate_backtest(backtest_results)
    
    assert 'vibe' in eval_result
    assert eval_result['all_pass'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
