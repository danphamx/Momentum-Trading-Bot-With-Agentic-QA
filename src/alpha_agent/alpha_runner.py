"""
Alpha Agent runner - main execution orchestrator
"""

import pandas as pd
from datetime import datetime
from src.data import DataFetcher, UniverseFilter
from src.alpha_agent.momentum_scorer import MomentumScorer
from src.alpha_agent.technical_filters import TechnicalFilters
from src.alpha_agent.play_detector import PlayDetector
from src.utils.logging import get_logger

logger = get_logger("alpha_agent.runner")


class AlphaAgentRunner:
    """Orchestrate the Alpha Agent workflow"""
    
    def __init__(self):
        self.logger = logger
        self.fetcher = DataFetcher()
        self.universe_filter = UniverseFilter()
        self.scorer = MomentumScorer()
        self.tech_filters = TechnicalFilters()
        self.detector = PlayDetector()
    
    def run_scan(self, tickers_list):
        """
        Run a complete Alpha Agent scan
        
        Args:
            tickers_list: list of ticker symbols to scan
        
        Returns:
            pd.DataFrame with recommended trades
        """
        self.logger.info(f"🚀 Starting Alpha Agent scan for {len(tickers_list)} tickers...")
        
        # Step 1: Fetch data for all tickers
        self.logger.info("Step 1/5: Fetching price data...")
        tickers_data = self.fetcher.fetch_multiple_tickers(tickers_list, period="5y")
        
        # Step 2: Fetch ticker info for circuit breaker filtering
        self.logger.info("Step 2/5: Fetching ticker info...")
        stocks_info = {}
        for ticker in tickers_list:
            info = self.fetcher.fetch_ticker_info(ticker)
            if info:
                stocks_info[ticker] = info
        
        # Step 3: Apply circuit breakers
        self.logger.info("Step 3/5: Applying circuit breakers...")
        eligible_stocks = self.universe_filter.apply_circuit_breakers(stocks_info)
        
        # Step 4: Score by momentum
        self.logger.info("Step 4/5: Calculating 12-1 momentum...")
        momentum_scores = self.scorer.score_universe(tickers_data)
        
        # Keep only eligible stocks
        momentum_scores = momentum_scores[momentum_scores['ticker'].isin(eligible_stocks.keys())]
        
        # Get top 10%
        top_performers = self.scorer.get_top_performers(momentum_scores, percentile=10)
        
        # Step 5: Detect plays
        self.logger.info("Step 5/5: Detecting technical plays...")
        recommendations = []
        
        for _, row in top_performers.iterrows():
            ticker = row['ticker']
            momentum_score = row['momentum_score']
            
            # Get price data
            data = tickers_data.get(ticker, pd.DataFrame())
            if data.empty:
                continue
            
            # Calculate technicals
            data_with_tech = self.tech_filters.calculate_all_technicals(data)
            technicals = self.tech_filters.get_latest_technicals(data_with_tech)
            
            # Check filters
            passes_200d = self.tech_filters.is_above_200d_sma(
                technicals['price'], technicals['sma_200']
            )
            passes_rsi = self.tech_filters.is_rsi_not_overbought(technicals['rsi'])
            
            if not (passes_200d and passes_rsi):
                self.logger.debug(f"{ticker}: Failed technical filters")
                continue
            
            # Detect play
            play = self.detector.classify_play(ticker, data_with_tech, technicals)
            
            if play['play'] is not None:
                recommendations.append({
                    "ticker": ticker,
                    "momentum_score": momentum_score,
                    "play": play['play'],
                    "confidence": play['confidence'],
                    "price": technicals['price'],
                    "sma_200": technicals['sma_200'],
                    "sma_60": technicals['sma_60'],
                    "rsi": technicals['rsi'],
                    "timestamp": datetime.now(),
                })
        
        result_df = pd.DataFrame(recommendations)
        
        if not result_df.empty:
            result_df = result_df.sort_values("confidence", ascending=False)
        
        self.logger.info(f"✅ Alpha Agent found {len(result_df)} trade recommendations")
        return result_df


if __name__ == "__main__":
    runner = AlphaAgentRunner()
    
    # Test with a small list
    test_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN", "NFLX"]
    
    results = runner.run_scan(test_tickers)
    
    if not results.empty:
        print("\n" + "="*60)
        print("ALPHA AGENT RECOMMENDATIONS")
        print("="*60)
        print(results[['ticker', 'momentum_score', 'play', 'confidence', 'price']].to_string())
    else:
        print("No recommendations found.")
