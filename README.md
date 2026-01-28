# Momentum Mastery: Agentic Trading System

## 🎯 Overview

**Momentum Mastery** is a mechanical momentum trading system designed to move from speculative small-cap trading to disciplined, large-cap momentum investing. The system combines an Alpha Agent (for trade identification) with a QA Agent (for backtesting and validation) to build a 15-20% annual compounding strategy targeting $4M-$10M net worth growth.

### Core Philosophy
- ✅ **Mechanical Rules**: No emotion, no "gut feels"
- ✅ **Large Caps Only**: Market Cap > $2B (goodbye penny stocks)
- ✅ **Protected Downside**: Max 15% drawdown tolerance via circuit breakers
- ✅ **Modular Architecture**: Small, testable pieces of code

---

## 📊 The Strategy

### Primary Signal: 12-1 Month Relative Strength
1. **Calculate** 12-month returns across market cap > $2B universe
2. **Remove** the most recent month (avoid mean reversion noise)
3. **Rank** top 10% performers
4. **Filter** with technical circuit breakers

### Technical Filters (The "Circuit Breakers")
- **Bullish Floor**: Price must be above 200-day SMA
- **Momentum Trigger**: Price crossing above 60-day SMA (while staying above 200d)
- **Volume Gate**: Daily volume > $10M
- **Volatility Guard**: RSI < 80 (avoid overextended entries)

### Three Proven "Plays"

| Play Name | Setup | Why It Works |
|-----------|-------|-------------|
| **The Golden Staircase** | Price > 60d SMA > 200d SMA | Confirms both short & long-term trends are up |
| **Mean Reversion Bounce** | Price touches 200d SMA but stays above | Institutions defend the 200d line |
| **60d Breakout** | Flat → crosses 60d SMA on volume | Fresh momentum burst after consolidation |

---

## 🤖 The Two Agents

### Alpha Agent (Trade Identification)
**Role**: Scan the market universe and identify high-probability setups
- Filters stocks: Market Cap > $2B
- Calculates: 12-1 momentum scores
- Flags: Golden Staircase, Mean Reversion Bounce, 60d Breakout
- Output: "5 Trades Recommended This Week"

### QA Agent (Backtester & Gatekeeper)
**Role**: Validate Alpha recommendations and learn from failures
- Backtest: 3-year historical test for every Alpha pick
- Report: Maximum Drawdown (MDD) — reject if > 15%
- Feedback: Suggest parameter adjustments if success rate < 60%
- Output: "3/5 Passed Quality Test. Estimated Win Rate: 62%"

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Data** | yfinance (free, Python-based) |
| **Backend** | Python + FastAPI (low-code, spreadsheet-friendly) |
| **Storage** | Google Sheets (via Apps Script) |
| **Alerts** | Slack + Gmail API |
| **Backtest Engine** | Vectorized NumPy/Pandas |

---

## 📁 Project Structure

```
Momentum-Trading-Bot-With-Agentic-QA/
├── README.md                              # This file
├── requirements.txt                        # Python dependencies
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                              # Data fetching module
│   │   ├── __init__.py
│   │   ├── fetcher.py                     # yfinance wrapper
│   │   └── universe_filter.py             # Market cap filtering
│   │
│   ├── alpha_agent/                       # Trade identification
│   │   ├── __init__.py
│   │   ├── momentum_scorer.py             # 12-1 momentum calculation
│   │   ├── technical_filters.py           # MA & RSI checks
│   │   ├── play_detector.py               # Golden Staircase, etc.
│   │   └── alpha_runner.py                # Main execution
│   │
│   ├── qa_agent/                          # Backtester & validator
│   │   ├── __init__.py
│   │   ├── backtest_engine.py             # Historical performance
│   │   ├── drawdown_calculator.py         # MDD computation
│   │   ├── quality_checker.py             # Pass/reject logic
│   │   └── qa_runner.py                   # Main execution
│   │
│   ├── alerts/                            # Slack/Gmail notifications
│   │   ├── __init__.py
│   │   ├── slack_notifier.py
│   │   └── email_notifier.py
│   │
│   └── utils/                             # Shared utilities
│       ├── __init__.py
│       ├── constants.py                   # Market cap, volume thresholds
│       ├── config.py                      # API keys, params
│       └── logging.py                     # Structured logging
│
├── tests/
│   ├── __init__.py
│   ├── test_momentum_scorer.py
│   ├── test_technical_filters.py
│   ├── test_backtest_engine.py
│   └── test_qa_agent.py
│
├── notebooks/                             # Jupyter for exploration
│   └── strategy_analysis.ipynb
│
├── config.example.yml                     # Example configuration
└── main.py                                # Entry point
```

---

## 🚀 Quick Start

### 1. Setup
```bash
# Clone repo
git clone <repo-url>
cd Momentum-Trading-Bot-With-Agentic-QA

# Install dependencies
pip install -r requirements.txt

# Copy and fill config
cp config.example.yml config.yml
# Add your Slack token, Gmail credentials, etc.
```

### 2. Run Alpha Agent (Find Trades)
```bash
python -m src.alpha_agent.alpha_runner
```

### 3. Run QA Agent (Validate Trades)
```bash
python -m src.qa_agent.qa_runner
```

### 4. Generate Report
```bash
python main.py --report
```

---

## 📋 Key Parameters

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| **Min Market Cap** | $2B | Avoid illiquid, volatile small caps |
| **Min Daily Volume** | $10M | Prevent liquidity traps |
| **Momentum Window** | 12-1 months | Industry standard |
| **Max Drawdown** | 15% | Dan's pain threshold |
| **200d SMA** | Price floor | Long-term trend confirmation |
| **60d SMA** | Momentum line | Entry signal |
| **Max RSI** | 80 | Overbought guard |
| **Backtest Period** | 3 years | Sufficient history, recent data |

---

## 📈 Success Metrics

### Weekly Report
```
Alpha Agent suggested: 5 trades
QA Agent approved: 3 trades (60% pass rate)
Rejected: 2 (high volatility, below volume threshold)
Estimated win rate: 62%
Top candidate: AAPL (Golden Staircase setup, MDD: 8%)
```

### Annual Goals
- **Target Return**: 15-20% annual compounding
- **Max Drawdown**: 15% (never worse)
- **Win Rate**: 60%+ on approved trades

---

## 🔧 Development Roadmap

- [ ] Phase 1: Data fetching & universe filtering
- [ ] Phase 2: 12-1 momentum scorer
- [ ] Phase 3: Technical filters (SMA, RSI)
- [ ] Phase 4: Play detector (Golden Staircase, etc.)
- [ ] Phase 5: Backtest engine
- [ ] Phase 6: QA approval logic
- [ ] Phase 7: Slack/Gmail alerts
- [ ] Phase 8: Weekly reporting
- [ ] Phase 9: Parameter optimization
- [ ] Phase 10: Live paper trading

---

## 📞 Configuration

See `config.example.yml` for:
- yfinance settings
- Slack webhook URL
- Gmail API credentials
- Google Sheets integration
- Portfolio limits (max 5 positions, etc.)

---

## 🤝 Feedback Loop

Every Friday:
1. Alpha Agent outputs candidate trades
2. QA Agent backtests each candidate
3. System generates "Friday Quality Report"
4. If win rate < 60%, system suggests:
   - Tighter stop loss (e.g., 15% → 10%)
   - Higher RSI threshold (e.g., 80 → 70)
   - Longer momentum window (e.g., 12 → 15 months)

---

## 📚 References

- Momentum Academic Research: Jegadeesh & Titman (1993)
- 200d SMA as Support: Classic technical analysis
- 60d SMA Breakout: Mean reversion + momentum combo
- Position sizing & risk management: Kelly Criterion

---

## 🛡️ Disclaimers

This system is for educational and paper-trading purposes. Always backtest thoroughly before deploying real capital. Past performance does not guarantee future results.

---

**Built for Dan Pham | Semi-Retired Builder | 2026**
