# Research 26 - Hedge Fund Strategy Document

## 1. Mission & Edge

### Mission
Run a lean, AI-augmented trading operation from a single manager's desk that achieves institutional-grade returns and risk control without a large team or physical trading floor.

### Edge
- **Multiple small, decorrelated edges** across market microstructure, events, options volatility, and slow factor tilts
- **AI agents handle** data ingestion, research, execution, and risk monitoring, freeing you to act as CIO/portfolio manager
- **Ruthless cost discipline** and regime-aware allocation to keep Sharpe high and drawdowns shallow

## 2. Return & Risk Targets

- **Sharpe ratio (portfolio)**: ≥ 5
- **CAGR**: ≥ 200%
- **Max drawdown**: ≤ 12% rolling 30-day
- **Portfolio vol target**: 35–45% annualized (enough to reach 200%+ CAGR given Sharpe)

## 3. Market Universe

- **Equities**: US large/mid caps + high-ADV ETFs (SPY, QQQ, sector ETFs)
- **Options**: Liquid single-name and ETF options for event-driven vol trades
- **Optional later**: Liquid index futures for drift patterns, hedging

## 4. Strategy Pillars

### Pillar A – Micro-Edges (short-hold, high Sharpe)
- Overnight reversion, close-fade, intraday mean-reversion
- Opening/closing patterns, ETF–basket mispricing (approximation)

### Pillar B – Event-Driven (medium hold, bursts of alpha)
- Post-earnings drift, guidance/call-tone drift, analyst revision clusters
- Supply-chain echo, corporate action drift

### Pillar C – Volatility/Options (convexity, risk-capped)
- Pre-earnings straddles/calendars, earnings vol-skew selector
- Macro-day long vol, hedged variance-risk-premium harvesting

### Pillar D – Slow Tilts (capacity & balance)
- Weekly momentum (sector/beta neutral), low-beta, quality/profitability
- Conservative investment, net share issuance

## 5. Portfolio Construction

### Sleeve Vol Targets
- **A**: 10–12%
- **B**: 12–15%
- **C**: 6–8%
- **D**: 8–10%

### Total Target Vol: 35–45%
Adjusted via 4-state regime switcher:
- **Trend / Low vol** → Upweight momentum + PEAD
- **Trend / High vol** → Tilt to micro edges + vol
- **Chop / Low vol** → Keep mix balanced
- **Chop / High vol** → Concentrate in micro edges + vol

### Sizing
Equal-risk contribution across active sleeves; scale each sleeve's gross based on recent decay or cost blowouts.

## 6. Risk Framework

### Position Limits
- **Single-name cap**: ≤ 3% NAV
- **Sector cap**: ≤ 15% NAV
- **Gross exposure**: ≤ 150% NAV
- **Net exposure**: ± 50% NAV

### Circuit Breakers
- **−1.5% daily** → halve gross
- **−2% daily** → flatten to 25% gross
- **−12% 30-day drawdown** → safe mode (A + C only) until recovery

### Additional Controls
- Per-trade loss caps in option/vol sleeves
- Daily vega caps

## 7. Operating Model

### One-human + AI agents:
- **Chief Data Officer AI**: Data collection, cleaning, schema checks
- **Strategist AI**: Feature creation, model training/backtesting, new idea proposals
- **Execution Trader AI**: Order routing, slippage minimization, execution scheduling
- **Risk Officer AI**: Real-time limits, VaR, circuit breakers
- **Performance Analyst AI**: PnL attribution, TCA, model decay monitoring
- **Ops/SRE AI**: Infra health, failover, secrets

## 8. Technology Stack

### Local
- Jupyter + Python for R&D, quick tests, visualization

### AWS Cloud
- **EC2 small CPU (24/7)** — live trading, schedulers, dashboards
- **EC2 GPU spot (on-demand)** — GRU/TCN or other heavy model training
- **S3** — raw + processed data, model artifacts
- **RDS Postgres** — trades, fills, model registry, risk states
- **Secrets Manager** — key storage
- **CloudWatch/Grafana/Prefect** — monitoring + alerts
- **Warm standby EC2 instance** for failover

## 9. Model Philosophy

- **Baselines first** (LightGBM, linear models) → sanity check
- **Deep learning selectively** (GRU/TCN) where patterns are non-linear and persistent
- **Walk-forward validation** with leakage checks; regime-segmented analysis
- **Decision target**: classes/quantiles of forward returns, not raw regression
- **Cost-aware objective**: train/evaluate on after-cost returns

## 10. Deployment Process

1. **Backtest** with realistic costs + slippage; stress spreads and fills
2. **Paper trade** 30+ days; track live vs backtest performance
3. **Go-live tiny** (10–20% intended gross); promote if daily Sharpe > 0.18 and no risk breaches
4. **Auto-deweight** sleeves with drawdown > 50% of budget or hit-rate decay
5. **Quarterly**: add/retire sleeves; refresh features/models; capacity tests

## 11. Cost Discipline

### Trading Rules
- Trade only top-ADV names in micro/event sleeves
- MOC/MOO for short-hold mean-reversion; IS/TWAP for event/factor tilts
- Options only in top-tier liquidity; limit orders; scheduled delta trims

### Target Slippage
- **Micro**: 3–6 bps
- **Event/Factor**: 8–12 bps
- **Options spreads**: ≤ 1% mid

## 12. Operating Rhythm

### Daily (≤ 1h)
Review dashboards (PnL, exposure, risk), respond to alerts, journal notes

### Weekly (90 min)
AI strategy council — promote/demote, drift checks, sandbox decisions

### Monthly
Retrain/refit where needed; update meta-weights; TCA review

### Quarterly
Sleeve turnover; stress tests; capacity expansion

## 13. Documentation

- **Risk policy** (1-page)
- **Runbook** (1-page)
- **Model cards** (per sleeve)
- **Changelog** (all code/model changes)
- **Postmortems** (any incidents)

## 14. Scaling Path

### $100k–500k
Micro + event sleeves; keep borrow/costs minimal

### $500k–2M
Add factor tilts + diversified vol sleeves

### $2M–10M
Expand universes, modest leverage, more events

### 10M+
More sleeves, multiple asset classes, capacity-aware meta-allocator

---

**Research 26** - Institutional-grade performance through AI-augmented systematic trading.
