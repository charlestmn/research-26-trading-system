# Research 26 - AI-Augmented Hedge Fund Trading System

## 🎯 Mission Statement

Run a lean, AI-augmented trading operation from a single manager's desk that achieves institutional-grade returns and risk control without a large team or physical trading floor.

## 📊 Performance Targets

- **Sharpe Ratio**: ≥ 5.0
- **CAGR**: ≥ 200%
- **Max Drawdown**: ≤ 12% (rolling 30-day)
- **Portfolio Volatility**: 35-45% annualized

## 🏗️ System Architecture

### AI Agent Framework
- **Chief Data Officer AI**: Data ingestion, validation, quality monitoring
- **Strategist AI**: Feature engineering, model training, strategy development
- **Execution Trader AI**: Order routing, slippage minimization, fill optimization
- **Risk Officer AI**: Real-time limits, VaR monitoring, circuit breakers
- **Performance Analyst AI**: PnL attribution, TCA, model decay detection
- **Ops/SRE AI**: Infrastructure health, failover, security management

### Strategy Pillars

#### Pillar A - Micro Edges (22% portfolio vol)
- **A1**: Overnight Reversion (11% vol)
- **A2**: Close-Fade (11% vol)

#### Pillar B - Event-Driven (27% portfolio vol)
- **B1**: Post-Earnings Drift (13.5% vol)
- **B2**: Guidance Tone (13.5% vol)

#### Pillar C - Options/Volatility (14% portfolio vol)
- **C1**: Pre-Earnings Straddles (7% vol)
- **C2**: Pre-Earnings Calendars (7% vol)

#### Pillar D - Slow Tilts (17% portfolio vol)
- **D1**: Weekly Momentum (8.5% vol)
- **D2**: Quality Tilt (8.5% vol)

## 🛡️ Risk Management

### Position Limits
- Single name: ≤ 3% NAV
- Sector: ≤ 15% NAV
- Gross exposure: ≤ 150% NAV
- Net exposure: ±50% NAV

### Circuit Breakers
- **-1.5% daily** → halve gross exposure
- **-2.0% daily** → flatten to 25% gross
- **-12% 30-day drawdown** → safe mode (A + C pillars only)

### Regime-Aware Allocation
4-state regime detection (Trend/Chop × High/Low Vol) with dynamic strategy weighting.

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your API keys
```

### Local Development
```bash
# Run backtests
python src/core/backtest_engine.py

# Start live trading (paper mode)
python src/core/trading_engine.py --paper

# Launch monitoring dashboard
python src/monitoring/dashboard.py
```

### Cloud Deployment
```bash
# Deploy to AWS
./scripts/deploy.sh production

# Monitor system health
./scripts/health_check.sh
```

## 📁 Repository Structure

```
research-26-trading-system/
├── src/
│   ├── strategies/          # 4-pillar strategy implementations
│   ├── core/               # Framework & engines
│   ├── data/               # Data pipeline & feeds
│   ├── execution/          # Order management & fills
│   ├── risk/               # Risk management & limits
│   ├── ml/                 # AI/ML pipeline
│   └── monitoring/         # Dashboards & alerts
├── tests/                  # Unit & integration tests
├── config/                 # Environment configurations
├── scripts/                # Deployment & utility scripts
├── notebooks/              # Research & analysis
├── docs/                   # Documentation & model cards
└── archive_v10_legacy/     # Previous system versions
```

## 📈 Performance Tracking

### Daily Metrics
- Portfolio PnL and attribution
- Risk metrics (VaR, exposure, correlation)
- Strategy performance and decay monitoring
- Execution quality (slippage, fill rates)

### Weekly Reviews
- AI strategy council meetings
- Model performance evaluation
- Risk limit adjustments
- New strategy sandbox decisions

### Monthly Operations
- Model retraining and validation
- Meta-weight optimization
- Transaction cost analysis
- Capacity expansion planning

## 🔧 Technology Stack

- **Local**: Jupyter + Python for R&D
- **Cloud**: AWS (EC2, S3, RDS, Lambda)
- **Data**: Alpaca, IEX Cloud, Alpha Vantage
- **ML**: scikit-learn, XGBoost, PyTorch
- **Monitoring**: CloudWatch, Grafana
- **Orchestration**: Prefect, Docker

## 📚 Documentation

- [Mission Statement](MISSION_STATEMENT.md) - Complete hedge fund strategy
- [Technical Architecture](TECHNICAL_ARCHITECTURE.md) - System design details
- [Risk Policy](RISK_POLICY.md) - Risk management framework
- [Runbook](RUNBOOK.md) - Operational procedures
- [Model Cards](docs/model_cards/) - Strategy documentation
- [Changelog](CHANGELOG.md) - System change history

## 🎯 Scaling Path

- **$100k-500k**: Micro + event sleeves, minimal costs
- **$500k-2M**: Add factor tilts + diversified vol sleeves
- **$2M-10M**: Expand universes, modest leverage, more events
- **$10M+**: Multiple asset classes, capacity-aware meta-allocator

## 📞 Support

For issues, feature requests, or questions:
- Create an issue in this repository
- Review the [troubleshooting guide](docs/troubleshooting.md)
- Check the [FAQ](docs/faq.md)

---

**Research 26** - Where AI meets institutional-grade trading excellence.
