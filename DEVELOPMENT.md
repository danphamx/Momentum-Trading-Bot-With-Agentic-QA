# Development Guide

## Architecture Overview

The Momentum Mastery system is built with **modular, isolated components** to minimize risk and enable easy testing/modification.

### Core Principles

1. **Single Responsibility**: Each module does ONE thing well
2. **Testability**: Every module has minimal dependencies
3. **Composability**: Modules can be used independently or together
4. **Logging**: Comprehensive structured logging throughout

---

## Project Structure

```
src/
├── data/                    # Data fetching & filtering
│   ├── fetcher.py          # yfinance wrapper
│   └── universe_filter.py  # Market cap/volume checks
│
├── alpha_agent/            # Trade identification
│   ├── momentum_scorer.py  # 12-1 momentum calculation
│   ├── technical_filters.py # MA & RSI calculations
│   ├── play_detector.py    # Setup detection (Golden Staircase, etc.)
│   └── alpha_runner.py     # Main orchestrator
│
├── qa_agent/              # Backtesting & validation
│   ├── backtest_engine.py # Historical testing
│   ├── drawdown_calculator.py # Risk metrics
│   ├── quality_checker.py # Pass/reject logic
│   └── qa_runner.py       # Main orchestrator
│
├── alerts/                # Notifications
│   ├── slack_notifier.py
│   └── email_notifier.py
│
└── utils/                 # Shared utilities
    ├── constants.py       # Thresholds & parameters
    ├── config.py          # Configuration management
    └── logging.py         # Structured logging
```

---

## Key Modules Explained

### 1. Data Module (`src/data/`)

**Purpose**: Fetch and filter market data

**Key Classes**:
- `DataFetcher`: Wraps yfinance for consistent data retrieval
- `UniverseFilter`: Applies circuit breakers (market cap, volume)

**Example**:
```python
from src.data import DataFetcher, UniverseFilter

fetcher = DataFetcher()
data = fetcher.fetch_historical_data("AAPL", period="5y")

filter_obj = UniverseFilter()
eligible = filter_obj.apply_circuit_breakers(stocks_info)
```

### 2. Alpha Agent (`src/alpha_agent/`)

**Purpose**: Identify high-probability trade setups

**Key Classes**:
- `MomentumScorer`: Calculates 12-1 momentum
- `TechnicalFilters`: Computes SMAs, RSI
- `PlayDetector`: Identifies Golden Staircase, Mean Reversion Bounce, 60d Breakout
- `AlphaAgentRunner`: Orchestrates the scan

**Example**:
```python
from src.alpha_agent import AlphaAgentRunner

runner = AlphaAgentRunner()
recommendations = runner.run_scan(["AAPL", "MSFT", "GOOGL"])
# Returns: DataFrame with ticker, momentum_score, play, confidence
```

### 3. QA Agent (`src/qa_agent/`)

**Purpose**: Validate trades with backtesting and risk analysis

**Key Classes**:
- `BacktestEngine`: Runs historical tests on strategies
- `DrawdownCalculator`: Computes max drawdown and recovery metrics
- `QualityChecker`: Validates against drawdown/win rate thresholds
- `QAAgentRunner`: Orchestrates validation

**Example**:
```python
from src.qa_agent import QAAgentRunner

qa_runner = QAAgentRunner()
qa_results = qa_runner.validate_multiple_trades(alpha_recommendations)
report = qa_runner.generate_qa_report(qa_results)
```

### 4. Alerts (`src/alerts/`)

**Purpose**: Send notifications

**Key Classes**:
- `SlackNotifier`: Slack webhook integration
- `EmailNotifier`: Gmail SMTP integration

---

## Adding a New Feature

### Example: Add Support for RSI Divergence

1. **Create the detector** in `src/alpha_agent/`:
   ```python
   # divergence_detector.py
   class DivergenceDetector:
       def detect_rsi_divergence(self, prices, rsi_values):
           # Your logic here
           return divergence_signal
   ```

2. **Integrate with PlayDetector**:
   ```python
   # In play_detector.py, add method
   def detect_rsi_divergence(self, ...):
       detector = DivergenceDetector()
       return detector.detect_rsi_divergence(...)
   ```

3. **Add tests**:
   ```python
   # tests/test_divergence_detector.py
   def test_detect_rsi_divergence():
       # Your tests
   ```

4. **Update AlphaAgentRunner** to use the new detector

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_momentum_scorer.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

---

## Modifying Parameters

All thresholds are centralized in `src/utils/constants.py`:

```python
MIN_MARKET_CAP_USD = 2_000_000_000  # Change to allow smaller caps
MAX_RSI = 80                         # Change overbought threshold
SMA_200_PERIOD = 200                # Change long-term MA period
MOMENTUM_WINDOW_MONTHS = 12         # Change momentum lookback
MAX_DRAWDOWN_PCT = 15               # Change max acceptable drawdown
```

---

## Extending the System

### Add a New "Play" Type

1. Add detection logic to `src/alpha_agent/play_detector.py`:
   ```python
   def detect_my_new_play(self, technicals):
       # Return (bool, confidence_score)
   ```

2. Register in `classify_play()` method

### Add a New Risk Metric

1. Add calculation to `src/qa_agent/drawdown_calculator.py`
2. Reference in `src/qa_agent/quality_checker.py`

### Add a New Alert Channel

1. Create `src/alerts/new_channel_notifier.py`
2. Import and use in `main.py`

---

## Debugging

### Enable Debug Mode

Set in `.env`:
```
DEBUG_MODE=True
LOG_LEVEL=DEBUG
```

### View Logs

Logs are saved to `logs/` directory with timestamps.

### Trace a Specific Ticker

```python
from src.alpha_agent import AlphaAgentRunner

runner = AlphaAgentRunner()
results = runner.run_scan(["AAPL"])

# Check detailed logs in logs/ folder
```

---

## Performance Notes

### Data Fetching
- Each ticker requires 1 yfinance call
- For 100+ tickers, consider rate limiting

### Backtesting
- 3-year backtest on single stock: ~1-2 seconds
- Vectorized operations (NumPy/Pandas) for speed

### QA Validation
- Validating 5 trades: ~5-10 seconds
- Dominated by backtest time, not calculation

---

## Next Steps

1. **Setup**: Copy `.env.example` to `.env` and add your API keys
2. **Test**: Run `pytest tests/` to verify setup
3. **Scan**: Run `python main.py` to test the full workflow
4. **Deploy**: Schedule via cron/Task Scheduler for weekly scans

---

**Built for Dan Pham | 2026**
