"""
Drawdown calculator - compute maximum drawdown and other risk metrics
"""

import pandas as pd
import numpy as np
from src.utils.logging import get_logger

logger = get_logger("qa_agent.drawdown_calculator")


class DrawdownCalculator:
    """Calculate drawdown metrics from price or equity data"""
    
    def __init__(self):
        self.logger = logger
    
    def calculate_cumulative_returns(self, prices):
        """
        Calculate cumulative returns from price series
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            pd.Series with cumulative returns
        """
        returns = prices.pct_change()
        cum_returns = (1 + returns).cumprod()
        
        return cum_returns
    
    def calculate_running_max(self, prices):
        """
        Calculate running maximum (peak) of prices
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            pd.Series with running max
        """
        return prices.expanding().max()
    
    def calculate_drawdown(self, prices):
        """
        Calculate drawdown from peak
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            pd.Series with drawdown as negative percentage
        """
        running_max = self.calculate_running_max(prices)
        drawdown = (prices - running_max) / running_max
        
        return drawdown
    
    def calculate_max_drawdown(self, prices):
        """
        Calculate maximum drawdown
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            float: maximum drawdown as negative decimal (e.g., -0.25 = 25%)
        """
        drawdown = self.calculate_drawdown(prices)
        max_dd = drawdown.min()
        
        self.logger.debug(f"Maximum Drawdown: {max_dd:.2%}")
        return max_dd
    
    def calculate_drawdown_duration(self, prices):
        """
        Calculate duration of maximum drawdown (days from peak to trough)
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            int: number of days
        """
        running_max = self.calculate_running_max(prices)
        is_drawdown = prices < running_max
        
        # Find consecutive True values
        groups = (is_drawdown != is_drawdown.shift()).cumsum()
        dd_duration = is_drawdown[is_drawdown].groupby(groups[is_drawdown]).size()
        
        if len(dd_duration) > 0:
            return dd_duration.max()
        return 0
    
    def calculate_recovery_time(self, prices):
        """
        Calculate time to recover from max drawdown
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            int: days to recover
        """
        running_max = self.calculate_running_max(prices)
        drawdown = (prices - running_max) / running_max
        max_dd_idx = drawdown.idxmin()
        
        # Find when price recovers above previous peak
        peak_before_dd = running_max.loc[:max_dd_idx].iloc[-1]
        recovery = prices[prices.index > max_dd_idx] >= peak_before_dd
        
        if recovery.any():
            recovery_idx = recovery[recovery].index[0]
            return (recovery_idx - max_dd_idx).days
        
        return None
    
    def calculate_volatility(self, prices, window=20):
        """
        Calculate annualized volatility
        
        Args:
            prices: pd.Series with price data
            window: rolling window for calculation
        
        Returns:
            float: annualized volatility
        """
        returns = prices.pct_change()
        volatility = returns.rolling(window=window).std() * np.sqrt(252)
        
        return volatility.iloc[-1]
    
    def analyze_drawdown_history(self, prices):
        """
        Comprehensive drawdown analysis
        
        Args:
            prices: pd.Series with price data
        
        Returns:
            dict with all drawdown metrics
        """
        max_dd = self.calculate_max_drawdown(prices)
        dd_duration = self.calculate_drawdown_duration(prices)
        recovery = self.calculate_recovery_time(prices)
        volatility = self.calculate_volatility(prices)
        
        return {
            "max_drawdown": max_dd,
            "max_drawdown_pct": max_dd * 100,
            "drawdown_duration_days": dd_duration,
            "recovery_days": recovery,
            "annualized_volatility": volatility,
        }


if __name__ == "__main__":
    calc = DrawdownCalculator()
    
    # Test with synthetic data
    dates = pd.date_range(end='2024-01-01', periods=500, freq='D')
    prices = 100 + np.cumsum(np.random.randn(500) * 1.5)
    prices_series = pd.Series(prices, index=dates)
    
    analysis = calc.analyze_drawdown_history(prices_series)
    
    print(f"✓ Max Drawdown: {analysis['max_drawdown_pct']:.2f}%")
    print(f"✓ Duration: {analysis['drawdown_duration_days']} days")
    print(f"✓ Recovery: {analysis['recovery_days']} days" if analysis['recovery_days'] else "Not recovered")
