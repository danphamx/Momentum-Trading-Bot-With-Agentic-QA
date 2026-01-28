"""
Quality checker - validate trades against risk criteria
"""

import pandas as pd
from src.utils.constants import MAX_DRAWDOWN_PCT, MIN_WIN_RATE_PCT
from src.utils.logging import get_logger

logger = get_logger("qa_agent.quality_checker")


class QualityChecker:
    """Validate trades based on historical performance criteria"""
    
    def __init__(self, max_drawdown_tol=MAX_DRAWDOWN_PCT, min_win_rate=MIN_WIN_RATE_PCT):
        self.logger = logger
        self.max_drawdown_tol = max_drawdown_tol
        self.min_win_rate = min_win_rate
    
    def check_drawdown(self, max_drawdown_pct):
        """
        Check if maximum drawdown is within tolerance
        
        Args:
            max_drawdown_pct: float, max drawdown as percentage (e.g., 25.5)
        
        Returns:
            bool, dict with details
        """
        passes = abs(max_drawdown_pct) <= self.max_drawdown_tol
        
        return passes, {
            "max_drawdown_pct": max_drawdown_pct,
            "max_allowed_pct": self.max_drawdown_tol,
            "passes": passes,
        }
    
    def check_win_rate(self, win_rate_pct):
        """
        Check if win rate meets minimum threshold
        
        Args:
            win_rate_pct: float, win rate as percentage (e.g., 55.5)
        
        Returns:
            bool, dict with details
        """
        passes = win_rate_pct >= self.min_win_rate
        
        return passes, {
            "win_rate_pct": win_rate_pct,
            "min_required_pct": self.min_win_rate,
            "passes": passes,
        }
    
    def check_sample_size(self, num_trades, min_trades=5):
        """
        Check if sample size is sufficient for statistical validity
        
        Args:
            num_trades: int, number of trades
            min_trades: int, minimum required
        
        Returns:
            bool, dict with details
        """
        passes = num_trades >= min_trades
        
        return passes, {
            "num_trades": num_trades,
            "min_required": min_trades,
            "passes": passes,
        }
    
    def check_profit_factor(self, profit_factor, min_pf=1.5):
        """
        Check profit factor (gross profit / gross loss)
        
        Args:
            profit_factor: float
            min_pf: float, minimum acceptable profit factor
        
        Returns:
            bool, dict with details
        """
        passes = profit_factor >= min_pf
        
        return passes, {
            "profit_factor": profit_factor,
            "min_required": min_pf,
            "passes": passes,
        }
    
    def evaluate_backtest(self, backtest_results):
        """
        Comprehensive trade validation
        
        Args:
            backtest_results: dict from backtest_engine.analyze_trades()
        
        Returns:
            dict with validation results and vibe assessment
        """
        checks = {}
        
        # Check win rate
        wr_passes, wr_detail = self.check_win_rate(backtest_results.get('win_rate', 0))
        checks['win_rate'] = wr_detail
        
        # Check sample size
        ss_passes, ss_detail = self.check_sample_size(backtest_results.get('total_trades', 0))
        checks['sample_size'] = ss_detail
        
        # Check profit factor (if we have the data)
        pf = backtest_results.get('profit_factor', 0)
        pf_passes, pf_detail = self.check_profit_factor(pf, min_pf=1.0)
        checks['profit_factor'] = pf_detail
        
        # Determine overall vibe
        all_pass = wr_passes and ss_passes and pf_passes
        
        if all_pass:
            vibe = "✅ VIBE APPROVED"
            confidence = "HIGH"
        elif ss_passes and (wr_passes or pf_passes):
            vibe = "⚠️  VIBE CONDITIONAL"
            confidence = "MEDIUM"
        else:
            vibe = "❌ VIBE REJECTED"
            confidence = "REJECT"
        
        return {
            "vibe": vibe,
            "confidence": confidence,
            "all_pass": all_pass,
            "checks": checks,
            "backtest_summary": backtest_results,
        }
    
    def suggest_improvements(self, evaluation):
        """
        Suggest parameter changes if trade fails QA
        
        Args:
            evaluation: dict from evaluate_backtest()
        
        Returns:
            list of suggested improvements
        """
        suggestions = []
        
        if not evaluation['all_pass']:
            wr = evaluation['checks']['win_rate']
            
            if wr['win_rate_pct'] < self.min_win_rate:
                gap = self.min_win_rate - wr['win_rate_pct']
                suggestions.append(f"Win rate too low by {gap:.1f}%. Try tightening stop loss (e.g., 10% → 7%)")
            
            if evaluation['checks']['sample_size']['num_trades'] < 5:
                suggestions.append("Only a few trades in backtest. Extend backtest period to 5+ years.")
            
            pf = evaluation['checks']['profit_factor']
            if pf['profit_factor'] < 1.0:
                suggestions.append("Losing money overall. Consider raising profit target (e.g., 20% → 25%)")
        
        return suggestions


if __name__ == "__main__":
    checker = QualityChecker()
    
    test_backtest = {
        "total_trades": 25,
        "win_rate": 62.5,
        "profit_factor": 1.8,
        "avg_win": 0.12,
        "avg_loss": -0.08,
    }
    
    eval_result = checker.evaluate_backtest(test_backtest)
    print(f"✓ Vibe: {eval_result['vibe']}")
    
    if not eval_result['all_pass']:
        suggestions = checker.suggest_improvements(eval_result)
        for sug in suggestions:
            print(f"  → {sug}")
