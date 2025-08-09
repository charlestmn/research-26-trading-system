# Research 26 - Operations Runbook

## Daily Operations (≤ 1 hour)

### Pre-Market (8:30 AM ET)
1. **System Health Check**
   - Verify all data feeds active
   - Check overnight model runs completed
   - Review any alerts from Risk Officer AI

2. **Market Preparation**
   - Review economic calendar for events
   - Check earnings announcements
   - Validate position reconciliation

### Market Hours (9:30 AM - 4:00 PM ET)
1. **Real-Time Monitoring**
   - Dashboard: PnL, exposure, risk metrics
   - Alert response: <5 min for critical alerts
   - Circuit breaker monitoring

2. **Execution Oversight**
   - Monitor fill quality and slippage
   - Review Execution Trader AI decisions
   - Validate order routing performance

### Post-Market (4:00 PM - 6:00 PM ET)
1. **Daily Review**
   - PnL attribution by strategy
   - Risk metrics vs limits
   - Model performance scores
   - Journal key observations

## Weekly Operations (90 minutes)

### AI Strategy Council Meeting
1. **Performance Review** (30 min)
   - Strategy Sharpe ratios vs targets
   - Drawdown analysis by pillar
   - Model decay detection results

2. **Risk Assessment** (30 min)
   - Correlation matrix review
   - Regime detection accuracy
   - Limit utilization analysis

3. **Strategy Decisions** (30 min)
   - Promote/demote underperforming sleeves
   - Sandbox new strategy ideas
   - Meta-weight adjustments

## Monthly Operations

### Model Maintenance
- Retrain models showing decay
- Update feature engineering pipelines
- Refresh regime detection parameters

### Performance Analysis
- Transaction cost analysis
- Capacity utilization review
- Benchmark comparison (Sharpe, CAGR, drawdown)

## Emergency Procedures

### Circuit Breaker Activation
1. **Level 1 (-1.5% daily)**: Auto-halve gross exposure
2. **Level 2 (-2.0% daily)**: Auto-flatten to 25% gross
3. **Level 3 (-12% 30-day)**: Manual safe mode activation

### System Failures
1. **Data Feed Loss**: Halt trading, activate backup feeds
2. **Model Failure**: Revert to baseline linear models
3. **Broker Issues**: Switch to backup execution venue
4. **Kill Switch**: Flatten all positions within 15 minutes

### Contact Information
- **Primary Broker**: Alpaca Markets
- **Backup Broker**: Interactive Brokers
- **Data Provider**: IEX Cloud (backup)
- **Cloud Provider**: AWS Support

## Key Metrics Dashboard

### Performance (Daily)
- Portfolio PnL ($ and %)
- Sharpe ratio (rolling 30-day)
- Max drawdown (rolling 30-day)
- Strategy attribution

### Risk (Real-Time)
- Gross/net exposure
- Single name concentrations
- Sector exposures
- VaR (95% 1-day)

### Execution (Daily)
- Average slippage by strategy
- Fill rates and timing
- Order routing efficiency
- Market impact analysis

---
*Emergency Contact: [Your Phone] | Last Updated: August 2025*
