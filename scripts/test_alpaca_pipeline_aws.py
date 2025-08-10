#!/usr/bin/env python3
"""
R26 Alpaca Data Pipeline AWS Test Script
Validates Alpaca API connectivity and S3 integration on AWS EC2 instance
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test AWS and environment setup"""
    print("\n=== ENVIRONMENT SETUP TEST ===")
    
    # Check required environment variables
    required_vars = [
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY',
        'AWS_DEFAULT_REGION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * 8}{os.getenv(var)[-4:]}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    # Test AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        return False
    
    # Test S3 access
    try:
        s3 = boto3.client('s3')
        bucket_name = os.getenv('R26_S3_BUCKET', 'r26-trading-data')
        
        # Try to list bucket (will create if doesn't exist)
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 bucket exists: {bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"⚠️ S3 bucket doesn't exist: {bucket_name}")
                print("   Creating bucket...")
                try:
                    s3.create_bucket(Bucket=bucket_name)
                    print(f"✅ S3 bucket created: {bucket_name}")
                except Exception as create_error:
                    print(f"❌ Failed to create S3 bucket: {create_error}")
                    return False
            else:
                print(f"❌ S3 access error: {e}")
                return False
    except Exception as e:
        print(f"❌ S3 setup test failed: {e}")
        return False
    
    print("✅ Environment setup test passed")
    return True

def test_alpaca_connectivity():
    """Test Alpaca API connectivity"""
    print("\n=== ALPACA API CONNECTIVITY TEST ===")
    
    try:
        from r26_data_pipeline_alpaca import AlpacaCollector
        
        # Initialize collector
        collector = AlpacaCollector()
        print("✅ Alpaca collector initialized")
        
        # Test API connectivity with account info
        url = f"{collector.base_url}/v2/account"
        response = collector.session.get(url, timeout=10)
        
        if response.status_code == 200:
            account_data = response.json()
            print(f"✅ Alpaca API connected")
            print(f"   Account Status: {account_data.get('status', 'Unknown')}")
            print(f"   Trading Blocked: {account_data.get('trading_blocked', 'Unknown')}")
            print(f"   Pattern Day Trader: {account_data.get('pattern_day_trader', 'Unknown')}")
        else:
            print(f"❌ Alpaca API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alpaca connectivity test failed: {e}")
        return False
    
    print("✅ Alpaca connectivity test passed")
    return True

def test_data_collection():
    """Test actual data collection"""
    print("\n=== DATA COLLECTION TEST ===")
    
    try:
        from r26_data_pipeline_alpaca import R26AlpacaDataPipeline
        
        # Initialize pipeline
        pipeline = R26AlpacaDataPipeline()
        print("✅ Pipeline initialized")
        
        # Test single symbol collection (short timeframe)
        test_symbol = "SPY"
        print(f"Testing {test_symbol} data collection (2 days, 1-minute)...")
        
        data = pipeline.alpaca_collector.get_historical_bars(
            test_symbol, "1Min", lookback_days=2
        )
        
        if data is not None and not data.empty:
            print(f"✅ Data collected: {len(data)} bars")
            print(f"   Date range: {data.index.min()} to {data.index.max()}")
            print(f"   Sample data:")
            print(data.head(3).to_string())
            
            # Test data quality validation
            quality = pipeline.validate_data_quality(data)
            print(f"   Quality score: {quality['score']}")
            if quality['issues']:
                print(f"   Quality issues: {quality['issues']}")
            
            # Test S3 save
            print(f"Testing S3 save...")
            s3_key = pipeline.storage.save_data_to_s3(data, test_symbol, "1min", "alpaca")
            
            if s3_key:
                print(f"✅ Data saved to S3: {s3_key}")
                
                # Test S3 load
                print(f"Testing S3 load...")
                loaded_data = pipeline.storage.load_data_from_s3(s3_key)
                
                if loaded_data is not None and len(loaded_data) == len(data):
                    print(f"✅ Data loaded from S3: {len(loaded_data)} bars")
                else:
                    print(f"❌ S3 load failed or data mismatch")
                    return False
            else:
                print(f"❌ S3 save failed")
                return False
                
        else:
            print(f"❌ No data collected for {test_symbol}")
            return False
            
    except Exception as e:
        print(f"❌ Data collection test failed: {e}")
        logger.exception("Data collection test error")
        return False
    
    print("✅ Data collection test passed")
    return True

def test_batch_collection():
    """Test small batch collection"""
    print("\n=== BATCH COLLECTION TEST ===")
    
    try:
        from r26_data_pipeline_alpaca import R26AlpacaDataPipeline
        
        pipeline = R26AlpacaDataPipeline()
        
        # Test small batch
        test_symbols = ["SPY", "QQQ", "IWM"]
        print(f"Testing batch collection: {test_symbols} (1 day, 1-minute)...")
        
        batch_results = pipeline.alpaca_collector.get_multiple_symbols_historical(
            test_symbols, "1Min", lookback_days=1, max_workers=2
        )
        
        successful = 0
        for symbol, data in batch_results.items():
            if data is not None and not data.empty:
                print(f"✅ {symbol}: {len(data)} bars")
                
                # Save to S3
                s3_key = pipeline.storage.save_data_to_s3(data, symbol, "1min", "alpaca")
                if s3_key:
                    print(f"   Saved to S3: {s3_key}")
                    successful += 1
                else:
                    print(f"   ❌ S3 save failed")
            else:
                print(f"❌ {symbol}: No data")
        
        if successful == len(test_symbols):
            print(f"✅ Batch collection test passed: {successful}/{len(test_symbols)} successful")
            return True
        else:
            print(f"⚠️ Batch collection partial success: {successful}/{len(test_symbols)}")
            return successful > 0
            
    except Exception as e:
        print(f"❌ Batch collection test failed: {e}")
        logger.exception("Batch collection test error")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n=== RATE LIMITING TEST ===")
    
    try:
        from r26_data_pipeline_alpaca import AlpacaCollector
        import time
        
        collector = AlpacaCollector()
        
        # Test multiple rapid requests
        start_time = time.time()
        request_times = []
        
        for i in range(5):
            request_start = time.time()
            collector._rate_limit()
            request_times.append(time.time() - request_start)
        
        total_time = time.time() - start_time
        avg_delay = sum(request_times) / len(request_times)
        
        print(f"✅ Rate limiting test completed")
        print(f"   Total time for 5 requests: {total_time:.2f}s")
        print(f"   Average delay per request: {avg_delay:.3f}s")
        print(f"   Expected delay: {collector.rate_limit_delay:.3f}s")
        
        if avg_delay >= collector.rate_limit_delay * 0.8:  # Allow some tolerance
            print(f"✅ Rate limiting working correctly")
            return True
        else:
            print(f"⚠️ Rate limiting may not be working as expected")
            return False
            
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("R26 ALPACA DATA PIPELINE - AWS VALIDATION TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print(f"AWS Region: {os.getenv('AWS_DEFAULT_REGION', 'Not set')}")
    print(f"Alpaca Base URL: {os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')}")
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Alpaca Connectivity", test_alpaca_connectivity),
        ("Data Collection", test_data_collection),
        ("Batch Collection", test_batch_collection),
        ("Rate Limiting", test_rate_limiting)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            logger.exception(f"{test_name} test exception")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED - Pipeline ready for production use!")
        print("\nNext steps:")
        print("1. Run bulk_historical_collection.py for full 2-year data collection")
        print("2. Monitor S3 bucket for data accumulation")
        print("3. Proceed with Pillar A strategy development")
    else:
        print(f"\n⚠️ {len(tests) - passed} tests failed - Review errors before production use")
        print("\nTroubleshooting:")
        print("1. Check environment variables (AWS credentials, Alpaca keys)")
        print("2. Verify S3 bucket permissions")
        print("3. Test network connectivity to Alpaca API")
        print("4. Check AWS EC2 instance permissions")
    
    print(f"\nTest completed at: {datetime.now()}")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
