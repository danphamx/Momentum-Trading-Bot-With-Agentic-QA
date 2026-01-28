# Quick Start Guide

## 1. Setup (First Time Only)

### Clone & Install
```bash
cd Momentum-Trading-Bot-With-Agentic-QA
pip install -r requirements.txt
```

### Configure
```bash
# Copy example config
cp .env.example .env

# Edit .env and add:
# - SLACK_WEBHOOK_URL (optional, for alerts)
# - EMAIL_ADDRESS & EMAIL_PASSWORD (optional, for email alerts)
# - GOOGLE_SHEETS_ID (optional, for spreadsheet integration)
```

## 2. Test the System

### Quick Test (Alpha Agent Only)
```bash
python -c "
from src.alpha_agent import AlphaAgentRunner

runner = AlphaAgentRunner()
results = runner.run_scan(['AAPL', 'MSFT', 'GOOGL', 'NVDA'])
print(results)
"
```

### Full Workflow Test
```bash
python main.py --tickers AAPL MSFT GOOGL NVDA --report
```

Expected output:
```
🚀 MOMENTUM MASTERY SYSTEM STARTING
[PHASE 1] Alpha Agent Scan
[PHASE 2] QA Agent Validation
[PHASE 3] Report Generation
✅ MOMENTUM MASTERY SYSTEM COMPLETE
```

## 3. Run Scans

### Scan Large-Cap Tech
```bash
python main.py --tickers AAPL MSFT GOOGL NVDA META AMZN NFLX TSLA --report
```

### Scan S&P 500 (Sample)
```bash
python main.py --tickers SPY QQQ IWM IWN IVE IVW --report
```

### Custom Ticker List
```bash
python main.py --tickers AAPL MSFT JPM JNJ PG --report
```

## 4. Understand the Output

### Alpha Agent Output
```
Alpha Agent found 5 trade recommendations
Ticker | Momentum Score | Play | Confidence | Price
NVDA   |  0.45          | Golden Staircase | 88% | $145.23
```

### QA Agent Output
```
✅ VIBE APPROVED
- Ticker: NVDA
- Win Rate: 62.5% (Passed)
- Max Drawdown: 12.3% (Passed, within 15% limit)
- Backtest: 25 trades analyzed
```

### Weekly Report
```
📊 MOMENTUM MASTERY WEEKLY REPORT
Total Evaluated: 5 trades
✅ Approved: 3
⚠️ Conditional: 1
❌ Rejected: 1
Pass Rate: 80%
```

## 5. Common Commands

### Run Alpha Agent Only
```python
from src.alpha_agent import AlphaAgentRunner
runner = AlphaAgentRunner()
results = runner.run_scan(["AAPL"])
print(results[['ticker', 'play', 'confidence', 'price']])
```

### Run QA Agent Only
```python
from src.qa_agent import QAAgentRunner
runner = QAAgentRunner()
result = runner.validate_single_trade("AAPL", backtest_period_years=3)
print(result['vibe'])
```

### Check System Logs
```bash
# View latest logs
cat logs/momentum_*.log | tail -100

# View specific component
grep "alpha_agent" logs/momentum_*.log
```

## 6. Troubleshooting

### Error: "No data returned for TICKER"
- Check ticker symbol is correct (AAPL, not apple)
- Try a different ticker (yfinance occasionally has issues)

### Error: "Slack webhook URL not configured"
- This is normal if you haven't set up Slack alerts
- System will still work without alerts

### Slow Performance
- First run takes longer to fetch data
- Subsequent runs are faster (data cached)
- QA validation (backtesting) takes 1-2 sec per stock

### Empty Results
- No trades passed Alpha filters
- Try scanning different tickers
- Check parameters in `src/utils/constants.py`

## 7. Fine-Tuning

### Increase Sensitivity (Find More Trades)
```python
# In constants.py
MIN_MARKET_CAP_USD = 1_000_000_000  # Lower from $2B to $1B
MAX_RSI = 85  # Raise from 80 to 85
```

### Increase Selectivity (Find Better Trades)
```python
# In constants.py
MAX_DRAWDOWN_PCT = 10  # Lower from 15% to 10%
MIN_WIN_RATE_PCT = 70  # Raise from 60% to 70%
```

## 8. Weekly Workflow

**Every Friday Morning:**
1. Run full scan: `python main.py --report`
2. Review approved trades
3. Log results for tracking
4. Make any parameter adjustments based on outcomes

**Monthly Review:**
1. Analyze win rate on previous trades
2. Update stop loss if needed
3. Adjust momentum window based on market conditions

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `main.py` | Entry point, orchestrates full workflow |
| `src/alpha_agent/alpha_runner.py` | Alpha Agent main logic |
| `src/qa_agent/qa_runner.py` | QA Agent main logic |
| `src/utils/constants.py` | All tunable parameters |
| `.env` | API keys and config (DON'T commit) |
| `logs/` | System execution logs |

---

## Next Steps

1. ✅ **Setup**: Complete the Setup section above
2. ✅ **Test**: Run the Quick Test
3. ✅ **Explore**: Modify a ticker and re-run
4. ✅ **Integrate**: Connect Slack/email alerts
5. ✅ **Schedule**: Set up weekly cron job

---

**Questions?** See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed architecture and module documentation.

**Built for Dan Pham | 2026**
