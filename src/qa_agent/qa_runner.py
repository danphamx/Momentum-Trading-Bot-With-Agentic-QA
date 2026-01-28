"""
QA Agent runner - backtest and validate trades
"""

import pandas as pd
from src.data import DataFetcher
from src.alpha_agent.technical_filters import TechnicalFilters
from src.qa_agent.backtest_engine import BacktestEngine
from src.qa_agent.drawdown_calculator import DrawdownCalculator
from src.qa_agent.quality_checker import QualityChecker
from src.utils.logging import get_logger

logger = get_logger("qa_agent.runner")


class QAAgentRunner:
    """Orchestrate the QA Agent workflow (backtesting & validation)"""
    
    def __init__(self):
        self.logger = logger
        self.fetcher = DataFetcher()
        self.tech_filters = TechnicalFilters()
        self.backtest_engine = BacktestEngine()
        self.dd_calculator = DrawdownCalculator()
        self.quality_checker = QualityChecker()
    
    def validate_single_trade(self, ticker, backtest_period_years=3, stop_loss_pct=0.10):
        """
        Run full QA validation on a single trade recommendation
        
        Args:
            ticker: str, stock ticker
            backtest_period_years: int, years of historical data
            stop_loss_pct: float, stop loss percentage
        
        Returns:
            dict with full validation results
        """
        self.logger.info(f"🔍 QA validation for {ticker}...")
        
        # Step 1: Fetch historical data
        self.logger.debug(f"  Fetching {backtest_period_years}y data...")
        data = self.fetcher.fetch_historical_data(ticker, period=f"{backtest_period_years}y")
        
        if data.empty:
            self.logger.error(f"  No data available for {ticker}")
            return {
                "ticker": ticker,
                "vibe": "❌ VIBE REJECTED",
                "reason": "No historical data",
            }
        
        # Step 2: Calculate technicals
        self.logger.debug(f"  Calculating technicals...")
        data = self.tech_filters.calculate_all_technicals(data)
        
        # Step 3: Run backtest
        self.logger.debug(f"  Running backtest...")
        trades = self.backtest_engine.backtest_sma_crossover(
            data, 
            sma_short=60, 
            sma_long=200,
            stop_loss_pct=stop_loss_pct
        )
        
        # Step 4: Analyze trades
        trade_analysis = self.backtest_engine.analyze_trades(trades)
        self.logger.debug(f"    {trade_analysis['total_trades']} trades | {trade_analysis['win_rate']:.1f}% win rate")
        
        # Step 5: Calculate drawdown
        self.logger.debug(f"  Calculating drawdown...")
        dd_analysis = self.dd_calculator.analyze_drawdown_history(data['Adj Close'])
        self.logger.debug(f"    Max DD: {dd_analysis['max_drawdown_pct']:.1f}%")
        
        # Step 6: Quality check
        self.logger.debug(f"  Running quality checks...")
        quality_eval = self.quality_checker.evaluate_backtest(trade_analysis)
        
        # Step 7: Get suggestions if failed
        suggestions = []
        if not quality_eval['all_pass']:
            suggestions = self.quality_checker.suggest_improvements(quality_eval)
        
        result = {
            "ticker": ticker,
            "vibe": quality_eval['vibe'],
            "confidence": quality_eval['confidence'],
            "trade_analysis": trade_analysis,
            "drawdown_analysis": dd_analysis,
            "quality_checks": quality_eval['checks'],
            "suggestions": suggestions,
        }
        
        return result
    
    def validate_multiple_trades(self, alpha_recommendations, backtest_period_years=3):
        """
        Run QA validation on multiple Alpha Agent recommendations
        
        Args:
            alpha_recommendations: pd.DataFrame from Alpha Agent
            backtest_period_years: int, years for backtest
        
        Returns:
            pd.DataFrame with validation results for all trades
        """
        self.logger.info(f"🔍 QA validation for {len(alpha_recommendations)} trades...")
        
        qa_results = []
        
        for _, rec in alpha_recommendations.iterrows():
            ticker = rec['ticker']
            
            validation = self.validate_single_trade(
                ticker, 
                backtest_period_years=backtest_period_years
            )
            
            # Merge with original recommendation
            validation['momentum_score'] = rec['momentum_score']
            validation['alpha_play'] = rec['play']
            validation['alpha_confidence'] = rec['confidence']
            
            qa_results.append(validation)
        
        result_df = pd.DataFrame(qa_results)
        
        # Count vibes
        approved = len(result_df[result_df['confidence'] == 'HIGH'])
        conditional = len(result_df[result_df['confidence'] == 'MEDIUM'])
        rejected = len(result_df[result_df['confidence'] == 'REJECT'])
        
        self.logger.info(f"✅ QA complete: {approved} approved, {conditional} conditional, {rejected} rejected")
        
        return result_df
    
    def generate_qa_report(self, qa_results):
        """
        Generate summary report from QA results
        
        Args:
            qa_results: pd.DataFrame from validate_multiple_trades()
        
        Returns:
            str: formatted report
        """
        total = len(qa_results)
        approved = len(qa_results[qa_results['confidence'] == 'HIGH'])
        conditional = len(qa_results[qa_results['confidence'] == 'MEDIUM'])
        rejected = len(qa_results[qa_results['confidence'] == 'REJECT'])
        
        pass_rate = (approved + conditional) / total * 100 if total > 0 else 0
        
        report = f"""
╔═══════════════════════════════════════════════════════════╗
║              QA AGENT VALIDATION REPORT                  ║
╚═══════════════════════════════════════════════════════════╝

Summary:
  Total Trades Evaluated: {total}
  ✅ Approved: {approved}
  ⚠️  Conditional: {conditional}
  ❌ Rejected: {rejected}
  Pass Rate: {pass_rate:.1f}%

Approved Trades:
"""
        approved_trades = qa_results[qa_results['confidence'] == 'HIGH']
        if not approved_trades.empty:
            for _, trade in approved_trades.iterrows():
                report += f"\n  • {trade['ticker']}: {trade['alpha_play']} (WR: {trade['trade_analysis']['win_rate']:.1f}%)"
        else:
            report += "\n  (None)"
        
        report += "\n\nRejected Trades:"
        rejected_trades = qa_results[qa_results['confidence'] == 'REJECT']
        if not rejected_trades.empty:
            for _, trade in rejected_trades.iterrows():
                report += f"\n  • {trade['ticker']}: {trade['suggestions'][0] if trade['suggestions'] else 'High drawdown'}"
        else:
            report += "\n  (None)"
        
        report += "\n"
        return report


if __name__ == "__main__":
    runner = QAAgentRunner()
    
    # Test validation on a single ticker
    result = runner.validate_single_trade("AAPL", backtest_period_years=2)
    
    print(f"✓ {result['ticker']}: {result['vibe']}")
    if result.get('suggestions'):
        for sug in result['suggestions']:
            print(f"  → {sug}")
