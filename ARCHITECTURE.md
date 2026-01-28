# System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOMENTUM MASTERY SYSTEM                      │
└─────────────────────────────────────────────────────────────────┘

                         INPUT: Ticker List
                                 ↓
                   ╔═════════════════════════╗
                   ║   DATA FETCHER LAYER    ║
                   ║  (src/data/)            ║
                   ║                         ║
                   ║ • Fetch 5y price data   ║
                   ║ • Fetch market cap info ║
                   ║ • Filter by universe    ║
                   ╚═════════════════════════╝
                                 ↓
                   Eligible Stocks + Price Data
                                 ↓
          ┌──────────────────────┴──────────────────────┐
          ↓                                              ↓
    ╔═════════════════╗                      ╔═════════════════╗
    ║  ALPHA AGENT    ║                      ║  QA AGENT       ║
    ║  (Identify)     ║                      ║  (Validate)     ║
    ╚═════════════════╝                      ╚═════════════════╝
          ↓                                              ↑
    • 12-1 Momentum                              For each Alpha
    • SMA Filters                                recommendation:
    • RSI Guards                                 
    • Play Detection                             • Backtest 3y
      (Golden Staircase,                         • Calculate DD
       Mean Reversion,                           • Check win rate
       60d Breakout)                             • Validate quality
          ↓                                              ↑
    5-10 Trade                                   ✅/⚠️/❌ Vibe
    Recommendations                             Status
          └──────────────────────┬──────────────────────┘
                                 ↓
                   ╔═════════════════════════╗
                   ║   ALERTS & REPORTING    ║
                   ║  (src/alerts/)          ║
                   ║                         ║
                   ║ • Slack webhook         ║
                   ║ • Email (Gmail)         ║
                   ║ • Generate HTML report  ║
                   ╚═════════════════════════╝
                                 ↓
                        OUTPUT: Weekly Report
```

---

## Module Dependencies

```
┌──────────────────────────────────────────────────────────┐
│                       MAIN.PY                            │
│              (Orchestrates full workflow)                │
└──────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        ↓                                 ↓
   ╔─────────────╗                 ╔─────────────╗
   │AlphaRunner  │                 │QARunner     │
   ╚─────────────╝                 ╚─────────────╝
        ↓                                 ↓
   ┌────┴─────────┬────────┐         ┌────┴──────────┬────┐
   ↓              ↓        ↓         ↓               ↓    ↓
DataFetcher  Momentum  Technical   Backtest     Drawdown  Quality
             Scorer    Filters     Engine       Calculator Checker
   ↓              ↓        ↓         ↓               ↓       ↓
PlayDetector  UniverseFilter    ┌────────────────────────────┐
              (circuit breaker)  │   All use Constants.py    │
                                 │   All use Config.py       │
                                 │   All use Logging.py      │
                                 └────────────────────────────┘
```

---

## Data Flow Through System

```
Step 1: DATA FETCHING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
["AAPL", "MSFT", ...] 
   ↓
[yfinance]
   ↓
{"AAPL": {"Open": [...], "Close": [...], "Volume": [...]}, ...}


Step 2: UNIVERSE FILTERING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All Stocks + Market Cap Info
   ↓
Market Cap Filter (> $2B)
   ↓
Volume Filter (> $10M daily)
   ↓
Eligible Universe


Step 3: ALPHA SCORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Price Data (5 years)
   ↓
Calculate 12-1 Momentum
   ↓
Rank by momentum
   ↓
Top 10% performers
   ↓
Calculate SMA 200, SMA 60, RSI
   ↓
Filter by technicals (price > SMA 200, RSI < 80)
   ↓
Detect plays (Golden Staircase, etc.)
   ↓
Trade Recommendations
[ticker, momentum_score, play, confidence, price]


Step 4: QA VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For Each Trade:
   ↓
Fetch 3-year history
   ↓
Run SMA crossover backtest
   ↓
Calculate max drawdown
   ↓
Calculate win rate
   ↓
Compare to thresholds:
  - Win rate ≥ 60%?
  - Max DD ≤ 15%?
  - Profit factor ≥ 1.5?
   ↓
Classify: ✅ Approved / ⚠️ Conditional / ❌ Rejected
   ↓
QA Results with Vibes


Step 5: REPORTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QA Results
   ↓
Generate summary report
   ↓
Send to:
  • Console (print)
  • Slack (optional)
  • Email (optional)
  • logs/ (always)
   ↓
DONE
```

---

## Class Relationships

```
┌────────────────────────────────────────────────────────┐
│                  DATA LAYER                            │
├────────────────────────────────────────────────────────┤
│ DataFetcher                 UniverseFilter             │
│  └─ fetch_historical_data()  └─ apply_circuit_breakers()
│  └─ fetch_ticker_info()      └─ filter_by_market_cap()
│                              └─ filter_by_volume()
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│               ALPHA AGENT LAYER                        │
├────────────────────────────────────────────────────────┤
│ MomentumScorer          TechnicalFilters               │
│  └─ calculate_12_1_      └─ calculate_sma()            │
│     momentum()            └─ calculate_rsi()           │
│  └─ score_universe()      └─ is_above_200d_sma()      │
│  └─ get_top_performers()  └─ is_rsi_not_overbought()  │
│                                                        │
│ PlayDetector            AlphaAgentRunner               │
│  └─ detect_golden_       └─ run_scan()                 │
│     staircase()                                        │
│  └─ detect_mean_                                      │
│     reversion_bounce()                                 │
│  └─ detect_60d_breakout()                             │
│  └─ classify_play()                                    │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│                QA AGENT LAYER                          │
├────────────────────────────────────────────────────────┤
│ BacktestEngine          DrawdownCalculator             │
│  └─ backtest_sma_       └─ calculate_max_              │
│     crossover()          drawdown()                    │
│  └─ analyze_trades()    └─ analyze_drawdown_          │
│                           history()                    │
│                                                        │
│ QualityChecker          QAAgentRunner                  │
│  └─ check_drawdown()    └─ validate_single_trade()   │
│  └─ check_win_rate()    └─ validate_multiple_trades()│
│  └─ evaluate_backtest() └─ generate_qa_report()      │
│  └─ suggest_improvements()                            │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│              ALERTS & UTILS LAYER                      │
├────────────────────────────────────────────────────────┤
│ SlackNotifier           EmailNotifier                  │
│  └─ send_message()      └─ send_email()               │
│  └─ send_trade_alert()  └─ send_trade_alert()         │
│  └─ send_weekly_        └─ send_weekly_report()       │
│     report()                                           │
│                                                        │
│ constants.py  config.py  logging.py                   │
│ (All params)  (Config)   (Logger)                      │
└────────────────────────────────────────────────────────┘
```

---

## Signal Flow: Single Stock Example

```
AAPL
  ↓
[DataFetcher] → 5-year price data
  ↓
[UniverseFilter] 
  ├─ Market Cap: $3.2T ✓ (passes $2B minimum)
  ├─ Daily Volume: $50M ✓ (passes $10M minimum)
  └─ → Eligible ✓
  ↓
[MomentumScorer]
  ├─ Last 12 months return: +35%
  ├─ Skip last month: +35% - (+2%)
  ├─ Final momentum: +32%
  └─ → Rank 5th out of 100 ✓ (top 10%)
  ↓
[TechnicalFilters]
  ├─ Current price: $180
  ├─ 200d SMA: $165 → Price > SMA ✓
  ├─ 60d SMA: $175 → Price > SMA ✓
  ├─ RSI (14): 72 → RSI < 80 ✓
  └─ → Passes all technical filters ✓
  ↓
[PlayDetector]
  ├─ Check Golden Staircase: $180 > $175 > $165 ✓
  ├─ Confidence: 88%
  └─ → Trade Setup: Golden Staircase
  ↓
ALPHA RECOMMENDATION:
┌──────────────────────────────────────┐
│ Ticker: AAPL                         │
│ Momentum Score: 0.32                 │
│ Play: Golden Staircase               │
│ Confidence: 88%                      │
│ Current Price: $180.00               │
└──────────────────────────────────────┘
  ↓
[QAAgentRunner] → For validation
  ↓
[BacktestEngine]
  ├─ Fetch 3-year history
  ├─ Run SMA 60/200 crossover strategy
  ├─ Results: 25 trades, 15 wins, 10 losses
  └─ Win rate: 60%
  ↓
[DrawdownCalculator]
  ├─ Max Drawdown: -12.3%
  ├─ Recovery Time: 45 days
  └─ Volatility (annualized): 18.2%
  ↓
[QualityChecker]
  ├─ Win rate 60% ≥ 60% minimum? ✓
  ├─ Max DD -12.3% ≤ -15% limit? ✓
  ├─ Profit factor 1.8 ≥ 1.5? ✓
  └─ Sample size 25 ≥ 5? ✓
  ↓
QA APPROVAL:
┌──────────────────────────────────────┐
│ Vibe: ✅ APPROVED                    │
│ Confidence: HIGH                     │
│ Win Rate: 60.0% ✓                    │
│ Max Drawdown: -12.3% ✓               │
│ Profit Factor: 1.8 ✓                 │
│ All Checks: PASS                     │
│ Suggestions: None                    │
└──────────────────────────────────────┘
  ↓
WEEKLY REPORT:
"• AAPL: Golden Staircase (WR: 60%, DD: 12.3%)"
```

---

## Testing Structure

```
tests/
├── test_momentum_scorer.py
│   ├─ test_calculate_monthly_returns()
│   ├─ test_calculate_12_1_momentum()
│   ├─ test_empty_data()
│   └─ test_score_universe()
│
├── test_technical_filters.py
│   ├─ test_calculate_sma()
│   ├─ test_calculate_rsi()
│   ├─ test_is_above_200d_sma()
│   └─ test_is_rsi_not_overbought()
│
├── test_backtest_engine.py
│   ├─ test_analyze_trades()
│   ├─ test_empty_trades()
│   └─ test_backtest_sma_crossover()
│
└── test_qa_agent.py
    ├─ test_check_drawdown_passes()
    ├─ test_check_drawdown_fails()
    ├─ test_check_win_rate_passes()
    ├─ test_check_win_rate_fails()
    └─ test_evaluate_backtest()
```

---

## Configuration & Constants

```
CONFIG.PY (from .env):
├─ SLACK_WEBHOOK_URL
├─ SLACK_BOT_TOKEN
├─ GOOGLE_SHEETS_ID
├─ EMAIL_ADDRESS
├─ EMAIL_PASSWORD
├─ DEBUG_MODE
├─ LOG_LEVEL
├─ PORTFOLIO_SIZE_USD
└─ MAX_DRAWDOWN_TOLERANCE_PCT

CONSTANTS.PY (hardcoded thresholds):
├─ MIN_MARKET_CAP_USD = $2B
├─ MIN_DAILY_VOLUME_USD = $10M
├─ MAX_RSI = 80
├─ MAX_DRAWDOWN_PCT = 15%
├─ MIN_WIN_RATE_PCT = 60%
├─ SMA_200_PERIOD = 200
├─ SMA_60_PERIOD = 60
├─ RSI_PERIOD = 14
├─ MOMENTUM_WINDOW_MONTHS = 12
├─ MOMENTUM_SKIP_MONTHS = 1
├─ BACKTEST_YEARS = 3
└─ MAX_POSITIONS = 5
```

---

## Error Handling

```
DataFetcher
  └─ No data → Empty DataFrame → Log warning

UniverseFilter
  └─ Insufficient data → Filter out → Log debug

MomentumScorer
  └─ < 37 months data → Return 0.0 → Log warning

TechnicalFilters
  └─ NaN values → Check before returning → Safe

PlayDetector
  └─ Missing signals → Return (False, 0.0) → Safe

BacktestEngine
  └─ Empty trades → Return default stats → Log

QualityChecker
  └─ Failed checks → Suggest improvements → Log

Alerts
  └─ No webhook URL → Log warning → Continue
```

---

**All modules are designed to fail gracefully and continue operation.**

**Built for Dan Pham | 2026**
