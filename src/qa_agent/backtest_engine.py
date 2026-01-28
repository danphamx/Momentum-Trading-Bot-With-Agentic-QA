"""
Backtest engine - historical performance evaluation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.utils.logging import get_logger

logger = get_logger("qa_agent.backtest_engine")


class BacktestEngine:
    """Run historical backtests on trades"""
    
    def __init__(self, initial_capital=10000):
        self.logger = logger
        self.initial_capital = initial_capital
    
    def backtest_entry_on_signal(self, data, entry_signal_col, stop_loss_pct=0.10, take_profit_pct=0.20):
        """
        Backtest a strategy with a given signal
        
        Args:
            data: pd.DataFrame with price data and signal column
            entry_signal_col: str, column name indicating entry signal (True/False)
            stop_loss_pct: float, stop loss as percent (e.g., 0.10 = 10%)
            take_profit_pct: float, take profit as percent
        
        Returns:
            dict with backtest results
        """
        if data.empty:
            return {"error": "No data"}
        
        trades = []
        entry_price = None
        entry_date = None
        position_open = False
        
        for idx, row in data.iterrows():
            price = row['Adj Close']
            
            # Entry signal
            if not position_open and row.get(entry_signal_col, False):
                entry_price = price
                entry_date = idx
                position_open = True
                trades.append({
                    "entry_date": entry_date,
                    "entry_price": entry_price,
                })
            
            # Exit conditions
            if position_open:
                pnl_pct = (price - entry_price) / entry_price
                
                # Hit stop loss
                if pnl_pct < -stop_loss_pct:
                    trades[-1].update({
                        "exit_date": idx,
                        "exit_price": price,
                        "return": pnl_pct,
                        "exit_reason": "stop_loss",
                    })
                    position_open = False
                
                # Hit take profit
                elif pnl_pct >= take_profit_pct:
                    trades[-1].update({
                        "exit_date": idx,
                        "exit_price": price,
                        "return": pnl_pct,
                        "exit_reason": "take_profit",
                    })
                    position_open = False
        
        # Close any open position at end of data
        if position_open:
            trades[-1].update({
                "exit_date": data.index[-1],
                "exit_price": data.iloc[-1]['Adj Close'],
                "return": (data.iloc[-1]['Adj Close'] - entry_price) / entry_price,
                "exit_reason": "end_of_data",
            })
        
        return trades
    
    def backtest_sma_crossover(self, data, sma_short=60, sma_long=200, stop_loss_pct=0.10):
        """
        Backtest: Buy when price > SMA_60 and > SMA_200
        
        Args:
            data: pd.DataFrame with price and SMA columns
            sma_short: short-term SMA column name
            sma_long: long-term SMA column name
            stop_loss_pct: stop loss percent
        
        Returns:
            list of trades
        """
        # Generate signals
        data['signal'] = (data['Adj Close'] > data[f'SMA_{sma_short}']) & \
                         (data['Adj Close'] > data[f'SMA_{sma_long}'])
        
        # Identify entry points (transition from False to True)
        data['entry'] = data['signal'] & ~data['signal'].shift(1).fillna(False)
        
        # Backtest
        trades = self.backtest_entry_on_signal(data, 'entry', stop_loss_pct=stop_loss_pct)
        
        return trades
    
    def analyze_trades(self, trades):
        """
        Analyze trade results
        
        Args:
            trades: list of trade dicts
        
        Returns:
            dict with statistics
        """
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
            }
        
        # Remove incomplete trades
        completed_trades = [t for t in trades if 'return' in t]
        
        if not completed_trades:
            return {
                "total_trades": len(trades),
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
            }
        
        returns = [t['return'] for t in completed_trades]
        
        winning_trades = [r for r in returns if r > 0]
        losing_trades = [r for r in returns if r < 0]
        
        win_rate = len(winning_trades) / len(completed_trades) * 100 if completed_trades else 0
        avg_win = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        gross_profit = sum([r for r in returns if r > 0])
        gross_loss = abs(sum([r for r in returns if r < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            "total_trades": len(completed_trades),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "net_return": sum(returns),
        }


if __name__ == "__main__":
    engine = BacktestEngine()
    
    # Test with synthetic data
    dates = pd.date_range(end='2024-01-01', periods=500, freq='D')
    prices = 100 + np.cumsum(np.random.randn(500) * 0.5)
    test_data = pd.DataFrame({
        'Adj Close': prices
    }, index=dates)
    
    test_data['SMA_200'] = test_data['Adj Close'].rolling(200).mean()
    test_data['SMA_60'] = test_data['Adj Close'].rolling(60).mean()
    
    trades = engine.backtest_sma_crossover(test_data)
    analysis = engine.analyze_trades(trades)
    
    print(f"✓ Backtest completed: {analysis['total_trades']} trades")
    print(f"✓ Win rate: {analysis['win_rate']:.1f}%")
    print(f"✓ Net return: {analysis['net_return']:.2%}")
