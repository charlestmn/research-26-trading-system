#!/usr/bin/env python3
"""
Test AWS Data Pipeline for R26 Trading System
Tests Yahoo Finance data collection on AWS EC2 instance
"""

import sys
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json

def test_yfinance_installation():
    """Test if yfinance is properly installed and working"""
    print("=" * 60)
    print("TESTING YFINANCE INSTALLATION")
    print("=" * 60)
    
    try:
        import yfinance as yf
        print(f"✅ yfinance imported successfully")
        print(f"✅ yfinance version: {yf.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import yfinance: {e}")
        return False

def test_basic_data_collection():
    """Test basic TQQQ data collection"""
    print("\n" + "=" * 60)
    print("TESTING BASIC TQQQ DATA COLLECTION")
    print("=" * 60)
    
    try:
        # Test basic daily data
        ticker = yf.Ticker("TQQQ")
        print(f"✅ Created TQQQ ticker object")
        
        # Get 5 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5)
        
        data = ticker.history(start=start_date, end=end_date)
        print(f"✅ Retrieved {len(data)} days of TQQQ data")
        print(f"✅ Data columns: {list(data.columns)}")
        print(f"✅ Date range: {data.index[0]} to {data.index[-1]}")
        
        # Display sample data
        print("\nSample data (last 3 rows):")
        print(data.tail(3))
        
        return True, data
        
    except Exception as e:
        print(f"❌ Failed to collect basic data: {e}")
        return False, None

def test_intraday_data_collection():
    """Test intraday data collection capabilities"""
    print("\n" + "=" * 60)
    print("TESTING INTRADAY DATA COLLECTION")
    print("=" * 60)
    
    try:
        ticker = yf.Ticker("TQQQ")
        
        # Test 1-minute data for last 7 days
        data_1m = ticker.history(period="7d", interval="1m")
        print(f"✅ Retrieved {len(data_1m)} 1-minute bars")
        
        # Test 5-minute data
        data_5m = ticker.history(period="7d", interval="5m")
        print(f"✅ Retrieved {len(data_5m)} 5-minute bars")
        
        # Test 15-minute data
        data_15m = ticker.history(period="7d", interval="15m")
        print(f"✅ Retrieved {len(data_15m)} 15-minute bars")
        
        return True, {
            '1m': data_1m,
            '5m': data_5m,
            '15m': data_15m
        }
        
    except Exception as e:
        print(f"❌ Failed to collect intraday data: {e}")
        return False, None

def test_data_quality():
    """Test data quality and completeness"""
    print("\n" + "=" * 60)
    print("TESTING DATA QUALITY")
    print("=" * 60)
    
    try:
        ticker = yf.Ticker("TQQQ")
        data = ticker.history(period="5d", interval="1d")
        
        # Check for missing values
        missing_values = data.isnull().sum()
        print(f"✅ Missing values check:")
        for col, missing in missing_values.items():
            print(f"   {col}: {missing} missing values")
        
        # Check data types
        print(f"✅ Data types:")
        for col, dtype in data.dtypes.items():
            print(f"   {col}: {dtype}")
        
        # Check price consistency
        if len(data) > 0:
            latest_close = data['Close'].iloc[-1]
            print(f"✅ Latest TQQQ close price: ${latest_close:.2f}")
            
            # Basic sanity check - TQQQ should be > $10 and < $200
            if 10 < latest_close < 200:
                print(f"✅ Price sanity check passed")
            else:
                print(f"⚠️  Price seems unusual: ${latest_close:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

def test_data_storage():
    """Test data storage capabilities"""
    print("\n" + "=" * 60)
    print("TESTING DATA STORAGE")
    print("=" * 60)
    
    try:
        # Create test data directory
        data_dir = "/tmp/r26_test_data"
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Created data directory: {data_dir}")
        
        # Get sample data
        ticker = yf.Ticker("TQQQ")
        data = ticker.history(period="5d", interval="1d")
        
        # Test CSV storage
        csv_path = os.path.join(data_dir, "tqqq_test.csv")
        data.to_csv(csv_path)
        print(f"✅ Saved data to CSV: {csv_path}")
        
        # Test reading back
        loaded_data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        print(f"✅ Successfully loaded data back from CSV")
        print(f"✅ Loaded {len(loaded_data)} rows")
        
        # Test JSON metadata storage
        metadata = {
            'symbol': 'TQQQ',
            'data_points': len(data),
            'start_date': str(data.index[0]),
            'end_date': str(data.index[-1]),
            'collection_time': str(datetime.now()),
            'columns': list(data.columns)
        }
        
        json_path = os.path.join(data_dir, "tqqq_metadata.json")
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata to JSON: {json_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data storage test failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "=" * 60)
    print("GENERATING TEST REPORT")
    print("=" * 60)
    
    report = {
        'test_timestamp': str(datetime.now()),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
        },
        'test_results': {}
    }
    
    # Run all tests
    tests = [
        ('yfinance_installation', test_yfinance_installation),
        ('basic_data_collection', lambda: test_basic_data_collection()[0]),
        ('intraday_data_collection', lambda: test_intraday_data_collection()[0]),
        ('data_quality', test_data_quality),
        ('data_storage', test_data_storage)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            report['test_results'][test_name] = 'PASSED' if result else 'FAILED'
            if not result:
                all_passed = False
        except Exception as e:
            report['test_results'][test_name] = f'ERROR: {str(e)}'
            all_passed = False
    
    # Save report
    report_path = "/tmp/r26_data_pipeline_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Test report saved to: {report_path}")
    print(f"Overall result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return report

def main():
    """Main test execution"""
    print("R26 AWS Data Pipeline Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Run individual tests
    test_yfinance_installation()
    test_basic_data_collection()
    test_intraday_data_collection()
    test_data_quality()
    test_data_storage()
    
    # Generate final report
    report = generate_test_report()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, result in report['test_results'].items():
        status = "✅" if result == "PASSED" else "❌"
        print(f"{status} {test_name}: {result}")

if __name__ == "__main__":
    main()
