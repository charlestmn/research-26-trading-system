#!/usr/bin/env python3
"""
R26 Data Pipeline - Alpaca-First Implementation
Built for AWS deployment with 2-year 1-minute historical data capability
"""

import requests
import pandas as pd
import json
import time
import os
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlpacaCollector:
    """Alpaca API collector for institutional-grade 1-minute historical data"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('ALPACA_API_KEY')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY')
        self.base_url = base_url or os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret_key,
            'User-Agent': 'R26-DataPipeline/1.0'
        })
        
        # Rate limiting: 200 requests per minute
        self.rate_limit_delay = 0.3  # 300ms between requests
        self.last_request_time = 0
        
        logger.info("Alpaca collector initialized")
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def get_historical_bars(self, symbol: str, timeframe: str = "1Min", 
                           start: datetime = None, end: datetime = None,
                           lookback_days: int = 730) -> Optional[pd.DataFrame]:
        """Fetch 2-year 1-minute historical bars from Alpaca API"""
        try:
            # Set default date range for 2-year lookback
            if end is None:
                end = datetime.now(pytz.UTC)
            if start is None:
                start = end - timedelta(days=lookback_days)
            
            # Format dates for API
            start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            url = f"{self.base_url}/v2/stocks/{symbol}/bars"
            params = {
                'timeframe': timeframe,
                'start': start_str,
                'end': end_str,
                'limit': 10000,  # Maximum per request
                'adjustment': 'raw',
                'feed': 'iex'  # Use IEX feed for reliability
            }
            
            all_data = []
            page_token = None
            
            while True:
                self._rate_limit()
                
                if page_token:
                    params['page_token'] = page_token
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                if 'bars' not in data or not data['bars']:
                    break
                
                # Process bars
                for bar in data['bars']:
                    all_data.append({
                        'Datetime': pd.to_datetime(bar['t']),
                        'Open': float(bar['o']),
                        'High': float(bar['h']),
                        'Low': float(bar['l']),
                        'Close': float(bar['c']),
                        'Volume': int(bar['v'])
                    })
                
                # Check for next page
                page_token = data.get('next_page_token')
                if not page_token:
                    break
                
                logger.info(f"Collected {len(all_data)} bars so far for {symbol}")
            
            if not all_data:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(all_data)
            df.set_index('Datetime', inplace=True)
            df.sort_index(inplace=True)
            
            # Remove duplicates
            df = df[~df.index.duplicated(keep='first')]
            
            logger.info(f"Successfully collected {len(df)} bars for {symbol} from Alpaca")
            return df
            
        except Exception as e:
            logger.error(f"Alpaca API error for {symbol}: {e}")
            return None
    
    def get_multiple_symbols_historical(self, symbols: List[str], timeframe: str = "1Min",
                                      lookback_days: int = 730, max_workers: int = 3) -> Dict[str, pd.DataFrame]:
        """Collect 2-year historical data for multiple symbols with rate limiting"""
        results = {}
        
        # Use fewer workers to respect rate limits
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.get_historical_bars, symbol, timeframe, 
                              lookback_days=lookback_days): symbol 
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None and not data.empty:
                        results[symbol] = data
                        logger.info(f"Successfully collected {len(data)} bars for {symbol}")
                    else:
                        logger.warning(f"No data collected for {symbol}")
                except Exception as e:
                    logger.error(f"Error collecting {symbol}: {e}")
        
        return results

class S3DataStorageManager:
    """AWS S3-based data storage manager for cloud-first architecture"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv('R26_S3_BUCKET', 'r26-trading-data')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3')
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"S3 client initialization failed: {e}")
            raise
    
    def save_data_to_s3(self, data: pd.DataFrame, symbol: str, interval: str, 
                       source: str = "alpaca") -> str:
        """Save data directly to S3 in Parquet format"""
        try:
            # Generate S3 key with partitioning
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"historical_data/symbol={symbol}/interval={interval}/source={source}/{symbol}_{interval}_{source}_{timestamp}.parquet"
            
            # Convert DataFrame to Parquet bytes
            parquet_buffer = data.to_parquet(compression='snappy')
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=parquet_buffer,
                ContentType='application/octet-stream'
            )
            
            logger.info(f"Uploaded {len(data)} rows to S3: s3://{self.bucket_name}/{s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"Error saving data to S3 for {symbol}: {e}")
            return None
    
    def load_data_from_s3(self, s3_key: str) -> Optional[pd.DataFrame]:
        """Load data from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            df = pd.read_parquet(response['Body'])
            logger.info(f"Loaded {len(df)} rows from S3: {s3_key}")
            return df
        except Exception as e:
            logger.error(f"Error loading data from S3: {e}")
            return None

class R26AlpacaDataPipeline:
    """R26 Data Pipeline optimized for Alpaca 2-year 1-minute data collection"""
    
    def __init__(self, s3_bucket: str = None):
        self.alpaca_collector = AlpacaCollector()
        self.storage = S3DataStorageManager(s3_bucket)
        
        logger.info("R26 Alpaca Data Pipeline initialized")
    
    def collect_pillar_a_universe(self) -> Dict[str, pd.DataFrame]:
        """Collect 2-year 1-minute data for Pillar A universe (S&P 500 + top 1000 by ADV)"""
        
        # Pillar A universe symbols (sample - expand as needed)
        pillar_a_symbols = [
            # S&P 500 core holdings
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B',
            'UNH', 'JNJ', 'V', 'PG', 'JPM', 'HD', 'CVX', 'MA', 'PFE', 'ABBV',
            'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'WMT', 'DIS', 'ABT', 'DHR',
            'VZ', 'ADBE', 'CMCSA', 'NKE', 'TXN', 'NEE', 'RTX', 'QCOM', 'PM', 'T',
            
            # High ADV names for micro edges
            'SPY', 'QQQ', 'IWM', 'EEM', 'GLD', 'SLV', 'TLT', 'HYG', 'LQD', 'XLF',
            'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLRE', 'XLB', 'XME',
            
            # Volatility instruments
            'TQQQ', 'SQQQ', 'SPXL', 'SPXS', 'TNA', 'TZA', 'FAS', 'FAZ', 'TECL', 'TECS'
        ]
        
        logger.info(f"Starting Pillar A universe collection: {len(pillar_a_symbols)} symbols")
        
        # Collect data in batches to manage API limits
        batch_size = 10
        all_results = {}
        
        for i in range(0, len(pillar_a_symbols), batch_size):
            batch = pillar_a_symbols[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
            
            batch_results = self.alpaca_collector.get_multiple_symbols_historical(
                batch, "1Min", lookback_days=730, max_workers=3
            )
            
            # Save each symbol's data to S3
            for symbol, data in batch_results.items():
                if data is not None and not data.empty:
                    s3_key = self.storage.save_data_to_s3(data, symbol, "1min", "alpaca")
                    if s3_key:
                        all_results[symbol] = data
                        logger.info(f"✅ {symbol}: {len(data)} bars saved to S3")
                    else:
                        logger.error(f"❌ {symbol}: Failed to save to S3")
            
            # Rate limiting between batches
            time.sleep(5)
        
        logger.info(f"Pillar A collection complete: {len(all_results)} symbols successfully processed")
        return all_results
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict:
        """Validate 1-minute data quality"""
        quality_score = 100
        issues = []
        
        if data.empty:
            return {'score': 0, 'issues': ['Empty dataset']}
        
        # Check for required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            quality_score -= 20
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for null values
        null_count = data.isnull().sum().sum()
        if null_count > 0:
            null_percentage = (null_count / (len(data) * len(data.columns))) * 100
            quality_score -= min(30, null_percentage)
            issues.append(f"Null values: {null_count} ({null_percentage:.1f}%)")
        
        # Check OHLC logic
        if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
            invalid_ohlc = (
                (data['High'] < data[['Open', 'Close', 'Low']].max(axis=1)) |
                (data['Low'] > data[['Open', 'Close', 'High']].min(axis=1))
            ).sum()
            
            if invalid_ohlc > 0:
                invalid_percentage = (invalid_ohlc / len(data)) * 100
                quality_score -= min(25, invalid_percentage)
                issues.append(f"Invalid OHLC logic: {invalid_ohlc} rows ({invalid_percentage:.1f}%)")
        
        # Check for data gaps in 1-minute data
        if len(data) > 1:
            time_diffs = data.index.to_series().diff()
            expected_diff = pd.Timedelta(minutes=1)
            gaps = (time_diffs > expected_diff * 5).sum()  # Allow up to 5-minute gaps
            if gaps > 0:
                quality_score -= min(15, gaps)
                issues.append(f"Data gaps detected: {gaps} instances")
        
        return {
            'score': max(0, quality_score),
            'issues': issues,
            'row_count': len(data),
            'null_count': null_count
        }
    
    def get_collection_summary(self) -> Dict:
        """Get summary of data collection status"""
        try:
            # List objects in S3 bucket
            response = self.storage.s3_client.list_objects_v2(
                Bucket=self.storage.bucket_name,
                Prefix='historical_data/'
            )
            
            summary = {
                'total_files': 0,
                'symbols': set(),
                'total_size_mb': 0,
                'last_updated': None
            }
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    summary['total_files'] += 1
                    summary['total_size_mb'] += obj['Size'] / (1024 * 1024)
                    
                    # Extract symbol from key
                    key_parts = obj['Key'].split('/')
                    for part in key_parts:
                        if part.startswith('symbol='):
                            summary['symbols'].add(part.split('=')[1])
                    
                    # Track latest modification
                    if summary['last_updated'] is None or obj['LastModified'] > summary['last_updated']:
                        summary['last_updated'] = obj['LastModified']
            
            summary['unique_symbols'] = len(summary['symbols'])
            summary['symbols'] = list(summary['symbols'])
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting collection summary: {e}")
            return {'error': str(e)}

def main():
    """Test the R26 Alpaca Data Pipeline"""
    print("R26 Alpaca Data Pipeline - 2-Year 1-Minute Historical Collection")
    print("=" * 70)
    
    try:
        # Initialize pipeline
        pipeline = R26AlpacaDataPipeline()
        
        # Test single symbol collection
        print("\n1. Testing single symbol collection (TQQQ)...")
        tqqq_data = pipeline.alpaca_collector.get_historical_bars("TQQQ", "1Min", lookback_days=5)
        
        if tqqq_data is not None:
            quality = pipeline.validate_data_quality(tqqq_data)
            print(f"✅ TQQQ: {len(tqqq_data)} bars collected (Quality: {quality['score']})")
            print(f"   Date range: {tqqq_data.index.min()} to {tqqq_data.index.max()}")
            
            # Save to S3
            s3_key = pipeline.storage.save_data_to_s3(tqqq_data, "TQQQ", "1min", "alpaca")
            if s3_key:
                print(f"✅ Saved to S3: {s3_key}")
        else:
            print("❌ Failed to collect TQQQ data")
        
        # Test small batch collection
        print("\n2. Testing small batch collection...")
        test_symbols = ["SPY", "QQQ", "IWM"]
        batch_results = pipeline.alpaca_collector.get_multiple_symbols_historical(
            test_symbols, "1Min", lookback_days=2, max_workers=2
        )
        
        print(f"✅ Batch collection results:")
        for symbol, data in batch_results.items():
            if data is not None:
                quality = pipeline.validate_data_quality(data)
                print(f"   {symbol}: {len(data)} bars (Quality: {quality['score']})")
                
                # Save to S3
                s3_key = pipeline.storage.save_data_to_s3(data, symbol, "1min", "alpaca")
                if s3_key:
                    print(f"   ✅ Saved to S3")
        
        # Get collection summary
        print("\n3. Collection Summary:")
        summary = pipeline.get_collection_summary()
        if 'error' not in summary:
            print(f"   Total files: {summary['total_files']}")
            print(f"   Unique symbols: {summary['unique_symbols']}")
            print(f"   Total size: {summary['total_size_mb']:.2f} MB")
            print(f"   Symbols: {', '.join(summary['symbols'][:10])}{'...' if len(summary['symbols']) > 10 else ''}")
        
        print("\n" + "=" * 70)
        print("✅ R26 Alpaca Data Pipeline test completed successfully")
        print("Ready for full Pillar A universe collection (730 days, 1-minute bars)")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        logger.error(f"Pipeline test error: {e}")

if __name__ == "__main__":
    main()
