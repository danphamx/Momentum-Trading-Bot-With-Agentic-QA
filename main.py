"""
Main entry point - orchestrate full Alpha + QA workflow
"""

from datetime import datetime
from src.alpha_agent import AlphaAgentRunner
from src.qa_agent import QAAgentRunner
from src.alerts import SlackNotifier, EmailNotifier
from src.utils.logging import get_logger
from src.utils.config import Config

logger = get_logger("main")


class MomentumSystem:
    """Main orchestrator for the Momentum Trading System"""
    
    def __init__(self):
        self.logger = logger
        self.alpha_runner = AlphaAgentRunner()
        self.qa_runner = QAAgentRunner()
        self.slack = SlackNotifier()
        self.email = EmailNotifier()
    
    def run_full_scan(self, tickers_list, generate_report=True):
        """
        Run complete Alpha + QA workflow
        
        Args:
            tickers_list: list of tickers to scan
            generate_report: bool, whether to generate summary report
        
        Returns:
            dict with results
        """
        self.logger.info("="*60)
        self.logger.info("🚀 MOMENTUM MASTERY SYSTEM STARTING")
        self.logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*60)
        
        # Step 1: Alpha Agent Scan
        self.logger.info("\n[PHASE 1] Alpha Agent Scan")
        self.logger.info("-" * 60)
        alpha_results = self.alpha_runner.run_scan(tickers_list)
        
        if alpha_results.empty:
            self.logger.warning("No Alpha recommendations found")
            return {
                "alpha_results": alpha_results,
                "qa_results": None,
                "status": "No trades found",
            }
        
        # Step 2: QA Agent Validation
        self.logger.info("\n[PHASE 2] QA Agent Validation")
        self.logger.info("-" * 60)
        qa_results = self.qa_runner.validate_multiple_trades(alpha_results)
        
        # Step 3: Generate Report
        if generate_report:
            self.logger.info("\n[PHASE 3] Report Generation")
            self.logger.info("-" * 60)
            report = self.qa_runner.generate_qa_report(qa_results)
            print(report)
        
        self.logger.info("\n" + "="*60)
        self.logger.info("✅ MOMENTUM MASTERY SYSTEM COMPLETE")
        self.logger.info("="*60)
        
        return {
            "alpha_results": alpha_results,
            "qa_results": qa_results,
            "status": "Complete",
        }
    
    def generate_full_report_html(self, qa_results):
        """
        Generate formatted HTML report for email/display
        
        Args:
            qa_results: pd.DataFrame from QA Agent
        
        Returns:
            str: HTML formatted report
        """
        total = len(qa_results)
        approved = len(qa_results[qa_results['confidence'] == 'HIGH'])
        conditional = len(qa_results[qa_results['confidence'] == 'MEDIUM'])
        rejected = len(qa_results[qa_results['confidence'] == 'REJECT'])
        
        pass_rate = (approved + conditional) / total * 100 if total > 0 else 0
        
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ color: #2c3e50; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .approved {{ color: green; font-weight: bold; }}
        .rejected {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>

<h1>📊 Momentum Mastery Weekly Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<h2>Summary</h2>
<table>
    <tr>
        <th>Metric</th>
        <th>Value</th>
    </tr>
    <tr>
        <td>Total Trades Evaluated</td>
        <td>{total}</td>
    </tr>
    <tr>
        <td class="approved">✅ Approved</td>
        <td>{approved}</td>
    </tr>
    <tr>
        <td>⚠️ Conditional</td>
        <td>{conditional}</td>
    </tr>
    <tr>
        <td class="rejected">❌ Rejected</td>
        <td>{rejected}</td>
    </tr>
    <tr>
        <td>Pass Rate</td>
        <td>{pass_rate:.1f}%</td>
    </tr>
</table>

<h2>Approved Trades</h2>
"""
        
        approved_trades = qa_results[qa_results['confidence'] == 'HIGH']
        if not approved_trades.empty:
            html += "<table><tr><th>Ticker</th><th>Play</th><th>Win Rate</th><th>Max DD</th></tr>"
            for _, trade in approved_trades.iterrows():
                wr = trade['trade_analysis']['win_rate']
                dd = trade['drawdown_analysis']['max_drawdown_pct']
                html += f"<tr><td>{trade['ticker']}</td><td>{trade['alpha_play']}</td><td>{wr:.1f}%</td><td>{dd:.1f}%</td></tr>"
            html += "</table>"
        else:
            html += "<p>No approved trades this week.</p>"
        
        html += """
</body>
</html>
"""
        return html


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Momentum Mastery Trading System")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN", "NFLX", "SPY", "QQQ"],
                        help="List of tickers to scan")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    
    args = parser.parse_args()
    
    system = MomentumSystem()
    results = system.run_full_scan(args.tickers, generate_report=args.report)


if __name__ == "__main__":
    main()
