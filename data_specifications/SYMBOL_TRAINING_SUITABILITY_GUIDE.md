# SYMBOL TRAINING SUITABILITY GUIDE

**Generated:** August 11, 2025  
**Purpose:** Guide ML model training based on data quality per trading session  
**Data File:** `symbol_training_suitability_matrix.csv`

## 📊 OVERVIEW

This guide explains how to use the Symbol Training Suitability Matrix to determine which symbols and trading sessions are suitable for machine learning model training based on data coverage quality.

## 🎯 TRAINING THRESHOLD

**95% Coverage = TRAINABLE**
- Symbols with ≥95% data coverage are marked as **TRAINABLE**
- Symbols with <95% data coverage are marked as **UNTRAINABLE**

## 📋 DATA STRUCTURE

The CSV file contains the following columns:

| Column | Description |
|--------|--------------|
| `Symbol` | Stock/ETF ticker symbol |
| `Regular_Pct` | Coverage % for regular hours (9:30 AM - 4:00 PM ET) |
| `Regular_Status` | TRAINABLE/UNTRAINABLE for regular hours |
| `PreMkt_Pct` | Coverage % for pre-market (4:00 AM - 9:30 AM ET) |
| `PreMkt_Status` | TRAINABLE/UNTRAINABLE for pre-market |
| `After_Pct` | Coverage % for after-hours (4:00 PM - 8:00 PM ET) |
| `After_Status` | TRAINABLE/UNTRAINABLE for after-hours |
| `Overnight_Pct` | Coverage % for overnight (8:00 PM - 4:00 AM ET) |
| `Overnight_Status` | TRAINABLE/UNTRAINABLE for overnight |
| `ExtHours_Pct` | Coverage % for extended hours (combined) |
| `ExtHours_Status` | TRAINABLE/UNTRAINABLE for extended hours |
| `Total_Bars` | Total number of 1-minute data bars |

## 🏆 TRAINING RECOMMENDATIONS

### ✅ REGULAR HOURS TRAINING (HIGHEST PRIORITY)
**5 TRAINABLE Symbols (≥95% coverage):**
1. **AAPL** - 95.8% coverage, 399,806 bars
2. **TSLA** - 95.7% coverage, 438,824 bars  
3. **SPY** - 95.6% coverage, 415,656 bars
4. **AMZN** - 95.5% coverage, 394,195 bars
5. **NVDA** - 95.3% coverage, 432,768 bars

### ❌ EXTENDED HOURS TRAINING (NOT RECOMMENDED)
**0 TRAINABLE Symbols** - All symbols have <95% coverage for:
- Pre-market sessions
- After-hours sessions  
- Overnight sessions
- Combined extended hours

## 🚀 IMPLEMENTATION GUIDE

### For Strategy Development:
```python
import pandas as pd

# Load the training suitability matrix
df = pd.read_csv('symbol_training_suitability_matrix.csv')

# Get symbols suitable for regular hours training
trainable_regular = df[df['Regular_Status'] == 'TRAINABLE']['Symbol'].tolist()
print(f"Trainable symbols for regular hours: {trainable_regular}")

# Filter by minimum data volume (e.g., >300K bars)
high_volume_trainable = df[
    (df['Regular_Status'] == 'TRAINABLE') & 
    (df['Total_Bars'] > 300000)
]['Symbol'].tolist()
```

### For Model Training:
```python
# Focus training on the 5 trainable symbols
TRAINABLE_SYMBOLS = ['AAPL', 'TSLA', 'SPY', 'AMZN', 'NVDA']

# Only use regular hours data (9:30 AM - 4:00 PM ET)
TRAINING_SESSIONS = ['regular_hours']

# Avoid extended hours data due to poor coverage
AVOID_SESSIONS = ['pre_market', 'after_hours', 'overnight', 'extended_hours']
```

## 📈 STRATEGIC INSIGHTS

### **Why Only 5 Symbols Are Trainable:**
- **High-quality threshold:** 95% coverage ensures robust training data
- **Data integrity:** Gaps in data can lead to poor model performance
- **Focus over breadth:** Better to train well on 5 symbols than poorly on 99

### **Regular Hours Advantage:**
- **Highest liquidity:** Most trading activity occurs during regular hours
- **Best data quality:** Market makers and institutions most active
- **Predictable patterns:** More consistent trading behavior

### **Extended Hours Limitations:**
- **Low liquidity:** Fewer participants, wider spreads
- **Irregular patterns:** Less predictable price movements  
- **Data gaps:** Many symbols have minimal extended hours activity

## 🎯 NEXT STEPS

1. **Start with the Big 5:** Focus initial model development on AAPL, TSLA, SPY, AMZN, NVDA
2. **Regular hours only:** Use 9:30 AM - 4:00 PM ET data exclusively
3. **Validate thoroughly:** Use out-of-sample testing on these high-quality datasets
4. **Scale gradually:** Once models perform well on these 5, consider expanding

## 🔍 DATA QUALITY NOTES

- **Pre-market percentages >100%:** This indicates more data than expected market hours, likely due to early trading or data collection overlaps
- **Total bars vary significantly:** Reflects different listing dates and trading activity levels
- **Coverage percentages:** Based on expected trading minutes during each session period

This matrix ensures your ML models are trained on the highest quality data available, maximizing the probability of developing profitable trading strategies.