"""
Universe filtering - identify eligible stocks based on circuit breakers
"""

import pandas as pd
from src.utils.constants import MIN_MARKET_CAP_USD, MIN_DAILY_VOLUME_USD
from src.utils.logging import get_logger

logger = get_logger("data.universe_filter")


class UniverseFilter:
    """Filter stocks for trading based on market cap and volume thresholds"""
    
    def __init__(self):
        self.logger = logger
        self.min_market_cap = MIN_MARKET_CAP_USD
        self.min_daily_volume = MIN_DAILY_VOLUME_USD
    
    def filter_by_market_cap(self, stocks_info):
        """
        Filter stocks with market cap above minimum threshold
        
        Args:
            stocks_info: dict with {ticker: {market_cap, ...}}
        
        Returns:
            dict with filtered stocks
        """
        filtered = {}
        for ticker, info in stocks_info.items():
            market_cap = info.get("market_cap", 0)
            
            if market_cap >= self.min_market_cap:
                filtered[ticker] = info
                self.logger.debug(f"{ticker}: Market cap ${market_cap:,.0f} ✓")
            else:
                self.logger.debug(f"{ticker}: Market cap ${market_cap:,.0f} ✗ (below $2B)")
        
        self.logger.info(f"Market cap filter: {len(filtered)}/{len(stocks_info)} passed")
        return filtered
    
    def filter_by_volume(self, stocks_info):
        """
        Filter stocks with average daily volume above minimum threshold
        
        Args:
            stocks_info: dict with {ticker: {avg_volume, ...}}
        
        Returns:
            dict with filtered stocks
        """
        filtered = {}
        for ticker, info in stocks_info.items():
            avg_volume = info.get("avg_volume", 0)
            avg_volume_10d = info.get("avg_volume_10d", 0)
            
            # Use 10-day average if available, otherwise use regular average
            volume_to_check = avg_volume_10d if avg_volume_10d > 0 else avg_volume
            daily_volume_usd = volume_to_check * 100  # Rough estimate (100 = avg price)
            
            if daily_volume_usd >= self.min_daily_volume:
                filtered[ticker] = info
                self.logger.debug(f"{ticker}: Est. daily vol ${daily_volume_usd:,.0f} ✓")
            else:
                self.logger.debug(f"{ticker}: Est. daily vol ${daily_volume_usd:,.0f} ✗ (below $10M)")
        
        self.logger.info(f"Volume filter: {len(filtered)}/{len(stocks_info)} passed")
        return filtered
    
    def apply_circuit_breakers(self, stocks_info):
        """
        Apply all circuit breaker filters
        
        Args:
            stocks_info: dict with stock information
        
        Returns:
            dict with stocks passing all filters
        """
        self.logger.info("Applying circuit breaker filters...")
        
        # Apply market cap filter
        filtered = self.filter_by_market_cap(stocks_info)
        
        # Apply volume filter
        filtered = self.filter_by_volume(filtered)
        
        self.logger.info(f"✓ Circuit breakers passed: {len(filtered)} stocks eligible")
        return filtered


if __name__ == "__main__":
    filter_obj = UniverseFilter()
    
    test_stocks = {
        "AAPL": {"market_cap": 3_000_000_000, "avg_volume": 50_000_000, "avg_volume_10d": 48_000_000},
        "PENNY": {"market_cap": 500_000_000, "avg_volume": 100_000, "avg_volume_10d": 0},
        "LOW_VOL": {"market_cap": 3_000_000_000, "avg_volume": 100_000, "avg_volume_10d": 0},
    }
    
    result = filter_obj.apply_circuit_breakers(test_stocks)
    print(f"✓ Filtered: {len(result)} stocks passed filters")
