# Momentum Mastery: Codebase Summary

## What Was Built

A **modular, production-ready trading system** for identifying large-cap momentum trades and validating them with backtesting. The system uses an **Alpha Agent** (to find trades) and a **QA Agent** (to validate trades).

---

## Complete File Structure

```
Momentum-Trading-Bot-With-Agentic-QA/
│
├── README.md                           # Project overview (START HERE)
├── QUICKSTART.md                       # Quick start guide (run the system)
├── DEVELOPMENT.md                      # Architecture & dev guide (extend system)
├── requirements.txt                    # Python dependencies
├── .env.example                        # Configuration template
├── .gitignore                          # Git ignore rules
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fetcher.py                  # 🔽 Fetch price data from yfinance
│   │   └── universe_filter.py          # 🚪 Circuit breakers (market cap, volume)
│   │
│   ├── alpha_agent/
│   │   ├── __init__.py
│   │   ├── momentum_scorer.py          # 📊 Calculate 12-1 momentum
│   │   ├── technical_filters.py        # 📈 Calculate SMA & RSI
│   │   ├── play_detector.py            # 🎯 Detect trade setups
│   │   └── alpha_runner.py             # 🚀 Main Alpha Agent orchestrator
│   │
│   ├── qa_agent/
│   │   ├── __init__.py
│   │   ├── backtest_engine.py          # 🧪 Run historical backtests
│   │   ├── drawdown_calculator.py      # 📉 Calculate risk metrics
│   │   ├── quality_checker.py          # ✅ Validate trades
│   │   └── qa_runner.py                # 🔍 Main QA Agent orchestrator
│   │
│   ├── alerts/
│   │   ├── __init__.py
│   │   ├── slack_notifier.py           # 💬 Slack webhooks
│   │   └── email_notifier.py           # 📧 Gmail integration
│   │
│   └── utils/
│       ├── __init__.py
│       ├── constants.py                # 🎯 All thresholds & parameters
│       ├── config.py                   # ⚙️ Config management
│       └── logging.py                  # 📝 Structured logging
│
├── tests/
│   ├── __init__.py
│   ├── test_momentum_scorer.py
│   ├── test_technical_filters.py
│   ├── test_backtest_engine.py
│   └── test_qa_agent.py
│
├── logs/                               # 📋 Runtime logs (auto-created)
│
└── main.py                             # 🎬 Main entry point
```

---

## Core Components Explained

### 1️⃣ **Data Module** (`src/data/`)
- **Purpose**: Fetch and filter market data
- **Key Classes**:
  - `DataFetcher`: Wraps yfinance, fetches OHLCV data
  - `UniverseFilter`: Applies circuit breakers (market cap > $2B, volume > $10M)
- **Output**: Cleaned price data + eligible stock list

### 2️⃣ **Alpha Agent** (`src/alpha_agent/`)
- **Purpose**: Identify high-probability trades
- **Key Classes**:
  - `MomentumScorer`: Calculates 12-1 relative strength (past 12 months, skip recent)
  - `TechnicalFilters`: Calculates SMAs (200d, 60d) and RSI (14)
  - `PlayDetector`: Identifies three setups:
    - **Golden Staircase**: Price > 60d SMA > 200d SMA (strongest signal)
    - **Mean Reversion Bounce**: Price near 200d SMA (support defense)
    - **60d Breakout**: Price breaks above 60d SMA on volume
  - `AlphaAgentRunner`: Orchestrates the full scan
- **Output**: DataFrame with trade recommendations (ticker, momentum_score, play, confidence, price)

### 3️⃣ **QA Agent** (`src/qa_agent/`)
- **Purpose**: Validate trades with backtesting
- **Key Classes**:
  - `BacktestEngine`: Runs 3-year historical tests with SMA crossover strategy
  - `DrawdownCalculator`: Computes max drawdown, recovery time, volatility
  - `QualityChecker`: Validates against criteria:
    - Win rate ≥ 60%
    - Max drawdown ≤ 15%
    - Min 5 trades in backtest
    - Profit factor ≥ 1.5
  - `QAAgentRunner`: Orchestrates validation and generates reports
- **Output**: DataFrame with pass/reject decisions (vibe status, confidence level)

### 4️⃣ **Alerts** (`src/alerts/`)
- **Purpose**: Send notifications
- **Key Classes**:
  - `SlackNotifier`: Posts to Slack webhook
  - `EmailNotifier`: Sends via Gmail SMTP
- **Features**: Trade alerts, weekly reports

### 5️⃣ **Utils** (`src/utils/`)
- **Purpose**: Shared infrastructure
- **Key Components**:
  - `constants.py`: All tunable parameters (circuit breaker thresholds, MA periods, etc.)
  - `config.py`: Environment config management
  - `logging.py`: Structured logging to console + file

---

## How It Works (Step by Step)

### **Phase 1: Alpha Agent Scan**
1. Fetch price data for all tickers (5 years)
2. Filter by market cap (> $2B) and volume (> $10M)
3. Calculate 12-1 momentum for remaining stocks
4. Identify top 10% performers
5. Apply technical filters (above 200d/60d SMA, RSI < 80)
6. Detect trade setups (Golden Staircase, etc.)
7. Output: 5-10 trade recommendations

### **Phase 2: QA Agent Validation**
1. For each Alpha recommendation:
   - Fetch 3-year historical data
   - Run backtest with SMA crossover strategy
   - Calculate max drawdown and win rate
   - Validate against thresholds
2. Classify each trade:
   - ✅ **Approved**: Passes all criteria (high confidence)
   - ⚠️ **Conditional**: Passes some criteria (medium confidence)
   - ❌ **Rejected**: Fails thresholds (provide suggestions to improve)
3. Generate summary report

### **Phase 3: Reporting & Alerts**
1. Print detailed report to console
2. (Optional) Send to Slack
3. (Optional) Send HTML email report
4. Save logs for analysis

---

## Key Design Decisions

### ✅ **Modularity First**
- Each module is independent and can be tested/used separately
- Minimal cross-dependencies
- Easy to add new features without modifying existing code

### ✅ **Small, Focused Functions**
- Each function does ONE thing well
- Reduces risk of bugs
- Makes testing straightforward

### ✅ **Centralized Configuration**
- All thresholds in `constants.py`
- All credentials in `.env`
- Easy to tune without changing code

### ✅ **Comprehensive Logging**
- Every major step logged
- Debug logs to file, info to console
- Timestamps for analysis

### ✅ **No External Dependencies on Execution**
- System runs WITHOUT Slack/email configured
- Alerts are optional, not required
- Graceful degradation

---

## What Each File Does

| File | Purpose | Key Functions |
|------|---------|----------------|
| `data/fetcher.py` | Fetch price data | `fetch_historical_data()`, `fetch_ticker_info()` |
| `data/universe_filter.py` | Filter stocks | `apply_circuit_breakers()`, `filter_by_market_cap()` |
| `alpha_agent/momentum_scorer.py` | Score momentum | `calculate_12_1_momentum()`, `score_universe()` |
| `alpha_agent/technical_filters.py` | Calculate technicals | `calculate_sma()`, `calculate_rsi()` |
| `alpha_agent/play_detector.py` | Detect setups | `detect_golden_staircase()`, `detect_60d_breakout()` |
| `alpha_agent/alpha_runner.py` | Orchestrate | `run_scan()` |
| `qa_agent/backtest_engine.py` | Test strategy | `backtest_sma_crossover()`, `analyze_trades()` |
| `qa_agent/drawdown_calculator.py` | Risk metrics | `calculate_max_drawdown()`, `analyze_drawdown_history()` |
| `qa_agent/quality_checker.py` | Validate trades | `evaluate_backtest()`, `suggest_improvements()` |
| `qa_agent/qa_runner.py` | Orchestrate | `validate_multiple_trades()`, `generate_qa_report()` |
| `utils/constants.py` | Parameters | `MIN_MARKET_CAP_USD`, `MAX_RSI`, etc. |
| `utils/config.py` | Configuration | `Config` class with env loading |
| `utils/logging.py` | Logging | `get_logger()`, `MomentumLogger` class |
| `main.py` | Entry point | `MomentumSystem.run_full_scan()` |

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Individual Tests
```bash
pytest tests/test_momentum_scorer.py -v
pytest tests/test_technical_filters.py -v
pytest tests/test_backtest_engine.py -v
pytest tests/test_qa_agent.py -v
```

---

## How to Extend

### Add a New "Play" (Setup Type)
1. Add detection method to `play_detector.py`
2. Register in `classify_play()`

### Add a New Risk Metric
1. Add calculation to `drawdown_calculator.py`
2. Reference in `quality_checker.py`

### Add a New Alert Channel
1. Create notifier class in `alerts/`
2. Import and use in `main.py`

### Modify Parameters
1. Edit values in `src/utils/constants.py`
2. No other code changes needed

---

## Running the System

### Quick Test
```bash
python main.py --tickers AAPL MSFT GOOGL --report
```

### Full Scan
```bash
python main.py --report
```

### Custom Tickers
```bash
python main.py --tickers SPY QQQ IWM --report
```

### Alpha Agent Only
```python
from src.alpha_agent import AlphaAgentRunner
runner = AlphaAgentRunner()
results = runner.run_scan(['AAPL', 'MSFT'])
```

### QA Agent Only
```python
from src.qa_agent import QAAgentRunner
runner = QAAgentRunner()
result = runner.validate_single_trade('AAPL')
```

---

## Thresholds & Parameters

All in `src/utils/constants.py`:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `MIN_MARKET_CAP_USD` | $2B | Avoid penny stocks |
| `MIN_DAILY_VOLUME_USD` | $10M | Avoid illiquid stocks |
| `MAX_RSI` | 80 | Avoid overbought |
| `MAX_DRAWDOWN_PCT` | 15% | Risk limit |
| `MIN_WIN_RATE_PCT` | 60% | Quality threshold |
| `SMA_200_PERIOD` | 200 | Long-term trend |
| `SMA_60_PERIOD` | 60 | Short-term momentum |
| `MOMENTUM_WINDOW_MONTHS` | 12 | Lookback period |

---

## Output Examples

### Alpha Agent Output
```
Ticker | Momentum Score | Play | Confidence | Price
NVDA   | 0.45           | Golden Staircase | 88% | $145.23
MSFT   | 0.38           | Mean Reversion Bounce | 75% | $410.55
```

### QA Agent Output
```
✅ VIBE APPROVED (NVDA)
- Win Rate: 62.5% ✓
- Max Drawdown: 12.3% ✓
- Profit Factor: 1.8 ✓
- Backtest: 25 trades
- Suggestion: None (passed all checks)
```

### Full Report
```
📊 MOMENTUM MASTERY WEEKLY REPORT
Total Evaluated: 5 trades
✅ Approved: 3 trades (60% pass rate)
⚠️ Conditional: 1 trade
❌ Rejected: 1 trade

Approved Trades:
• NVDA: Golden Staircase (WR: 62.5%, DD: 12.3%)
• MSFT: Mean Reversion Bounce (WR: 65.0%, DD: 10.2%)
• GOOGL: 60d Breakout (WR: 58.0%, DD: 14.5%)
```

---

## Performance

- **Alpha Scan**: ~30 seconds (10 tickers)
- **QA Validation**: ~5 seconds per stock
- **Full System**: ~2 minutes (5 tickers)

---

## Next Steps

1. **Setup** → Follow `QUICKSTART.md`
2. **Test** → Run `python main.py --report`
3. **Configure** → Add `.env` with API keys (optional)
4. **Deploy** → Schedule weekly scans
5. **Monitor** → Review logs in `logs/` directory

---

## Architecture Philosophy

**"Small, testable pieces > Big monolithic functions"**

Every module can be:
- ✅ Imported independently
- ✅ Unit tested in isolation
- ✅ Modified without affecting others
- ✅ Understood by reading 100-200 lines of code

This design protects against accidental bugs and makes the system maintainable long-term.

---

**Built for Dan Pham | Semi-Retired Builder | 2026**
