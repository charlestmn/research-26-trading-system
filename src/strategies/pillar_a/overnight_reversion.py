"""
Research 26 - Overnight Reversion Strategy (Pillar A)

This strategy exploits mean reversion in overnight returns by taking positions
at market close and exiting at market open or mid-morning.

Strategy Logic:
- Calculate z-score of daily return vs 20-day rolling mean/std
- Go short stocks with extreme positive overnight returns
- Go long stocks with extreme negative overnight returns
- Exit positions at next open or by 10 AM

Target: 11% volatility sleeve, high Sharpe ratio
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, time

from src.core.base_strategy import (
    BaseStrategy, StrategyConfig, StrategyPillar, 
    MarketData, Signal, SignalType, Position
)


class OvernightReversionStrategy(BaseStrategy):
    """
    Overnight mean reversion strategy for Pillar A (Micro Edges).
    
    This strategy identifies stocks with extreme overnight moves and bets
    on mean reversion during the next trading session.
    """
    
    def __init__(self, config: Optional[StrategyConfig] = None):
        """Initialize overnight reversion strategy"""
        if config is None:
            config = self._get_default_config()
        
        super().__init__(config)
        
        # Strategy-specific parameters
        self.lookback_window = 20  # Rolling window for z-score calculation
        self.entry_threshold = 1.75  # Z-score threshold for signal generation
        self.exit_time = time(10, 0)  # Exit by 10 AM if not at open
        self.max_positions = 50  # Maximum number of concurrent positions
        
        # Performance tracking
        self.signal_history = []
        self.trade_history = []
    
    @staticmethod
    def _get_default_config() -> StrategyConfig:
        """Get default configuration for overnight reversion strategy"""
        return StrategyConfig(
            name="overnight_reversion",
            pillar=StrategyPillar.A,
            target_vol=0.11,  # 11% target volatility
            universe=["SPY", "QQQ", "IWM"],  # Start with ETFs, expand to S&P 500
            max_position_size=0.02,  # 2% max per position for diversification
            rebalance_frequency="daily",
            cost_model={
                "commission": 0.0,  # Commission-free trading
                "slippage_bps": 4.5,  # 4.5 bps average slippage
                "market_impact": 0.1  # Minimal market impact for liquid names
            }
        )
    
    def generate_signals(self, data: MarketData) -> List[Signal]:
        """
        Generate overnight reversion signals based on extreme moves.
        
        Args:
            data: MarketData with OHLCV prices
            
        Returns:
            List of Signal objects for overnight reversion trades
        """
        if not data.validate():
            return []
        
        signals = []
        current_time = pd.Timestamp.now()
        
        # Calculate overnight returns (previous close to current open)
        prices = data.prices.copy()
        prices['prev_close'] = prices['close'].shift(1)
        prices['overnight_return'] = (prices['open'] - prices['prev_close']) / prices['prev_close']
        
        # Calculate rolling statistics for z-score
        prices['return_mean'] = prices['overnight_return'].rolling(self.lookback_window).mean()
        prices['return_std'] = prices['overnight_return'].rolling(self.lookback_window).std()
        prices['z_score'] = (prices['overnight_return'] - prices['return_mean']) / prices['return_std']
        
        # Get latest data for each symbol
        latest_data = prices.groupby(level=0).last() if isinstance(prices.index, pd.MultiIndex) else prices.iloc[-1:]
        
        for symbol in self.universe:
            if symbol not in latest_data.index:
                continue
                
            row = latest_data.loc[symbol] if isinstance(latest_data, pd.DataFrame) else latest_data
            
            # Skip if insufficient data
            if pd.isna(row['z_score']) or pd.isna(row['overnight_return']):
                continue
            
            z_score = row['z_score']
            overnight_return = row['overnight_return']
            
            # Generate signals based on extreme z-scores
            if abs(z_score) >= self.entry_threshold:
                # Mean reversion signal: fade extreme moves
                signal_type = SignalType.SELL if z_score > 0 else SignalType.BUY
                
                # Signal strength based on z-score magnitude
                strength = min(abs(z_score) / 3.0, 1.0)  # Cap at 3 standard deviations
                
                # Confidence based on consistency of pattern
                confidence = self._calculate_confidence(prices, symbol, z_score)
                
                signal = Signal(
                    symbol=symbol,
                    signal_type=signal_type,
                    strength=strength,
                    confidence=confidence,
                    timestamp=current_time,
                    metadata={
                        'z_score': z_score,
                        'overnight_return': overnight_return,
                        'strategy': 'overnight_reversion',
                        'entry_threshold': self.entry_threshold
                    }
                )
                
                signals.append(signal)
        
        self.signals_generated += len(signals)
        self.signal_history.extend(signals)
        
        return signals
    
    def _calculate_confidence(self, prices: pd.DataFrame, symbol: str, z_score: float) -> float:
        """
        Calculate confidence in signal based on historical pattern consistency.
        
        Args:
            prices: Price data with calculated metrics
            symbol: Symbol to analyze
            z_score: Current z-score
            
        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Get symbol-specific data
            if isinstance(prices.index, pd.MultiIndex):
                symbol_data = prices.loc[symbol].copy()
            else:
                symbol_data = prices.copy()
            
            # Look at historical performance of similar signals
            similar_signals = symbol_data[
                (abs(symbol_data['z_score']) >= self.entry_threshold) & 
                (np.sign(symbol_data['z_score']) == np.sign(z_score))
            ].copy()
            
            if len(similar_signals) < 5:
                return 0.5  # Default confidence for insufficient history
            
            # Calculate next-day returns for similar signals
            similar_signals['next_return'] = similar_signals['close'].shift(-1) / similar_signals['open'] - 1
            
            # Mean reversion success rate (opposite direction to overnight move)
            if z_score > 0:  # Extreme positive overnight, expect negative next day
                success_rate = (similar_signals['next_return'] < 0).mean()
            else:  # Extreme negative overnight, expect positive next day
                success_rate = (similar_signals['next_return'] > 0).mean()
            
            # Adjust confidence based on success rate and sample size
            sample_adjustment = min(len(similar_signals) / 20, 1.0)
            confidence = success_rate * sample_adjustment
            
            return max(0.1, min(0.9, confidence))  # Bound between 0.1 and 0.9
            
        except Exception:
            return 0.5  # Default confidence on error
    
    def size_positions(self, signals: List[Signal], portfolio_value: float) -> List[Position]:
        """
        Size positions based on signal strength and risk management.
        
        Args:
            signals: List of signals from generate_signals()
            portfolio_value: Current portfolio value
            
        Returns:
            List of Position objects with target weights
        """
        if not signals:
            return []
        
        positions = []
        
        # Sort signals by strength * confidence for prioritization
        sorted_signals = sorted(signals, key=lambda s: s.strength * s.confidence, reverse=True)
        
        # Limit to maximum number of positions
        selected_signals = sorted_signals[:self.max_positions]
        
        # Calculate base position size
        base_weight = self.target_vol / len(selected_signals) if selected_signals else 0
        
        for signal in selected_signals:
            # Adjust position size based on signal quality
            quality_multiplier = signal.strength * signal.confidence
            target_weight = base_weight * quality_multiplier
            
            # Apply maximum position size limit
            target_weight = min(target_weight, self.config.max_position_size)
            
            # Apply signal direction
            if signal.signal_type == SignalType.SELL:
                target_weight = -target_weight
            
            # Calculate trade size (assuming current weight is 0 for new positions)
            current_weight = self.current_positions.get(signal.symbol, 0.0)
            trade_size = target_weight - current_weight
            
            position = Position(
                symbol=signal.symbol,
                target_weight=target_weight,
                current_weight=current_weight,
                trade_size=trade_size,
                risk_adjusted=False,
                metadata={
                    'signal_strength': signal.strength,
                    'signal_confidence': signal.confidence,
                    'z_score': signal.metadata.get('z_score', 0),
                    'strategy': 'overnight_reversion'
                }
            )
            
            positions.append(position)
        
        return positions
    
    def validate_trades(self, positions: List[Position]) -> List[Position]:
        """
        Validate trades for liquidity, timing, and risk constraints.
        
        Args:
            positions: List of positions from size_positions()
            
        Returns:
            List of validated positions ready for execution
        """
        validated_positions = []
        current_time = datetime.now().time()
        
        # Only trade during specific hours (near close for entry)
        market_close = time(15, 45)  # 15 minutes before close
        market_open = time(9, 30)
        
        # Check if we're in valid trading window
        valid_entry_time = current_time >= market_close or current_time <= self.exit_time
        
        if not valid_entry_time:
            return []  # No trades outside valid windows
        
        for position in positions:
            # Skip tiny positions
            if abs(position.trade_size) < 0.001:  # Less than 0.1%
                continue
            
            # Liquidity check (simplified - would use real ADV data in production)
            if self._check_liquidity(position.symbol, abs(position.trade_size)):
                validated_positions.append(position)
            else:
                # Reduce position size if liquidity constrained
                reduced_size = position.trade_size * 0.5
                if abs(reduced_size) >= 0.001:
                    position.trade_size = reduced_size
                    position.target_weight = position.current_weight + reduced_size
                    position.risk_adjusted = True
                    validated_positions.append(position)
        
        return validated_positions
    
    def _check_liquidity(self, symbol: str, position_size: float) -> bool:
        """
        Check if position size is appropriate for symbol liquidity.
        
        Args:
            symbol: Symbol to check
            position_size: Absolute position size as fraction of portfolio
            
        Returns:
            True if position size is acceptable
        """
        # Simplified liquidity check - in production would use real ADV data
        if symbol in ['SPY', 'QQQ', 'IWM']:  # Highly liquid ETFs
            return position_size <= 0.05  # Up to 5% of portfolio
        else:
            return position_size <= 0.02  # Up to 2% for individual stocks
    
    def should_exit_position(self, symbol: str, current_time: datetime) -> bool:
        """
        Determine if position should be exited based on time or other criteria.
        
        Args:
            symbol: Symbol to check
            current_time: Current timestamp
            
        Returns:
            True if position should be exited
        """
        # Exit at market open or by exit time
        market_open = time(9, 30)
        
        return (current_time.time() >= market_open and 
                current_time.time() <= self.exit_time)
    
    def get_strategy_specific_metrics(self) -> Dict:
        """Get additional metrics specific to overnight reversion strategy"""
        base_metrics = self.get_performance_metrics()
        
        # Calculate strategy-specific metrics
        if self.signal_history:
            avg_z_score = np.mean([s.metadata.get('z_score', 0) for s in self.signal_history])
            avg_confidence = np.mean([s.confidence for s in self.signal_history])
            signal_distribution = {
                'buy_signals': sum(1 for s in self.signal_history if s.signal_type == SignalType.BUY),
                'sell_signals': sum(1 for s in self.signal_history if s.signal_type == SignalType.SELL)
            }
        else:
            avg_z_score = 0
            avg_confidence = 0
            signal_distribution = {'buy_signals': 0, 'sell_signals': 0}
        
        strategy_metrics = {
            'avg_z_score': avg_z_score,
            'avg_confidence': avg_confidence,
            'signal_distribution': signal_distribution,
            'entry_threshold': self.entry_threshold,
            'lookback_window': self.lookback_window,
            'max_positions': self.max_positions
        }
        
        return {**base_metrics, **strategy_metrics}
