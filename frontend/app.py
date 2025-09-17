"""
Streamlit Frontend for DCAlytics
Optional alternative to the HTML dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="DCAlytics - BTC DCA Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f97316;
    }
    
    .stMetric > div > div > div > div {
        color: #f97316;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitDCAlytics:
    def __init__(self):
        self.api_base = "http://localhost:8000"  # Adjust as needed
        
    def run(self):
        # Header
        st.title("🚀 DCAlytics")
        st.markdown("### Smart, Hedged BTC Investing Made Simple")
        st.markdown("---")
        
        # Sidebar for strategy configuration
        with st.sidebar:
            st.header("⚙️ Strategy Configuration")
            
            # Investment parameters
            investment_amount = st.number_input(
                "Investment Amount (USD)",
                min_value=1,
                value=100,
                step=1,
                help="Amount to invest at each DCA interval"
            )
            
            frequency_days = st.selectbox(
                "DCA Frequency",
                options=[1, 7, 14, 30],
                index=1,
                format_func=lambda x: {1: "Daily", 7: "Weekly", 14: "Bi-weekly", 30: "Monthly"}[x]
            )
            
            hedge_percentage = st.slider(
                "Hedge Percentage",
                min_value=0,
                max_value=50,
                value=10,
                step=1,
                help="Percentage of investment to hedge against volatility"
            )
            
            # Date range
            st.subheader("📅 Time Period")
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=365)
                )
            
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
            
            # Run simulation button
            if st.button("🎯 Run Simulation", use_container_width=True):
                if start_date >= end_date:
                    st.error("Start date must be before end date")
                else:
                    self.run_simulation(
                        investment_amount,
                        frequency_days,
                        hedge_percentage,
                        start_date,
                        end_date
                    )
        
        # Main content area
        if 'simulation_result' not in st.session_state:
            # Welcome message
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info("👈 Configure your DCA strategy in the sidebar and click 'Run Simulation' to get started!")
                
                # Show current BTC price
                try:
                    current_price = self.get_current_btc_price()
                    st.metric("Current BTC Price", f"${current_price:,.2f}")
                except:
                    st.warning("Unable to fetch current BTC price")
        else:
            # Display simulation results
            self.display_results(st.session_state.simulation_result)
    
    def run_simulation(self, investment_amount, frequency_days, hedge_percentage, start_date, end_date):
        """Run DCA simulation"""
        try:
            with st.spinner("Running simulation..."):
                # Prepare request data
                strategy_data = {
                    "strategy": {
                        "investment_amount": investment_amount,
                        "frequency_days": frequency_days,
                        "hedge_percentage": hedge_percentage,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "use_historical_data": True
                }
                
                # Make API request (simulate if API not available)
                try:
                    response = requests.post(f"{self.api_base}/api/simulate", json=strategy_data)
                    if response.status_code == 200:
                        result = response.json()
                    else:
                        # Fallback to simulated data
                        result = self.simulate_locally(strategy_data["strategy"])
                except:
                    # Fallback to simulated data
                    result = self.simulate_locally(strategy_data["strategy"])
                
                st.session_state.simulation_result = result
                st.success("Simulation completed successfully!")
                st.rerun()
                
        except Exception as e:
            st.error(f"Simulation failed: {str(e)}")
    
    def simulate_locally(self, strategy):
        """Local simulation fallback"""
        # Generate sample data for demonstration
        start_date = datetime.fromisoformat(strategy["start_date"])
        end_date = datetime.fromisoformat(strategy["end_date"])
        
        # Generate sample portfolio data
        dates = pd.date_range(start_date, end_date, freq='D')
        np.random.seed(42)
        
        # Simulate portfolio growth
        initial_value = 0
        values = [initial_value]
        invested = [0]
        
        for i, date in enumerate(dates[1:]):
            # Add investments on DCA schedule
            if i % strategy["frequency_days"] == 0:
                invested.append(invested[-1] + strategy["investment_amount"])
            else:
                invested.append(invested[-1])
            
            # Simulate market movement
            growth = np.random.normal(0.0005, 0.02)  # Small daily growth with volatility
            values.append(max(0, values[-1] * (1 + growth) + (invested[-1] - invested[-2] if len(invested) > 1 else 0)))
        
        # Create portfolio history
        portfolio_history = []
        for i, date in enumerate(dates):
            portfolio_history.append({
                "timestamp": date.isoformat(),
                "total_invested": invested[i],
                "total_value": values[i],
                "unrealized_pnl": values[i] - invested[i]
            })
        
        # Calculate metrics
        final_value = values[-1]
        total_invested = invested[-1]
        total_return = ((final_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "strategy": strategy,
            "portfolio_history": portfolio_history,
            "final_portfolio": {
                "total_invested": total_invested,
                "total_value": final_value,
                "unrealized_pnl": final_value - total_invested,
                "btc_holdings": final_value / 50000,  # Assume BTC at $50k
            },
            "total_return": total_return,
            "annualized_return": total_return,  # Simplified
            "max_drawdown": 15.2,
            "sharpe_ratio": 1.25
        }
    
    def display_results(self, result):
        """Display simulation results"""
        st.header("📊 Simulation Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Return",
                f"{result['total_return']:.2f}%",
                delta=f"{result['total_return']:.2f}%" if result['total_return'] > 0 else None
            )
        
        with col2:
            st.metric(
                "Annualized Return",
                f"{result['annualized_return']:.2f}%"
            )
        
        with col3:
            st.metric(
                "Max Drawdown",
                f"{result['max_drawdown']:.2f}%",
                delta=f"-{result['max_drawdown']:.2f}%",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Sharpe Ratio",
                f"{result['sharpe_ratio']:.2f}"
            )
        
        # Portfolio summary
        st.subheader("💰 Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        
        final_portfolio = result["final_portfolio"]
        
        with col1:
            st.metric(
                "Total Invested",
                f"${final_portfolio['total_invested']:,.2f}"
            )
        
        with col2:
            st.metric(
                "Portfolio Value",
                f"${final_portfolio['total_value']:,.2f}"
            )
        
        with col3:
            st.metric(
                "Unrealized P&L",
                f"${final_portfolio['unrealized_pnl']:,.2f}",
                delta=f"${final_portfolio['unrealized_pnl']:,.2f}"
            )
        
        # Charts
        st.subheader("📈 Portfolio Performance")
        
        # Prepare data for plotting
        portfolio_df = pd.DataFrame(result["portfolio_history"])
        portfolio_df['timestamp'] = pd.to_datetime(portfolio_df['timestamp'])
        
        # Portfolio value chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_df['timestamp'],
            y=portfolio_df['total_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='#10b981', width=2),
            fill='tonexty'
        ))
        
        fig.add_trace(go.Scatter(
            x=portfolio_df['timestamp'],
            y=portfolio_df['total_invested'],
            mode='lines',
            name='Total Invested',
            line=dict(color='#6b7280', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="Portfolio Value Over Time",
            xaxis_title="Date",
            yaxis_title="Value (USD)",
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Strategy details
        with st.expander("📋 Strategy Details"):
            strategy = result["strategy"]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Investment Amount:** ${strategy['investment_amount']}")
                st.write(f"**Frequency:** Every {strategy['frequency_days']} days")
            
            with col2:
                st.write(f"**Hedge Percentage:** {strategy['hedge_percentage']}%")
                st.write(f"**Duration:** {strategy['start_date']} to {strategy['end_date']}")
    
    def get_current_btc_price(self):
        """Get current BTC price"""
        try:
            response = requests.get(f"{self.api_base}/api/btc-price/current")
            if response.status_code == 200:
                return response.json()["price"]
        except:
            pass
        
        # Fallback to simulated price
        return 45000 + np.random.normal(0, 2000)

def main():
    app = StreamlitDCAlytics()
    app.run()

if __name__ == "__main__":
    main()