# Research 26 - Risk Policy

## Position Limits
- **Single Name**: ≤ 3% NAV
- **Sector**: ≤ 15% NAV  
- **Gross Exposure**: ≤ 150% NAV
- **Net Exposure**: ±50% NAV

## Circuit Breakers
- **Daily Loss -1.5%**: Halve gross exposure immediately
- **Daily Loss -2.0%**: Flatten to 25% gross exposure
- **30-Day Drawdown -12%**: Safe mode (Pillars A + C only) until recovery

## Strategy Risk Allocation
- **Pillar A (Micro)**: 22% portfolio vol (10-12% per sleeve)
- **Pillar B (Events)**: 27% portfolio vol (12-15% per sleeve)
- **Pillar C (Options)**: 14% portfolio vol (6-8% per sleeve)
- **Pillar D (Tilts)**: 17% portfolio vol (8-10% per sleeve)

## Real-Time Monitoring
- **VaR**: 95% 1-day ≤ 2% NAV
- **Correlation**: Cross-strategy ≤ 0.3
- **Liquidity**: Min 20-day ADV for all positions
- **Greeks**: Daily vega ≤ 0.5% NAV per $1 VIX move

## Regime-Based Adjustments
- **VIX > 30**: Reduce gross by 25%
- **Market Gap > 2%**: Halt new positions for 30min
- **Correlation Spike**: Reduce when avg pairwise > 0.5

## Emergency Procedures
- **Kill Switch**: Flatten all positions within 15 minutes
- **Data Loss**: Halt trading until feeds restored
- **Model Failure**: Revert to baseline linear models
- **Broker Issues**: Activate backup execution venue

---
*Updated: August 2025 | Next Review: November 2025*
