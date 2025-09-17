"""
FastAPI Backend for DCAlytics BTC DCA Trading System
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import List
import os

from .models import SimulationRequest, SimulationResult, BTCPriceData
from .trading_engine import TradingEngine

# Create FastAPI app
app = FastAPI(
    title="DCAlytics API",
    description="Bitcoin DCA Trading System with Hedging Strategies",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize trading engine
trading_engine = TradingEngine()

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def read_root():
    """Serve the main dashboard"""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "DCAlytics API is running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


@app.post("/api/simulate", response_model=SimulationResult)
async def run_simulation(request: SimulationRequest):
    """Run DCA simulation with specified strategy"""
    try:
        result = trading_engine.run_simulation(request.strategy)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/api/btc-price", response_model=List[BTCPriceData])
async def get_btc_price_history(
    start_date: datetime = None,
    end_date: datetime = None,
    limit: int = 365
):
    """Get historical BTC price data"""
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=limit)
        if not end_date:
            end_date = datetime.now()
        
        # Filter price data
        price_data = trading_engine.btc_price_history
        mask = (price_data['timestamp'] >= start_date) & (price_data['timestamp'] <= end_date)
        filtered_data = price_data[mask].head(limit)
        
        return [
            BTCPriceData(
                timestamp=row['timestamp'],
                price=row['price']
            )
            for _, row in filtered_data.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price data: {str(e)}")


@app.get("/api/btc-price/current")
async def get_current_btc_price():
    """Get current BTC price"""
    try:
        current_price = trading_engine.get_btc_price(datetime.now())
        return {
            "price": current_price,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current price: {str(e)}")


@app.get("/api/strategies/example")
async def get_example_strategies():
    """Get example DCA strategies"""
    return {
        "conservative": {
            "investment_amount": 100,
            "frequency_days": 7,
            "hedge_percentage": 10,
            "description": "Weekly $100 investment with 10% hedging"
        },
        "aggressive": {
            "investment_amount": 500,
            "frequency_days": 14,
            "hedge_percentage": 25,
            "description": "Bi-weekly $500 investment with 25% hedging"
        },
        "hodl": {
            "investment_amount": 1000,
            "frequency_days": 30,
            "hedge_percentage": 0,
            "description": "Monthly $1000 investment, no hedging"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)