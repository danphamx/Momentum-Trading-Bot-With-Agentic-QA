"""
Shared constants for the Momentum Trading System
"""

# Circuit Breaker Thresholds
MIN_MARKET_CAP_USD = 2_000_000_000  # $2B
MIN_DAILY_VOLUME_USD = 10_000_000   # $10M
MAX_RSI = 80  # Overbought threshold
MAX_DRAWDOWN_PCT = 15  # 15% maximum acceptable drawdown
MIN_WIN_RATE_PCT = 60  # Minimum acceptable win rate

# Technical Indicators
SMA_200_PERIOD = 200  # Long-term trend (Bullish Floor)
SMA_60_PERIOD = 60   # Momentum line
RSI_PERIOD = 14      # RSI calculation window

# Momentum Calculation
MOMENTUM_WINDOW_MONTHS = 12
MOMENTUM_SKIP_MONTHS = 1  # Skip most recent month

# Backtesting
BACKTEST_YEARS = 3  # Historical backtest period

# Reporting
REPORT_DAY = "Friday"
WEEKLY_REPORT_HOUR = 8  # 8 AM

# Limits
MAX_POSITIONS = 5
POSITION_SIZE_PCT = 20  # Percent of portfolio per trade

print("✓ Constants loaded")
