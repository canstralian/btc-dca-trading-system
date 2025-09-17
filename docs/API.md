# DCAlytics API Documentation

## Overview
DCAlytics provides a RESTful API for running Bitcoin Dollar-Cost Averaging (DCA) simulations with hedging strategies.

## Base URL
- Development: `http://localhost:8000`
- Production: Your deployed URL

## Authentication
Currently, no authentication is required for the API endpoints.

## Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Current BTC Price
**GET** `/api/btc-price/current`

Get the current Bitcoin price.

**Response:**
```json
{
  "price": 45000.50,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Historical BTC Price Data
**GET** `/api/btc-price`

Get historical Bitcoin price data.

**Query Parameters:**
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format  
- `limit` (optional): Maximum number of records (default: 365)

**Response:**
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "price": 45000.50,
    "volume": null
  }
]
```

### Run DCA Simulation
**POST** `/api/simulate`

Run a DCA simulation with specified strategy.

**Request Body:**
```json
{
  "strategy": {
    "investment_amount": 100,
    "frequency_days": 7,
    "hedge_percentage": 10,
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2024-01-01T00:00:00Z"
  },
  "use_historical_data": true
}
```

**Response:**
```json
{
  "strategy": {
    "investment_amount": 100,
    "frequency_days": 7,
    "hedge_percentage": 10,
    "start_date": "2023-01-01T00:00:00Z",
    "end_date": "2024-01-01T00:00:00Z"
  },
  "trades": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "action": "buy",
      "btc_price": 16500.00,
      "amount_usd": 100,
      "btc_quantity": 0.006060606,
      "hedge_action": null
    }
  ],
  "portfolio_history": [
    {
      "timestamp": "2023-01-01T00:00:00Z",
      "total_invested": 100,
      "btc_holdings": 0.006060606,
      "btc_value": 100,
      "hedge_value": 0,
      "total_value": 100,
      "unrealized_pnl": 0
    }
  ],
  "final_portfolio": {
    "timestamp": "2024-01-01T00:00:00Z",
    "total_invested": 5200,
    "btc_holdings": 0.12345678,
    "btc_value": 5500,
    "hedge_value": 50,
    "total_value": 5550,
    "unrealized_pnl": 350
  },
  "total_return": 6.73,
  "annualized_return": 6.73,
  "max_drawdown": 15.2,
  "sharpe_ratio": 1.25
}
```

### Example Strategies
**GET** `/api/strategies/example`

Get example DCA strategies.

**Response:**
```json
{
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
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `422`: Validation Error
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error description"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

## CORS

CORS is enabled for all origins in development. In production, configure specific allowed origins.

## Data Models

### DCA Strategy
- `investment_amount`: USD amount to invest at each interval
- `frequency_days`: Days between investments (1, 7, 14, 30)
- `hedge_percentage`: Percentage of investment to hedge (0-50)
- `start_date`: Simulation start date (ISO format)
- `end_date`: Simulation end date (ISO format)

### Performance Metrics
- `total_return`: Total return percentage
- `annualized_return`: Annualized return percentage
- `max_drawdown`: Maximum drawdown percentage
- `sharpe_ratio`: Risk-adjusted return metric