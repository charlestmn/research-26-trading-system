#!/usr/bin/env python3
"""
R26 Data Pipeline - Cloud-Native Multi-Source Data Collection System
Built for AWS deployment with Python 3.7 compatibility
"""

import requests
import pandas as pd
import json
import time
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityValidator:
    """Validates and scores data quality"""
    
    @staticmethod
    def validate_ohlcv(data: pd.DataFrame) -> Dict:
        """Validate OHLCV data and return quality metrics"""
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
        
        # Check OHLC logic (High >= Open,Close,Low and Low <= Open,Close,High)
        if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
            invalid_ohlc = (
                (data['High'] < data[['Open', 'Close', 'Low']].max(axis=1)) |
                (data['Low'] > data[['Open', 'Close', 'High']].min(axis=1))
            ).sum()
            
            if invalid_ohlc > 0:
                invalid_percentage = (invalid_ohlc / len(data)) * 100
                quality_score -= min(25, invalid_percentage)
                issues.append(f"Invalid OHLC logic: {invalid_ohlc} rows ({invalid_percentage:.1f}%)")
        
        # Check for zero/negative prices
        if 'Close' in data.columns:
            invalid_prices = (data['Close'] <= 0).sum()
            if invalid_prices > 0:
                quality_score -= 15
                issues.append(f"Invalid prices: {invalid_prices} rows")
        
        # Check for extreme price movements (>50% in one period)
        if 'Close' in data.columns and len(data) > 1:
            price_changes = data['Close'].pct_change().abs()
            extreme_moves = (price_changes > 0.5).sum()
            if extreme_moves > 0:
                quality_score -= 10
                issues.append(f"Extreme price movements: {extreme_moves} periods")
        
        return {
            'score': max(0, quality_score),
            'issues': issues,
            'row_count': len(data),
            'null_count': null_count
        }

class YahooFinanceCollector:
    """Direct Yahoo Finance API collector (no yfinance dependency)"""
    
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch data from Yahoo Finance API"""
        try:
            url = f"{self.base_url}/{symbol}"
            params = {
                'period1': self._get_period_start(period),
                'period2': int(time.time()),
                'interval': interval,
                'includePrePost': 'false',
                'events': 'div,splits'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or not data['chart']['result']:
                logger.warning(f"No data returned for {symbol}")
                return None
            
            result = data['chart']['result'][0]
            
            # Extract timestamps and OHLCV data
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'Datetime': pd.to_datetime(timestamps, unit='s'),
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })
            
            # Clean data
            df = df.dropna()
            df.set_index('Datetime', inplace=True)
            
            logger.info(f"Successfully collected {len(df)} rows for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    def _get_period_start(self, period: str) -> int:
        """Convert period string to Unix timestamp"""
        now = datetime.now()
        
        period_map = {
            '1d': now - timedelta(days=1),
            '5d': now - timedelta(days=5),
            '1mo': now - timedelta(days=30),
            '3mo': now - timedelta(days=90),
            '6mo': now - timedelta(days=180),
            '1y': now - timedelta(days=365),
            '2y': now - timedelta(days=730),
            '5y': now - timedelta(days=1825),
            '10y': now - timedelta(days=3650)
        }
        
        start_date = period_map.get(period, now - timedelta(days=30))
        return int(start_date.timestamp())

class AlphaVantageCollector:
    """Alpha Vantage API collector as backup data source"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
    
    def get_data(self, symbol: str, interval: str = "daily") -> Optional[pd.DataFrame]:
        """Fetch data from Alpha Vantage API"""
        try:
            function_map = {
                '1min': 'TIME_SERIES_INTRADAY',
                '5min': 'TIME_SERIES_INTRADAY',
                '15min': 'TIME_SERIES_INTRADAY',
                '30min': 'TIME_SERIES_INTRADAY',
                '60min': 'TIME_SERIES_INTRADAY',
                'daily': 'TIME_SERIES_DAILY'
            }
            
            function = function_map.get(interval, 'TIME_SERIES_DAILY')
            
            params = {
                'function': function,
                'symbol': symbol,
                'apikey': self.api_key,
                'outputsize': 'full'
            }
            
            if 'INTRADAY' in function:
                params['interval'] = interval
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Find the time series key
            time_series_key = None
            for key in data.keys():
                if 'Time Series' in key:
                    time_series_key = key
                    break
            
            if not time_series_key or time_series_key not in data:
                logger.warning(f"No time series data for {symbol}")
                return None
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            df_data = []
            for timestamp, values in time_series.items():
                df_data.append({
                    'Datetime': pd.to_datetime(timestamp),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('Datetime', inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"Successfully collected {len(df)} rows for {symbol} from Alpha Vantage")
            return df
            
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None

class DataStorageManager:
    """Manages data storage and retrieval"""
    
    def __init__(self, storage_dir: str = "r26_data"):
        self.storage_dir = storage_dir
        self.metadata_db = os.path.join(storage_dir, "metadata.db")
        
        # Create storage directory
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize metadata database
        self._init_metadata_db()
    
    def _init_metadata_db(self):
        """Initialize metadata database"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                interval TEXT NOT NULL,
                source TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                quality_issues TEXT,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, interval, source, start_date, end_date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_data(self, data: pd.DataFrame, symbol: str, interval: str, 
                  source: str, quality_metrics: Dict) -> str:
        """Save data to storage and update metadata"""
        
        # Generate file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{symbol}_{interval}_{source}_{timestamp}.csv"
        file_path = os.path.join(self.storage_dir, filename)
        
        # Save data
        data.to_csv(file_path)
        
        # Update metadata
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO data_metadata 
            (symbol, interval, source, start_date, end_date, row_count, 
             quality_score, quality_issues, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol, interval, source,
            data.index.min().isoformat(),
            data.index.max().isoformat(),
            len(data),
            quality_metrics['score'],
            json.dumps(quality_metrics['issues']),
            file_path
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {len(data)} rows to {file_path}")
        return file_path
    
    def get_latest_data(self, symbol: str, interval: str) -> Optional[pd.DataFrame]:
        """Get the latest data for a symbol and interval"""
        conn = sqlite3.connect(self.metadata_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, quality_score FROM data_metadata 
            WHERE symbol = ? AND interval = ?
            ORDER BY created_at DESC, quality_score DESC
            LIMIT 1
        ''', (symbol, interval))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            file_path, quality_score = result
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, index_col=0, parse_dates=True)
                logger.info(f"Loaded {len(df)} rows from {file_path} (quality: {quality_score})")
                return df
        
        return None

class R26DataPipeline:
    """Main R26 Data Pipeline orchestrator"""
    
    def __init__(self, storage_dir: str = "r26_data"):
        self.collectors = {
            'yahoo': YahooFinanceCollector(),
            'alphavantage': AlphaVantageCollector()
        }
        self.validator = DataQualityValidator()
        self.storage = DataStorageManager(storage_dir)
        
        logger.info("R26 Data Pipeline initialized")
    
    def collect_data(self, symbol: str, period: str = "1mo", interval: str = "1d", 
                    preferred_source: str = "yahoo") -> Optional[pd.DataFrame]:
        """Collect data with automatic failover between sources"""
        
        # Try preferred source first
        sources_to_try = [preferred_source] + [s for s in self.collectors.keys() if s != preferred_source]
        
        for source in sources_to_try:
            try:
                logger.info(f"Attempting to collect {symbol} data from {source}")
                
                if source == 'yahoo':
                    data = self.collectors[source].get_data(symbol, period, interval)
                else:
                    # Map interval for other sources
                    interval_map = {'1d': 'daily', '1min': '1min', '5min': '5min'}
                    mapped_interval = interval_map.get(interval, 'daily')
                    data = self.collectors[source].get_data(symbol, mapped_interval)
                
                if data is not None and not data.empty:
                    # Validate data quality
                    quality_metrics = self.validator.validate_ohlcv(data)
                    
                    logger.info(f"Data quality score: {quality_metrics['score']}")
                    
                    # Save data if quality is acceptable (>50)
                    if quality_metrics['score'] > 50:
                        self.storage.save_data(data, symbol, interval, source, quality_metrics)
                        return data
                    else:
                        logger.warning(f"Data quality too low ({quality_metrics['score']}), trying next source")
                
            except Exception as e:
                logger.error(f"Error collecting from {source}: {e}")
                continue
        
        # If all sources fail, try to get cached data
        logger.warning(f"All sources failed for {symbol}, attempting to load cached data")
        cached_data = self.storage.get_latest_data(symbol, interval)
        if cached_data is not None:
            logger.info(f"Using cached data for {symbol}")
            return cached_data
        
        logger.error(f"Failed to collect data for {symbol} from any source")
        return None
    
    def collect_multiple_symbols(self, symbols: List[str], period: str = "1mo", 
                                interval: str = "1d", max_workers: int = 5) -> Dict[str, pd.DataFrame]:
        """Collect data for multiple symbols concurrently"""
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.collect_data, symbol, period, interval): symbol 
                for symbol in symbols
            }
            
            # Collect results
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if data is not None:
                        results[symbol] = data
                        logger.info(f"Successfully collected data for {symbol}")
                    else:
                        logger.warning(f"Failed to collect data for {symbol}")
                except Exception as e:
                    logger.error(f"Exception collecting {symbol}: {e}")
        
        return results
    
    def get_data_summary(self) -> pd.DataFrame:
        """Get summary of all stored data"""
        conn = sqlite3.connect(self.storage.metadata_db)
        
        df = pd.read_sql_query('''
            SELECT symbol, interval, source, start_date, end_date, 
                   row_count, quality_score, created_at
            FROM data_metadata 
            ORDER BY created_at DESC
        ''', conn)
        
        conn.close()
        return df

def main():
    """Test the R26 Data Pipeline"""
    print("R26 Data Pipeline Test")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = R26DataPipeline()
    
    # Test single symbol collection
    print("Testing TQQQ data collection...")
    tqqq_data = pipeline.collect_data("TQQQ", period="1mo", interval="1d")
    
    if tqqq_data is not None:
        print(f"✅ Successfully collected {len(tqqq_data)} rows of TQQQ data")
        print("\nSample data:")
        print(tqqq_data.head())
        print(f"\nData range: {tqqq_data.index.min()} to {tqqq_data.index.max()}")
    else:
        print("❌ Failed to collect TQQQ data")
    
    # Test multiple symbols
    print("\n" + "=" * 50)
    print("Testing multiple symbol collection...")
    symbols = ["TQQQ", "QQQ", "SPY"]
    multi_data = pipeline.collect_multiple_symbols(symbols, period="5d", interval="1d")
    
    print(f"✅ Collected data for {len(multi_data)} symbols:")
    for symbol, data in multi_data.items():
        print(f"  {symbol}: {len(data)} rows")
    
    # Show data summary
    print("\n" + "=" * 50)
    print("Data Storage Summary:")
    summary = pipeline.get_data_summary()
    print(summary)

if __name__ == "__main__":
    main()
