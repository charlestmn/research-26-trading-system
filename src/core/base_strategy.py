"""
Research 26 - Base Strategy Interface

This module defines the abstract base class for all trading strategies in the Research 26 system.
All strategies must inherit from BaseStrategy and implement the required methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from enum import Enum


class StrategyPillar(Enum):
    """Strategy pillar classification"""
    A = "micro_edges"      # Short-hold, high Sharpe
    B = "event_driven"     # Medium hold, bursts of alpha
    C = "options_vol"      # Convexity, risk-capped
    D = "slow_tilts"       # Capacity & balance


class SignalType(Enum):
    """Signal types for position sizing"""
    BUY = 1
    SELL = -1
    HOLD = 0


@dataclass
class StrategyConfig:
    """Configuration for strategy initialization"""
    name: str
    pillar: StrategyPillar
    target_vol: float  # Target volatility (e.g., 0.11 for 11%)
    universe: List[str]  # List of symbols or universe definition
    max_position_size: float = 0.03  # Max 3% NAV per position
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    cost_model: Optional[Dict] = None  # Slippage and commission assumptions
    
    def __post_init__(self):
        """Validate configuration parameters"""
        if self.target_vol <= 0 or self.target_vol > 1:
            raise ValueError("Target volatility must be between 0 and 1")
        if self.max_position_size <= 0 or self.max_position_size > 0.1:
            raise ValueError("Max position size must be between 0 and 0.1 (10%)")


@dataclass
class MarketData:
    """Container for market data used by strategies"""
    prices: pd.DataFrame  # OHLCV data
    fundamentals: Optional[pd.DataFrame] = None
    options: Optional[pd.DataFrame] = None
    news: Optional[pd.DataFrame] = None
    economic: Optional[pd.DataFrame] = None
    
    def validate(self) -> bool:
        """Validate market data integrity"""
        if self.prices.empty:
            return False
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in self.prices.columns for col in required_columns)


@dataclass
class Signal:
    """Individual trading signal"""
    symbol: str
    signal_type: SignalType
    strength: float  # Signal strength (0-1)
    confidence: float  # Model confidence (0-1)
    timestamp: pd.Timestamp
    metadata: Optional[Dict] = None


@dataclass
class Position:
    """Position sizing output"""
    symbol: str
    target_weight: float  # Target portfolio weight
    current_weight: float  # Current portfolio weight
    trade_size: float  # Required trade size
    risk_adjusted: bool = False  # Whether position was risk-adjusted
    metadata: Optional[Dict] = None


class BaseStrategy(ABC):
    """
    Abstract base class for all Research 26 trading strategies.
    
    Each strategy must implement the core methods for signal generation,
    position sizing, and trade validation. The framework handles execution,
    risk management, and performance tracking.
    """
    
    def __init__(self, config: StrategyConfig):
        """
        Initialize strategy with configuration.
        
        Args:
            config: StrategyConfig object with strategy parameters
        """
        self.config = config
        self.name = config.name
        self.pillar = config.pillar
        self.target_vol = config.target_vol
        self.universe = config.universe
        
        # Performance tracking
        self.signals_generated = 0
        self.trades_executed = 0
        self.last_rebalance = None
        
        # Risk metrics
        self.current_positions = {}
        self.realized_vol = 0.0
        self.sharpe_ratio = 0.0
        
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate strategy configuration"""
        if not self.universe:
            raise ValueError("Strategy universe cannot be empty")
        if self.target_vol <= 0:
            raise ValueError("Target volatility must be positive")
    
    @abstractmethod
    def generate_signals(self, data: MarketData) -> List[Signal]:
        """
        Generate trading signals based on market data.
        
        This is the core alpha generation method that each strategy must implement.
        It should analyze the provided market data and return a list of trading signals.
        
        Args:
            data: MarketData object containing prices and other market information
            
        Returns:
            List of Signal objects with buy/sell/hold recommendations
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    @abstractmethod
    def size_positions(self, signals: List[Signal], portfolio_value: float) -> List[Position]:
        """
        Convert signals to position sizes based on risk management rules.
        
        This method takes the raw signals and converts them to actual position sizes,
        considering portfolio value, target volatility, and risk constraints.
        
        Args:
            signals: List of Signal objects from generate_signals()
            portfolio_value: Current portfolio value in dollars
            
        Returns:
            List of Position objects with target weights and trade sizes
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    @abstractmethod
    def validate_trades(self, positions: List[Position]) -> List[Position]:
        """
        Apply final risk checks and filters to proposed trades.
        
        This method performs final validation of trades before execution,
        including liquidity checks, position limits, and other constraints.
        
        Args:
            positions: List of Position objects from size_positions()
            
        Returns:
            List of validated Position objects ready for execution
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass
    
    def calculate_target_volatility(self, returns: pd.Series) -> float:
        """
        Calculate realized volatility for comparison with target.
        
        Args:
            returns: Series of strategy returns
            
        Returns:
            Annualized volatility
        """
        if len(returns) < 2:
            return 0.0
        return returns.std() * np.sqrt(252)  # Annualized
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio for strategy performance.
        
        Args:
            returns: Series of strategy returns
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0.0
        
        excess_returns = returns.mean() * 252 - risk_free_rate
        volatility = self.calculate_target_volatility(returns)
        
        return excess_returns / volatility if volatility > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict:
        """
        Get current strategy performance metrics.
        
        Returns:
            Dictionary with performance statistics
        """
        return {
            'name': self.name,
            'pillar': self.pillar.value,
            'target_vol': self.target_vol,
            'realized_vol': self.realized_vol,
            'sharpe_ratio': self.sharpe_ratio,
            'signals_generated': self.signals_generated,
            'trades_executed': self.trades_executed,
            'last_rebalance': self.last_rebalance,
            'active_positions': len(self.current_positions)
        }
    
    def should_rebalance(self, current_time: pd.Timestamp) -> bool:
        """
        Determine if strategy should rebalance based on frequency setting.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            True if rebalance is needed
        """
        if self.last_rebalance is None:
            return True
            
        if self.config.rebalance_frequency == "daily":
            return current_time.date() > self.last_rebalance.date()
        elif self.config.rebalance_frequency == "weekly":
            return (current_time - self.last_rebalance).days >= 7
        elif self.config.rebalance_frequency == "monthly":
            return current_time.month != self.last_rebalance.month
        
        return False
    
    def update_positions(self, executed_trades: List[Position]) -> None:
        """
        Update internal position tracking after trade execution.
        
        Args:
            executed_trades: List of executed Position objects
        """
        for position in executed_trades:
            if position.target_weight == 0:
                # Position closed
                self.current_positions.pop(position.symbol, None)
            else:
                # Position opened or adjusted
                self.current_positions[position.symbol] = position.target_weight
        
        self.trades_executed += len(executed_trades)
        self.last_rebalance = pd.Timestamp.now()
    
    def __repr__(self) -> str:
        """String representation of strategy"""
        return f"{self.__class__.__name__}(name='{self.name}', pillar={self.pillar.value})"
