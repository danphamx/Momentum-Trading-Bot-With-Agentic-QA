"""
Momentum scorer - calculates 12-1 month relative strength
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utils.constants import MOMENTUM_WINDOW_MONTHS, MOMENTUM_SKIP_MONTHS
from src.utils.logging import get_logger

logger = get_logger("alpha_agent.momentum_scorer")


class MomentumScorer:
    """Calculate 12-1 month momentum (skip most recent month for mean reversion)"""
    
    def __init__(self):
        self.logger = logger
        self.window_months = MOMENTUM_WINDOW_MONTHS
        self.skip_months = MOMENTUM_SKIP_MONTHS
    
    def calculate_monthly_returns(self, data):
        """
        Calculate monthly returns from daily OHLCV data
        
        Args:
            data: pd.DataFrame with 'Adj Close' column and datetime index
        
        Returns:
            pd.Series with monthly returns
        """
        if data.empty:
            return pd.Series()
        
        # Resample to monthly frequency, take last close of each month
        monthly_data = data['Adj Close'].resample('ME').last()
        
        # Calculate returns
        monthly_returns = monthly_data.pct_change()
        
        self.logger.debug(f"Calculated {len(monthly_returns)} monthly returns")
        return monthly_returns
    
    def calculate_12_1_momentum(self, data):
        """
        Calculate 12-1 month momentum (past 12 months, skip most recent month)
        
        Args:
            data: pd.DataFrame with 'Adj Close' column
        
        Returns:
            float: momentum score (cumulative return)
        """
        monthly_returns = self.calculate_monthly_returns(data)
        
        if len(monthly_returns) < self.window_months + 1:
            self.logger.warning(f"Insufficient data: {len(monthly_returns)} months")
            return 0.0
        
        # Get 12 months, skip the most recent month
        # [-13:-1] means: go back 13 months, stop before most recent
        returns_to_use = monthly_returns.iloc[-(self.window_months + 1):-self.skip_months]
        
        # Calculate cumulative return (compound)
        momentum = (1 + returns_to_use).prod() - 1
        
        self.logger.debug(f"12-1 momentum: {momentum:.2%}")
        return momentum
    
    def score_universe(self, tickers_data):
        """
        Score all tickers in the universe
        
        Args:
            tickers_data: dict with {ticker: DataFrame}
        
        Returns:
            pd.DataFrame with columns: ticker, momentum_score, rank
        """
        scores = []
        
        for ticker, data in tickers_data.items():
            if data.empty:
                self.logger.debug(f"Skipping {ticker}: no data")
                continue
            
            momentum = self.calculate_12_1_momentum(data)
            scores.append({
                "ticker": ticker,
                "momentum_score": momentum,
            })
        
        # Convert to DataFrame and rank
        df = pd.DataFrame(scores)
        
        if df.empty:
            self.logger.warning("No valid scores calculated")
            return df
        
        df["rank"] = df["momentum_score"].rank(ascending=False)
        df = df.sort_values("rank")
        
        self.logger.info(f"✓ Scored {len(df)} tickers")
        return df
    
    def get_top_performers(self, scores_df, percentile=10):
        """
        Get top X% of performers by momentum
        
        Args:
            scores_df: DataFrame with momentum scores
            percentile: Top X% (default 10%)
        
        Returns:
            pd.DataFrame with top performers
        """
        if scores_df.empty:
            return scores_df
        
        cutoff = len(scores_df) * percentile / 100
        top = scores_df.head(int(cutoff))
        
        self.logger.info(f"✓ Top {percentile}% = {len(top)} stocks")
        return top


if __name__ == "__main__":
    scorer = MomentumScorer()
    
    # Test with synthetic data
    dates = pd.date_range(end=datetime.now(), periods=36, freq='ME')
    prices = np.random.uniform(100, 150, len(dates))
    test_data = pd.DataFrame({
        'Adj Close': prices
    }, index=dates)
    
    momentum = scorer.calculate_12_1_momentum(test_data)
    print(f"✓ Test momentum: {momentum:.2%}")
