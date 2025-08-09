"""
Research 26 - Risk Management Engine

This module implements the core risk management system including:
- Real-time position and exposure monitoring
- Circuit breaker implementation
- VaR calculation and stress testing
- Regime detection and correlation monitoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

from src.core.base_strategy import Position


class RiskLevel(Enum):
    """Risk alert levels"""
    GREEN = "normal"
    YELLOW = "warning"
    ORANGE = "elevated"
    RED = "critical"


class CircuitBreakerLevel(Enum):
    """Circuit breaker activation levels"""
    NONE = 0
    LEVEL_1 = 1  # -1.5% daily loss
    LEVEL_2 = 2  # -2.0% daily loss
    LEVEL_3 = 3  # -12% 30-day drawdown


@dataclass
class RiskAlert:
    """Risk alert notification"""
    level: RiskLevel
    message: str
    metric: str
    current_value: float
    limit_value: float
    timestamp: datetime
    action_required: bool = False


@dataclass
class Portfolio:
    """Portfolio state for risk calculations"""
    positions: Dict[str, float]  # symbol -> weight
    nav: float
    cash: float
    timestamp: datetime
    daily_pnl: float = 0.0
    daily_pnl_pct: float = 0.0


class RiskEngine:
    """
    Core risk management engine for Research 26.
    
    Monitors portfolio risk in real-time and implements automated
    circuit breakers and position limits.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize risk engine with configuration"""
        self.config = config or self._get_default_config()
        
        # Risk limits
        self.position_limits = {
            'single_name': self.config.get('single_name_limit', 0.03),  # 3% NAV
            'sector': self.config.get('sector_limit', 0.15),            # 15% NAV
            'gross': self.config.get('gross_limit', 1.50),              # 150% NAV
            'net': self.config.get('net_limit', 0.50)                   # ±50% NAV
        }
        
        # Circuit breaker thresholds
        self.circuit_breakers = {
            'daily_loss_1': self.config.get('daily_loss_1', -0.015),   # -1.5%
            'daily_loss_2': self.config.get('daily_loss_2', -0.020),   # -2.0%
            'drawdown_30d': self.config.get('drawdown_30d', -0.120)    # -12%
        }
        
        # VaR parameters
        self.var_confidence = self.config.get('var_confidence', 0.95)  # 95% VaR
        self.var_horizon = self.config.get('var_horizon', 1)           # 1-day
        
        # State tracking
        self.current_breaker_level = CircuitBreakerLevel.NONE
        self.risk_alerts = []
        self.portfolio_history = []
        self.correlation_matrix = pd.DataFrame()
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def _get_default_config() -> Dict:
        """Get default risk management configuration"""
        return {
            'single_name_limit': 0.03,
            'sector_limit': 0.15,
            'gross_limit': 1.50,
            'net_limit': 0.50,
            'daily_loss_1': -0.015,
            'daily_loss_2': -0.020,
            'drawdown_30d': -0.120,
            'var_confidence': 0.95,
            'var_horizon': 1,
            'correlation_threshold': 0.3,
            'vix_spike_threshold': 30,
            'max_sector_exposure': 0.15
        }
    
    def check_limits(self, portfolio: Portfolio) -> List[RiskAlert]:
        """
        Check all risk limits and generate alerts.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            List of risk alerts
        """
        alerts = []
        
        # Single name concentration check
        alerts.extend(self._check_single_name_limits(portfolio))
        
        # Gross/net exposure checks
        alerts.extend(self._check_exposure_limits(portfolio))
        
        # VaR check
        alerts.extend(self._check_var_limits(portfolio))
        
        # Correlation check
        alerts.extend(self._check_correlation_limits(portfolio))
        
        # Update alert history
        self.risk_alerts.extend(alerts)
        
        return alerts
    
    def _check_single_name_limits(self, portfolio: Portfolio) -> List[RiskAlert]:
        """Check single name concentration limits"""
        alerts = []
        
        for symbol, weight in portfolio.positions.items():
            abs_weight = abs(weight)
            
            if abs_weight > self.position_limits['single_name']:
                level = RiskLevel.RED if abs_weight > self.position_limits['single_name'] * 1.2 else RiskLevel.ORANGE
                
                alert = RiskAlert(
                    level=level,
                    message=f"Single name limit exceeded: {symbol}",
                    metric="single_name_concentration",
                    current_value=abs_weight,
                    limit_value=self.position_limits['single_name'],
                    timestamp=datetime.now(),
                    action_required=True
                )
                alerts.append(alert)
        
        return alerts
    
    def _check_exposure_limits(self, portfolio: Portfolio) -> List[RiskAlert]:
        """Check gross and net exposure limits"""
        alerts = []
        
        # Calculate exposures
        gross_exposure = sum(abs(weight) for weight in portfolio.positions.values())
        net_exposure = sum(portfolio.positions.values())
        
        # Gross exposure check
        if gross_exposure > self.position_limits['gross']:
            level = RiskLevel.RED if gross_exposure > self.position_limits['gross'] * 1.1 else RiskLevel.ORANGE
            
            alert = RiskAlert(
                level=level,
                message="Gross exposure limit exceeded",
                metric="gross_exposure",
                current_value=gross_exposure,
                limit_value=self.position_limits['gross'],
                timestamp=datetime.now(),
                action_required=True
            )
            alerts.append(alert)
        
        # Net exposure check
        if abs(net_exposure) > self.position_limits['net']:
            level = RiskLevel.ORANGE
            
            alert = RiskAlert(
                level=level,
                message="Net exposure limit exceeded",
                metric="net_exposure",
                current_value=abs(net_exposure),
                limit_value=self.position_limits['net'],
                timestamp=datetime.now(),
                action_required=False
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_var_limits(self, portfolio: Portfolio) -> List[RiskAlert]:
        """Check Value at Risk limits"""
        alerts = []
        
        try:
            var = self.calculate_var(portfolio)
            var_limit = 0.02  # 2% of NAV
            
            if var > var_limit:
                level = RiskLevel.RED if var > var_limit * 1.5 else RiskLevel.ORANGE
                
                alert = RiskAlert(
                    level=level,
                    message=f"VaR limit exceeded: {var:.2%}",
                    metric="value_at_risk",
                    current_value=var,
                    limit_value=var_limit,
                    timestamp=datetime.now(),
                    action_required=True
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.warning(f"VaR calculation failed: {e}")
        
        return alerts
    
    def _check_correlation_limits(self, portfolio: Portfolio) -> List[RiskAlert]:
        """Check correlation limits between strategies"""
        alerts = []
        
        if not self.correlation_matrix.empty:
            # Check for correlation spikes
            max_correlation = self.correlation_matrix.abs().max().max()
            correlation_threshold = self.config.get('correlation_threshold', 0.3)
            
            if max_correlation > correlation_threshold:
                level = RiskLevel.ORANGE
                
                alert = RiskAlert(
                    level=level,
                    message=f"High correlation detected: {max_correlation:.2f}",
                    metric="strategy_correlation",
                    current_value=max_correlation,
                    limit_value=correlation_threshold,
                    timestamp=datetime.now(),
                    action_required=False
                )
                alerts.append(alert)
        
        return alerts
    
    def check_breakers(self, portfolio: Portfolio) -> CircuitBreakerLevel:
        """
        Check circuit breaker conditions and return activation level.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Circuit breaker level to activate
        """
        # Check daily loss thresholds
        if portfolio.daily_pnl_pct <= self.circuit_breakers['daily_loss_2']:
            self.current_breaker_level = CircuitBreakerLevel.LEVEL_2
            self.logger.critical(f"Circuit breaker LEVEL 2 activated: {portfolio.daily_pnl_pct:.2%} daily loss")
            return CircuitBreakerLevel.LEVEL_2
        
        elif portfolio.daily_pnl_pct <= self.circuit_breakers['daily_loss_1']:
            self.current_breaker_level = CircuitBreakerLevel.LEVEL_1
            self.logger.warning(f"Circuit breaker LEVEL 1 activated: {portfolio.daily_pnl_pct:.2%} daily loss")
            return CircuitBreakerLevel.LEVEL_1
        
        # Check 30-day drawdown
        drawdown_30d = self._calculate_30day_drawdown(portfolio)
        if drawdown_30d <= self.circuit_breakers['drawdown_30d']:
            self.current_breaker_level = CircuitBreakerLevel.LEVEL_3
            self.logger.critical(f"Circuit breaker LEVEL 3 activated: {drawdown_30d:.2%} 30-day drawdown")
            return CircuitBreakerLevel.LEVEL_3
        
        # No breaker activation
        self.current_breaker_level = CircuitBreakerLevel.NONE
        return CircuitBreakerLevel.NONE
    
    def _calculate_30day_drawdown(self, portfolio: Portfolio) -> float:
        """Calculate 30-day rolling maximum drawdown"""
        if len(self.portfolio_history) < 30:
            return 0.0
        
        # Get last 30 days of NAV data
        recent_history = self.portfolio_history[-30:]
        nav_series = pd.Series([p.nav for p in recent_history])
        
        # Calculate rolling maximum and drawdown
        rolling_max = nav_series.expanding().max()
        drawdown = (nav_series - rolling_max) / rolling_max
        
        return drawdown.min()
    
    def calculate_var(self, portfolio: Portfolio) -> float:
        """
        Calculate Value at Risk for the portfolio.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            VaR as fraction of NAV
        """
        if len(self.portfolio_history) < 30:
            return 0.0  # Insufficient data
        
        # Calculate daily returns
        nav_series = pd.Series([p.nav for p in self.portfolio_history[-252:]])  # Last year
        returns = nav_series.pct_change().dropna()
        
        if len(returns) < 10:
            return 0.0
        
        # Calculate VaR using historical simulation
        var_percentile = (1 - self.var_confidence) * 100
        var = np.percentile(returns, var_percentile)
        
        return abs(var)  # Return as positive value
    
    def detect_regime(self, market_data: pd.DataFrame) -> str:
        """
        Detect market regime for risk adjustment.
        
        Args:
            market_data: Market data with price information
            
        Returns:
            Regime string: TREND_LOW_VOL, TREND_HIGH_VOL, CHOP_LOW_VOL, CHOP_HIGH_VOL
        """
        try:
            # Calculate trend score (momentum)
            returns = market_data['close'].pct_change()
            trend_score = returns.rolling(20).mean() / returns.rolling(20).std()
            current_trend = trend_score.iloc[-1] if not trend_score.empty else 0
            
            # Calculate volatility score
            vol_score = returns.rolling(20).std() * np.sqrt(252)  # Annualized
            current_vol = vol_score.iloc[-1] if not vol_score.empty else 0
            
            # Classify regime
            trend_threshold = 0.1
            vol_threshold = 0.20  # 20% annualized volatility
            
            if current_trend > trend_threshold and current_vol < vol_threshold:
                return "TREND_LOW_VOL"
            elif current_trend > trend_threshold and current_vol >= vol_threshold:
                return "TREND_HIGH_VOL"
            elif current_trend <= trend_threshold and current_vol < vol_threshold:
                return "CHOP_LOW_VOL"
            else:
                return "CHOP_HIGH_VOL"
        
        except Exception as e:
            self.logger.warning(f"Regime detection failed: {e}")
            return "UNKNOWN"
    
    def apply_circuit_breaker(self, portfolio: Portfolio, level: CircuitBreakerLevel) -> Dict[str, float]:
        """
        Apply circuit breaker adjustments to portfolio.
        
        Args:
            portfolio: Current portfolio state
            level: Circuit breaker level to apply
            
        Returns:
            Dictionary of adjusted position weights
        """
        adjusted_positions = portfolio.positions.copy()
        
        if level == CircuitBreakerLevel.LEVEL_1:
            # Halve gross exposure
            for symbol in adjusted_positions:
                adjusted_positions[symbol] *= 0.5
            self.logger.info("Applied circuit breaker LEVEL 1: halved gross exposure")
        
        elif level == CircuitBreakerLevel.LEVEL_2:
            # Flatten to 25% gross exposure
            gross_exposure = sum(abs(weight) for weight in adjusted_positions.values())
            if gross_exposure > 0:
                scale_factor = 0.25 / gross_exposure
                for symbol in adjusted_positions:
                    adjusted_positions[symbol] *= scale_factor
            self.logger.info("Applied circuit breaker LEVEL 2: flattened to 25% gross")
        
        elif level == CircuitBreakerLevel.LEVEL_3:
            # Safe mode: only Pillars A and C
            # This would require strategy pillar information
            # For now, reduce all positions by 75%
            for symbol in adjusted_positions:
                adjusted_positions[symbol] *= 0.25
            self.logger.info("Applied circuit breaker LEVEL 3: safe mode activated")
        
        return adjusted_positions
    
    def update_portfolio_history(self, portfolio: Portfolio) -> None:
        """Update portfolio history for risk calculations"""
        self.portfolio_history.append(portfolio)
        
        # Keep only last year of data
        if len(self.portfolio_history) > 252:
            self.portfolio_history = self.portfolio_history[-252:]
    
    def update_correlation_matrix(self, strategy_returns: pd.DataFrame) -> None:
        """Update correlation matrix between strategies"""
        try:
            self.correlation_matrix = strategy_returns.corr()
        except Exception as e:
            self.logger.warning(f"Correlation matrix update failed: {e}")
    
    def get_risk_summary(self, portfolio: Portfolio) -> Dict:
        """
        Get comprehensive risk summary.
        
        Args:
            portfolio: Current portfolio state
            
        Returns:
            Dictionary with risk metrics
        """
        # Calculate exposures
        gross_exposure = sum(abs(weight) for weight in portfolio.positions.values())
        net_exposure = sum(portfolio.positions.values())
        
        # Get largest positions
        sorted_positions = sorted(portfolio.positions.items(), key=lambda x: abs(x[1]), reverse=True)
        top_positions = sorted_positions[:5]
        
        # Calculate VaR
        var = self.calculate_var(portfolio)
        
        return {
            'timestamp': datetime.now(),
            'nav': portfolio.nav,
            'daily_pnl': portfolio.daily_pnl,
            'daily_pnl_pct': portfolio.daily_pnl_pct,
            'gross_exposure': gross_exposure,
            'net_exposure': net_exposure,
            'num_positions': len(portfolio.positions),
            'top_positions': top_positions,
            'var_95_1day': var,
            'circuit_breaker_level': self.current_breaker_level.value,
            'active_alerts': len([a for a in self.risk_alerts if a.timestamp > datetime.now() - timedelta(hours=1)]),
            'position_limits': self.position_limits,
            'within_limits': {
                'gross': gross_exposure <= self.position_limits['gross'],
                'net': abs(net_exposure) <= self.position_limits['net'],
                'single_name': all(abs(w) <= self.position_limits['single_name'] for w in portfolio.positions.values())
            }
        }
