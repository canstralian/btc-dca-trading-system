"""
Trading Engine for DCAlytics - Core DCA and Hedging Logic
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Dict
from .models import (
    DCAStrategy, TradeRecord, PortfolioSnapshot, 
    SimulationResult, BTCPriceData, HedgePosition
)


class TradingEngine:
    """Core trading engine implementing DCA and hedging strategies"""
    
    def __init__(self):
        self.btc_price_history = self._generate_sample_btc_data()
    
    def _generate_sample_btc_data(self) -> pd.DataFrame:
        """Generate sample BTC price data for simulation"""
        start_date = datetime(2020, 1, 1)
        end_date = datetime.now()
        dates = pd.date_range(start_date, end_date, freq='D')
        
        # Simulate BTC price evolution with some volatility
        np.random.seed(42)
        initial_price = 7000
        returns = np.random.normal(0.001, 0.04, len(dates))  # ~0.1% daily return, 4% volatility
        
        prices = [initial_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        return pd.DataFrame({
            'timestamp': dates,
            'price': prices
        })
    
    def get_btc_price(self, timestamp: datetime) -> float:
        """Get BTC price at specific timestamp"""
        # Convert to naive datetime for comparison
        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)
        
        # Find closest date in historical data
        price_data = self.btc_price_history
        closest_idx = (price_data['timestamp'] - timestamp).abs().idxmin()
        return price_data.loc[closest_idx, 'price']
    
    def calculate_dca_trades(self, strategy: DCAStrategy) -> List[TradeRecord]:
        """Calculate DCA trades based on strategy"""
        trades = []
        current_date = strategy.start_date
        
        # Convert to naive datetime if needed
        if current_date.tzinfo is not None:
            current_date = current_date.replace(tzinfo=None)
        end_date = strategy.end_date
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
        
        while current_date <= end_date:
            btc_price = self.get_btc_price(current_date)
            btc_quantity = strategy.investment_amount / btc_price
            
            # Main DCA buy
            trade = TradeRecord(
                timestamp=current_date,
                action='buy',
                btc_price=btc_price,
                amount_usd=strategy.investment_amount,
                btc_quantity=btc_quantity
            )
            trades.append(trade)
            
            # Handle hedging if percentage > 0
            if strategy.hedge_percentage > 0:
                hedge_amount = strategy.investment_amount * (strategy.hedge_percentage / 100)
                hedge_trade = TradeRecord(
                    timestamp=current_date,
                    action='hedge',
                    btc_price=btc_price,
                    amount_usd=hedge_amount,
                    btc_quantity=0,
                    hedge_action='short_position'
                )
                trades.append(hedge_trade)
            
            current_date += timedelta(days=strategy.frequency_days)
        
        return trades
    
    def calculate_portfolio_history(self, trades: List[TradeRecord], 
                                   strategy: DCAStrategy) -> List[PortfolioSnapshot]:
        """Calculate portfolio evolution over time"""
        portfolio_history = []
        btc_holdings = 0
        total_invested = 0
        hedge_positions = []
        
        # Get all unique dates for portfolio snapshots
        trade_dates = [trade.timestamp for trade in trades]
        
        # Convert to naive datetimes for pandas
        start_date = strategy.start_date
        end_date = strategy.end_date
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
            
        all_dates = pd.date_range(start_date, end_date, freq='D')
        
        for date in all_dates:
            # Process trades for this date
            daily_trades = [t for t in trades if t.timestamp.date() == date.date()]
            
            for trade in daily_trades:
                if trade.action == 'buy':
                    btc_holdings += trade.btc_quantity
                    total_invested += trade.amount_usd
                elif trade.action == 'hedge':
                    hedge_positions.append({
                        'amount': trade.amount_usd,
                        'entry_price': trade.btc_price,
                        'timestamp': trade.timestamp
                    })
            
            # Calculate current portfolio value
            current_btc_price = self.get_btc_price(date)
            btc_value = btc_holdings * current_btc_price
            
            # Calculate hedge value (simplified short position)
            hedge_value = 0
            for hedge in hedge_positions:
                # Simplified hedge calculation: profit from price decrease
                price_change = (hedge['entry_price'] - current_btc_price) / hedge['entry_price']
                hedge_value += hedge['amount'] * price_change
            
            total_value = btc_value + hedge_value
            unrealized_pnl = total_value - total_invested
            
            snapshot = PortfolioSnapshot(
                timestamp=date,
                total_invested=total_invested,
                btc_holdings=btc_holdings,
                btc_value=btc_value,
                hedge_value=hedge_value,
                total_value=total_value,
                unrealized_pnl=unrealized_pnl
            )
            portfolio_history.append(snapshot)
        
        return portfolio_history
    
    def calculate_metrics(self, portfolio_history: List[PortfolioSnapshot], 
                         strategy: DCAStrategy) -> Dict[str, float]:
        """Calculate performance metrics"""
        if not portfolio_history:
            return {}
        
        initial_value = portfolio_history[0].total_invested or 1
        final_value = portfolio_history[-1].total_value
        
        # Total return
        total_return = (final_value - initial_value) / initial_value * 100
        
        # Annualized return
        days = (strategy.end_date - strategy.start_date).days
        years = days / 365.25
        annualized_return = ((final_value / initial_value) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Max drawdown
        peak = 0
        max_drawdown = 0
        for snapshot in portfolio_history:
            if snapshot.total_value > peak:
                peak = snapshot.total_value
            drawdown = (peak - snapshot.total_value) / peak * 100 if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Simplified Sharpe ratio (assuming 2% risk-free rate)
        returns = []
        for i in range(1, len(portfolio_history)):
            if portfolio_history[i-1].total_value > 0:
                daily_return = (portfolio_history[i].total_value - portfolio_history[i-1].total_value) / portfolio_history[i-1].total_value
                returns.append(daily_return)
        
        if returns:
            avg_return = np.mean(returns) * 365  # Annualized
            volatility = np.std(returns) * np.sqrt(365)  # Annualized
            sharpe_ratio = (avg_return - 0.02) / volatility if volatility > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    
    def run_simulation(self, strategy: DCAStrategy) -> SimulationResult:
        """Run complete DCA simulation"""
        # Generate trades
        trades = self.calculate_dca_trades(strategy)
        
        # Calculate portfolio history
        portfolio_history = self.calculate_portfolio_history(trades, strategy)
        
        # Calculate metrics
        metrics = self.calculate_metrics(portfolio_history, strategy)
        
        # Create final portfolio snapshot
        final_portfolio = portfolio_history[-1] if portfolio_history else PortfolioSnapshot(
            timestamp=strategy.end_date,
            total_invested=0,
            btc_holdings=0,
            btc_value=0,
            hedge_value=0,
            total_value=0,
            unrealized_pnl=0
        )
        
        return SimulationResult(
            strategy=strategy,
            trades=trades,
            portfolio_history=portfolio_history,
            final_portfolio=final_portfolio,
            total_return=metrics.get('total_return', 0),
            annualized_return=metrics.get('annualized_return', 0),
            max_drawdown=metrics.get('max_drawdown', 0),
            sharpe_ratio=metrics.get('sharpe_ratio', 0)
        )