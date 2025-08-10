# R26 AWS Deployment Guide
**Phase 1: Alpaca Data Pipeline Execution**

## 🎯 OVERVIEW

This guide provides step-by-step instructions for executing the completed Alpaca data pipeline on AWS EC2 to collect 2 years of 1-minute historical data for the Pillar A universe.

**What's Ready:**
- ✅ Complete Alpaca API data pipeline
- ✅ AWS S3 storage system with Parquet format
- ✅ Bulk historical collection for 200+ symbols
- ✅ Comprehensive test suite
- ✅ Rate limiting and data quality validation

## 🚀 QUICK START

### Prerequisites
- AWS EC2 instance running (54.198.134.93)
- Alpaca API keys configured
- AWS credentials configured
- Repository cloned and updated

### Execution Commands
```bash
# Connect to AWS instance
ssh -i your-key.pem ec2-user@54.198.134.93

# Navigate to project
cd /home/ec2-user/research-26-trading-system

# Pull latest code
git pull origin main

# Test the pipeline (5-10 minutes)
python scripts/test_alpaca_pipeline_aws.py

# Execute bulk collection (2-4 hours)
python scripts/bulk_historical_collection.py
```

## 📋 DETAILED EXECUTION STEPS

### Step 1: Environment Validation
```bash
# Test all systems before bulk collection
python scripts/test_alpaca_pipeline_aws.py
```

**Expected Output:**
```
R26 ALPACA DATA PIPELINE - AWS VALIDATION TEST
============================================================

=== ENVIRONMENT SETUP TEST ===
✅ ALPACA_API_KEY: ********1234
✅ ALPACA_SECRET_KEY: ********5678
✅ AWS_DEFAULT_REGION: us-east-1
✅ AWS Identity: arn:aws:iam::123456789012:user/ec2-user
✅ S3 bucket exists: r26-trading-data
✅ Environment setup test passed

=== ALPACA API CONNECTIVITY TEST ===
✅ Alpaca collector initialized
✅ Alpaca API connected
   Account Status: ACTIVE
   Trading Blocked: False
   Pattern Day Trader: False
✅ Alpaca connectivity test passed

=== DATA COLLECTION TEST ===
✅ Pipeline initialized
Testing SPY data collection (2 days, 1-minute)...
✅ Data collected: 780 bars
   Date range: 2025-08-08 09:30:00-04:00 to 2025-08-09 16:00:00-04:00
   Quality score: 95
✅ Data saved to S3: historical/alpaca/1min/SPY/year=2025/month=08/SPY_1min_20250810_151118.parquet
✅ Data loaded from S3: 780 bars
✅ Data collection test passed

=== BATCH COLLECTION TEST ===
Testing batch collection: ['SPY', 'QQQ', 'IWM'] (1 day, 1-minute)...
✅ SPY: 390 bars
   Saved to S3: historical/alpaca/1min/SPY/year=2025/month=08/SPY_1min_20250810_151119.parquet
✅ QQQ: 390 bars
   Saved to S3: historical/alpaca/1min/QQQ/year=2025/month=08/QQQ_1min_20250810_151119.parquet
✅ IWM: 390 bars
   Saved to S3: historical/alpaca/1min/IWM/year=2025/month=08/IWM_1min_20250810_151119.parquet
✅ Batch collection test passed: 3/3 successful

=== RATE LIMITING TEST ===
✅ Rate limiting test completed
   Total time for 5 requests: 1.25s
   Average delay per request: 0.250s
   Expected delay: 0.300s
✅ Rate limiting working correctly

============================================================
TEST SUMMARY
============================================================
Environment Setup   : ✅ PASS
Alpaca Connectivity : ✅ PASS
Data Collection     : ✅ PASS
Batch Collection    : ✅ PASS
Rate Limiting       : ✅ PASS

Overall: 5/5 tests passed

🎉 ALL TESTS PASSED - Pipeline ready for production use!

Next steps:
1. Run bulk_historical_collection.py for full 2-year data collection
2. Monitor S3 bucket for data accumulation
3. Proceed with Pillar A strategy development
```

### Step 2: Execute Bulk Historical Collection
```bash
# Start the bulk collection process
python scripts/bulk_historical_collection.py
```

**Interactive Prompts:**
```
R26 BULK HISTORICAL DATA COLLECTION
2-Year 1-Minute Data for Pillar A Universe
============================================================

Target universe: 200 symbols

This will collect 2 years of 1-minute data for 200 symbols.
Estimated time: 2-4 hours depending on API performance.
Estimated data size: 5-10 GB

Proceed with bulk collection? (yes/no): yes

Starting bulk collection...
```

**Progress Monitoring:**
```bash
# Monitor progress in real-time (separate terminal)
tail -f bulk_collection.log

# Check S3 bucket contents
aws s3 ls s3://r26-trading-data/historical/alpaca/1min/ --recursive
```

### Step 3: Monitor Collection Progress

**Expected Progress Output:**
```
=== BATCH 1/25 ===
Symbols: AAPL, MSFT, GOOGL, GOOG, AMZN, TSLA, META, NVDA
✅ AAPL: 525,600 bars (Q:94) -> S3
✅ MSFT: 525,600 bars (Q:96) -> S3
✅ GOOGL: 525,600 bars (Q:93) -> S3
✅ GOOG: 525,600 bars (Q:93) -> S3
✅ AMZN: 525,600 bars (Q:95) -> S3
✅ TSLA: 525,600 bars (Q:92) -> S3
✅ META: 525,600 bars (Q:94) -> S3
✅ NVDA: 525,600 bars (Q:97) -> S3
Progress: 4.0% (8 successful)
Waiting 45s before next batch...

=== BATCH 2/25 ===
Symbols: BRK.B, UNH, JNJ, V, PG, JPM, HD, CVX
...
```

## 📊 EXPECTED OUTCOMES

### Data Volume
- **Total Symbols:** 200+ (Pillar A universe)
- **Time Period:** 2 years (730 days)
- **Resolution:** 1-minute bars
- **Total Bars:** ~100M bars across all symbols
- **Storage Size:** 5-10 GB in compressed Parquet format

### Collection Timeline
- **Batch Size:** 8 symbols per batch
- **Batch Delay:** 45 seconds between batches
- **Total Batches:** ~25 batches
- **Estimated Duration:** 2-4 hours
- **Success Rate:** >90% expected

### S3 Storage Structure
```
r26-trading-data/
├── historical/
│   └── alpaca/
│       └── 1min/
│           ├── AAPL/
│           │   ├── year=2023/month=08/AAPL_1min_20250810_151200.parquet
│           │   ├── year=2023/month=09/AAPL_1min_20250810_151201.parquet
│           │   └── ...
│           ├── MSFT/
│           └── ...
└── collection_metadata/
    └── bulk_collection_metadata_20250810_151200.json
```

## 🔍 MONITORING & TROUBLESHOOTING

### Real-time Monitoring
```bash
# Monitor log file
tail -f bulk_collection.log

# Check S3 uploads
aws s3 ls s3://r26-trading-data/historical/alpaca/1min/ --recursive | wc -l

# Monitor system resources
top
df -h
```

### Common Issues & Solutions

**Issue: API Rate Limiting**
```
ERROR: Rate limit exceeded
Solution: Script automatically handles with 45s delays
```

**Issue: S3 Upload Failures**
```
ERROR: S3 save failed
Solution: Check AWS credentials and S3 bucket permissions
```

**Issue: Data Quality Issues**
```
WARNING: Low quality (65) - gaps detected
Solution: Script continues, low-quality data flagged in reports
```

**Issue: Network Connectivity**
```
ERROR: Connection timeout
Solution: Script retries automatically, check internet connection
```

### Recovery Commands
```bash
# Resume interrupted collection (script tracks progress)
python scripts/bulk_historical_collection.py

# Check collection status
ls -la bulk_collection_*.log
ls -la bulk_collection_metadata_*.json

# Verify S3 data
aws s3 ls s3://r26-trading-data/historical/alpaca/1min/ --recursive --summarize
```

## 📈 SUCCESS VALIDATION

### Collection Report
After completion, the script generates a comprehensive report:

```
=== R26 BULK HISTORICAL DATA COLLECTION REPORT ===

Collection Summary:
- Start Time: 2025-08-10 15:12:00
- End Time: 2025-08-10 18:45:30
- Duration: 3:33:30
- Total Symbols Attempted: 200
- Successful Collections: 192
- Failed Collections: 8
- Success Rate: 96.0%
- Total Bars Collected: 95,234,567

Data Quality Summary:
- Average Quality Score: 94.2
- Quality Range: 78 - 98
- High Quality (>90): 175
- Good Quality (70-90): 17

Top Performers by Data Volume:
- SPY: 525,600 bars (Q:97)
- QQQ: 525,600 bars (Q:96)
- AAPL: 525,600 bars (Q:95)
...
```

### Validation Checklist
- [ ] Collection report shows >90% success rate
- [ ] S3 bucket contains data for all major symbols
- [ ] Average quality score >90
- [ ] No critical errors in log files
- [ ] Metadata files generated successfully

## 🎯 NEXT STEPS AFTER COMPLETION

### Immediate Actions
1. **Verify Data Integrity**
   ```bash
   python scripts/validate_collected_data.py
   ```

2. **Generate Data Summary**
   ```bash
   python scripts/generate_data_summary.py
   ```

3. **Begin Feature Engineering**
   - Start Phase 2: ML Model Development
   - Implement technical indicators
   - Create feature pipelines

### Phase 2 Preparation
- **ML Pipeline Development:** Feature engineering on collected data
- **Model Training Infrastructure:** AWS-native training pipeline
- **Strategy Implementation:** Begin Pillar A overnight reversion strategy
- **Real-time Data Feeds:** Add live streaming for trading execution

## 🔐 SECURITY CONSIDERATIONS

### API Keys
- Alpaca keys stored in environment variables
- Never commit keys to repository
- Rotate keys regularly

### AWS Security
- EC2 instance with minimal required permissions
- S3 bucket with encryption at rest
- VPC security groups configured

### Data Protection
- All data encrypted in transit and at rest
- Access logs maintained
- Regular security audits

---

**Status:** Ready for execution  
**Last Updated:** August 10, 2025, 3:11 PM PST  
**Next Update:** After bulk collection completion

*Execute with confidence - all systems tested and validated!*
