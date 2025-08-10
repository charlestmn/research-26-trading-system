#!/usr/bin/env python3
"""
R26 Bulk Historical Data Collection Script
Collects 2-year 1-minute data for all Pillar A equities using Alpaca API
Designed for AWS EC2 execution with S3 storage
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict
import json

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from r26_data_pipeline_alpaca import R26AlpacaDataPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bulk_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkHistoricalCollector:
    """Orchestrates bulk collection of 2-year 1-minute historical data"""
    
    def __init__(self):
        self.pipeline = R26AlpacaDataPipeline()
        self.collection_stats = {
            'start_time': None,
            'end_time': None,
            'total_symbols': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'total_bars_collected': 0,
            'total_data_size_mb': 0,
            'errors': []
        }
        
    def get_pillar_a_universe(self) -> List[str]:
        """Get complete Pillar A universe: S&P 500 + top 1000 by ADV"""
        
        # Core S&P 500 symbols (expanded list)
        sp500_core = [
            # Mega caps (>$500B)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B',
            
            # Large caps ($100B-$500B)
            'UNH', 'JNJ', 'V', 'PG', 'JPM', 'HD', 'CVX', 'MA', 'PFE', 'ABBV',
            'BAC', 'KO', 'AVGO', 'PEP', 'TMO', 'COST', 'WMT', 'DIS', 'ABT', 'DHR',
            'VZ', 'ADBE', 'CMCSA', 'NKE', 'TXN', 'NEE', 'RTX', 'QCOM', 'PM', 'T',
            'CRM', 'NFLX', 'ORCL', 'WFC', 'AMD', 'LLY', 'INTC', 'UPS', 'IBM', 'GS',
            'MS', 'CAT', 'HON', 'AMGN', 'SPGI', 'LOW', 'INTU', 'BKNG', 'AXP', 'BLK',
            'SYK', 'TJX', 'MDLZ', 'GILD', 'C', 'SCHW', 'CB', 'MO', 'USB', 'ANTM',
            'ISRG', 'TGT', 'LRCX', 'CVS', 'ZTS', 'MMM', 'PLD', 'SO', 'DUK', 'BSX',
            'REGN', 'EQIX', 'AON', 'ICE', 'KLAC', 'APD', 'SHW', 'CME', 'EL', 'PYPL',
            'ITW', 'ADSK', 'GD', 'MMC', 'CCI', 'ATVI', 'MRNA', 'SNOW', 'DXCM', 'MELI',
            
            # Mid caps with high volume
            'ROKU', 'PLTR', 'COIN', 'RBLX', 'HOOD', 'SOFI', 'RIVN', 'LCID', 'F', 'GM',
            'AAL', 'DAL', 'UAL', 'CCL', 'NCLH', 'RCL', 'MGM', 'WYNN', 'LVS', 'PENN',
            'DKNG', 'FUBO', 'SKLZ', 'OPEN', 'WISH', 'CLOV', 'SPCE', 'TLRY', 'CGC', 'ACB'
        ]
        
        # High ADV ETFs and leveraged products
        high_adv_etfs = [
            # Broad market ETFs
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'EEM', 'EFA',
            
            # Sector ETFs
            'XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLP', 'XLY', 'XLU', 'XLRE', 'XLB',
            'XME', 'XRT', 'XHB', 'XOP', 'XBI', 'SOXX', 'SMH', 'ARKK', 'ARKQ', 'ARKG',
            
            # Fixed income
            'TLT', 'IEF', 'SHY', 'HYG', 'LQD', 'JNK', 'EMB', 'TIP', 'VCIT', 'VCSH',
            
            # Commodities
            'GLD', 'SLV', 'GDX', 'GDXJ', 'USO', 'UNG', 'DBA', 'DBC', 'PDBC', 'IAU',
            
            # Volatility
            'VXX', 'UVXY', 'SVXY', 'VIXY', 'VIXM', 'VIX',
            
            # Leveraged ETFs (3x)
            'TQQQ', 'SQQQ', 'SPXL', 'SPXS', 'TNA', 'TZA', 'FAS', 'FAZ', 'TECL', 'TECS',
            'LABU', 'LABD', 'CURE', 'RXL', 'NAIL', 'SRS', 'USLV', 'DSLV', 'NUGT', 'DUST',
            'JNUG', 'JDST', 'GUSH', 'DRIP', 'ERX', 'ERY', 'BOIL', 'KOLD', 'UGAZ', 'DGAZ',
            
            # 2x Leveraged
            'SSO', 'SDS', 'QLD', 'QID', 'UWM', 'TWM', 'ROM', 'REW', 'UYG', 'SKF',
            'UCC', 'SCC', 'UYM', 'SMN', 'UXI', 'SIJ', 'URE', 'SRS', 'UPW', 'SDP'
        ]
        
        # Crypto-related stocks (high volatility, good for micro edges)
        crypto_stocks = [
            'COIN', 'MSTR', 'RIOT', 'MARA', 'CLSK', 'BITF', 'HUT', 'BTBT', 'CAN', 'EBON',
            'SOS', 'EBANG', 'GREE', 'SPRT', 'ANY', 'HVBT', 'WULF', 'CORZ', 'IREN', 'CIFR'
        ]
        
        # Meme stocks and high retail interest
        meme_stocks = [
            'GME', 'AMC', 'BB', 'NOK', 'SNDL', 'NAKD', 'EXPR', 'KOSS', 'BBBY', 'CLOV',
            'WISH', 'WKHS', 'RIDE', 'NKLA', 'HYLN', 'GOEV', 'CANOO', 'FISV', 'CHPT', 'BLNK'
        ]
        
        # Combine all universes
        all_symbols = list(set(sp500_core + high_adv_etfs + crypto_stocks + meme_stocks))
        
        logger.info(f"Pillar A universe: {len(all_symbols)} symbols")
        return sorted(all_symbols)
    
    def collect_in_batches(self, symbols: List[str], batch_size: int = 10, 
                          delay_between_batches: int = 30) -> Dict:
        """Collect data in batches to manage API rate limits"""
        
        self.collection_stats['start_time'] = datetime.now()
        self.collection_stats['total_symbols'] = len(symbols)
        
        logger.info(f"Starting bulk collection: {len(symbols)} symbols in batches of {batch_size}")
        
        successful_collections = {}
        
        for i in range(0, len(symbols), batch_size):
            batch_num = i // batch_size + 1
            batch = symbols[i:i+batch_size]
            
            logger.info(f"\n=== BATCH {batch_num}/{(len(symbols)-1)//batch_size + 1} ===")
            logger.info(f"Symbols: {', '.join(batch)}")
            
            try:
                # Collect batch data
                batch_results = self.pipeline.alpaca_collector.get_multiple_symbols_historical(
                    batch, "1Min", lookback_days=730, max_workers=3
                )
                
                # Process and save each symbol
                for symbol, data in batch_results.items():
                    if data is not None and not data.empty:
                        # Validate data quality
                        quality = self.pipeline.validate_data_quality(data)
                        
                        if quality['score'] >= 70:  # High quality threshold for 1-min data
                            # Save to S3
                            s3_key = self.pipeline.storage.save_data_to_s3(
                                data, symbol, "1min", "alpaca"
                            )
                            
                            if s3_key:
                                successful_collections[symbol] = {
                                    'bars': len(data),
                                    'quality_score': quality['score'],
                                    's3_key': s3_key,
                                    'date_range': f"{data.index.min()} to {data.index.max()}"
                                }
                                
                                self.collection_stats['successful_collections'] += 1
                                self.collection_stats['total_bars_collected'] += len(data)
                                
                                logger.info(f"✅ {symbol}: {len(data)} bars (Q:{quality['score']}) -> S3")
                            else:
                                self.collection_stats['failed_collections'] += 1
                                self.collection_stats['errors'].append(f"{symbol}: S3 save failed")
                                logger.error(f"❌ {symbol}: S3 save failed")
                        else:
                            self.collection_stats['failed_collections'] += 1
                            self.collection_stats['errors'].append(
                                f"{symbol}: Low quality ({quality['score']}) - {quality['issues']}"
                            )
                            logger.warning(f"⚠️ {symbol}: Low quality ({quality['score']})")
                    else:
                        self.collection_stats['failed_collections'] += 1
                        self.collection_stats['errors'].append(f"{symbol}: No data returned")
                        logger.error(f"❌ {symbol}: No data returned")
                
                # Progress update
                progress = (i + len(batch)) / len(symbols) * 100
                logger.info(f"Progress: {progress:.1f}% ({self.collection_stats['successful_collections']} successful)")
                
                # Delay between batches to respect rate limits
                if i + batch_size < len(symbols):
                    logger.info(f"Waiting {delay_between_batches}s before next batch...")
                    time.sleep(delay_between_batches)
                    
            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}")
                for symbol in batch:
                    self.collection_stats['failed_collections'] += 1
                    self.collection_stats['errors'].append(f"{symbol}: Batch error - {str(e)}")
        
        self.collection_stats['end_time'] = datetime.now()
        return successful_collections
    
    def generate_collection_report(self, successful_collections: Dict) -> str:
        """Generate comprehensive collection report"""
        
        duration = self.collection_stats['end_time'] - self.collection_stats['start_time']
        
        report = f"""
=== R26 BULK HISTORICAL DATA COLLECTION REPORT ===

Collection Summary:
- Start Time: {self.collection_stats['start_time']}
- End Time: {self.collection_stats['end_time']}
- Duration: {duration}
- Total Symbols Attempted: {self.collection_stats['total_symbols']}
- Successful Collections: {self.collection_stats['successful_collections']}
- Failed Collections: {self.collection_stats['failed_collections']}
- Success Rate: {(self.collection_stats['successful_collections']/self.collection_stats['total_symbols']*100):.1f}%
- Total Bars Collected: {self.collection_stats['total_bars_collected']:,}

Data Quality Summary:
"""
        
        if successful_collections:
            quality_scores = [info['quality_score'] for info in successful_collections.values()]
            avg_quality = sum(quality_scores) / len(quality_scores)
            min_quality = min(quality_scores)
            max_quality = max(quality_scores)
            
            report += f"""
- Average Quality Score: {avg_quality:.1f}
- Quality Range: {min_quality} - {max_quality}
- High Quality (>90): {sum(1 for q in quality_scores if q > 90)}
- Good Quality (70-90): {sum(1 for q in quality_scores if 70 <= q <= 90)}

Top Performers by Data Volume:
"""
            
            # Sort by bar count
            top_performers = sorted(
                successful_collections.items(),
                key=lambda x: x[1]['bars'],
                reverse=True
            )[:10]
            
            for symbol, info in top_performers:
                report += f"- {symbol}: {info['bars']:,} bars (Q:{info['quality_score']})"
        
        if self.collection_stats['errors']:
            report += f"\n\nErrors ({len(self.collection_stats['errors'])}):\n"
            for error in self.collection_stats['errors'][:20]:  # Show first 20 errors
                report += f"- {error}\n"
            
            if len(self.collection_stats['errors']) > 20:
                report += f"... and {len(self.collection_stats['errors']) - 20} more errors\n"
        
        report += "\n=== END REPORT ==="
        
        return report
    
    def save_collection_metadata(self, successful_collections: Dict):
        """Save collection metadata for future reference"""
        
        metadata = {
            'collection_timestamp': self.collection_stats['start_time'].isoformat(),
            'collection_stats': self.collection_stats,
            'successful_symbols': list(successful_collections.keys()),
            'collection_details': successful_collections
        }
        
        # Save to local file
        metadata_file = f"bulk_collection_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Collection metadata saved to: {metadata_file}")
        
        # Try to save to S3 as well
        try:
            s3_key = f"collection_metadata/{metadata_file}"
            self.pipeline.storage.s3_client.put_object(
                Bucket=self.pipeline.storage.bucket_name,
                Key=s3_key,
                Body=json.dumps(metadata, indent=2, default=str),
                ContentType='application/json'
            )
            logger.info(f"Collection metadata uploaded to S3: {s3_key}")
        except Exception as e:
            logger.warning(f"Failed to upload metadata to S3: {e}")

def main():
    """Execute bulk historical data collection"""
    
    print("R26 BULK HISTORICAL DATA COLLECTION")
    print("2-Year 1-Minute Data for Pillar A Universe")
    print("=" * 60)
    
    try:
        # Initialize collector
        collector = BulkHistoricalCollector()
        
        # Get universe
        symbols = collector.get_pillar_a_universe()
        print(f"\nTarget universe: {len(symbols)} symbols")
        
        # Confirm execution
        print(f"\nThis will collect 2 years of 1-minute data for {len(symbols)} symbols.")
        print("Estimated time: 2-4 hours depending on API performance.")
        print("Estimated data size: 5-10 GB")
        
        confirm = input("\nProceed with bulk collection? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Collection cancelled.")
            return
        
        # Execute collection
        print("\nStarting bulk collection...")
        successful_collections = collector.collect_in_batches(
            symbols, 
            batch_size=8,  # Smaller batches for stability
            delay_between_batches=45  # Longer delays for rate limiting
        )
        
        # Generate and save report
        report = collector.generate_collection_report(successful_collections)
        print("\n" + report)
        
        # Save report to file
        report_file = f"bulk_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Save metadata
        collector.save_collection_metadata(successful_collections)
        
        print(f"\n✅ Bulk collection completed!")
        print(f"Report saved to: {report_file}")
        print(f"Successful collections: {len(successful_collections)}/{len(symbols)}")
        
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user.")
        logger.info("Collection interrupted by user")
    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        logger.error(f"Collection failed: {e}")

if __name__ == "__main__":
    main()
