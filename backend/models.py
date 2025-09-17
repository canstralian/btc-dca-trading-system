"""
Data models for DCAlytics BTC DCA Trading System
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class DCAStrategy(BaseModel):
    """DCA strategy configuration"""
    investment_amount: float
    frequency_days: int
    hedge_percentage: float
    start_date: datetime
    end_date: datetime


class TradeRecord(BaseModel):
    """Individual trade record"""
    timestamp: datetime
    action: str  # 'buy' or 'sell'
    btc_price: float
    amount_usd: float
    btc_quantity: float
    hedge_action: Optional[str] = None


class PortfolioSnapshot(BaseModel):
    """Portfolio state at a point in time"""
    timestamp: datetime
    total_invested: float
    btc_holdings: float
    btc_value: float
    hedge_value: float
    total_value: float
    unrealized_pnl: float


class SimulationRequest(BaseModel):
    """Request for running a DCA simulation"""
    strategy: DCAStrategy
    use_historical_data: bool = True


class SimulationResult(BaseModel):
    """Complete simulation results"""
    strategy: DCAStrategy
    trades: List[TradeRecord]
    portfolio_history: List[PortfolioSnapshot]
    final_portfolio: PortfolioSnapshot
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float


class BTCPriceData(BaseModel):
    """BTC price data point"""
    timestamp: datetime
    price: float
    volume: Optional[float] = None


class HedgePosition(BaseModel):
    """Hedge position details"""
    timestamp: datetime
    hedge_type: str  # 'short', 'options', 'stablecoin'
    amount: float
    entry_price: float
    current_value: float