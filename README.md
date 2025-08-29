# btc-dca-trading-system


<!-- Load GitHub Buttons script -->
<script async defer src="https://buttons.github.io/buttons.js"></script>

*Smart, hedged BTC investing made simple.*

## **Table of Contents**

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Project Structure](#project-structure)
6. [Configuration](#configuration)
7. [Contributing](#contributing)
8. [License](#license)

---

## **Introduction**

DCAlytics is an interactive cryptocurrency dashboard and simulation tool that combines **dynamic dollar-cost averaging (DCA)** with **risk-managed hedging strategies**. The platform allows users to:

* Visualize portfolio performance
* Simulate BTC trades
* Optimize investments while managing market volatility

It features a sleek, responsive interface built for both desktop and mobile.

---

## **Features**

* **Dynamic DCA Engine**: Configure recurring BTC purchases at user-defined intervals.
* **Hedging Strategies**: Reduce exposure to market volatility with adjustable hedging percentages.
* **Portfolio Analytics**: Real-time charts comparing DCA strategies vs HODL.
* **Trade Simulation**: Backtest strategies using historical and live BTC data.
* **Responsive Interface**: TailwindCSS + Chart.js for interactive dashboards.

---

## **Installation**

### **Prerequisites**

* Python 3.11+
* Node.js 18+ (for frontend if running locally)
* Git

### **Clone the Repository**

```bash
git clone https://github.com/canstralian/dcalytics.git
cd dcalytics
```

### **Backend Setup (FastAPI)**

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn backend.main:app --reload
```

### **Frontend Setup (Static Dashboard / Gradio / Streamlit)**

* **Option 1: Static Frontend**
  Simply open `frontend/index.html` in a browser or deploy to **Hugging Face Spaces**.

* **Option 2: Streamlit (Optional)**

```bash
pip install streamlit
streamlit run frontend/app.py
```

---

## **Usage**

1. Open the dashboard in a browser.
2. Configure your DCA strategy:

   * Investment Amount
   * DCA Frequency
   * Hedge Percentage
   * Time Period
3. Click **Run Simulation**.
4. Visualize results: portfolio value, BTC price evolution, risk metrics, and performance comparison charts.
5. Export reports if needed.

---

## **Project Structure**

```
dcalytics/
├── backend/                 # FastAPI backend
│   ├── main.py              # API routes
│   ├── models.py            # Data models
│   ├── trading_engine.py    # Algorithmic trading logic
│   └── requirements.txt
├── frontend/                # Dashboard UI
│   ├── index.html
│   ├── app.py               # Streamlit frontend (optional)
│   ├── styles.css
│   └── scripts.js
├── data/                    # Sample datasets or cached BTC prices
├── docs/                    # Documentation and diagrams
└── README.md
```

---

## **Configuration**

* **Backend**: `config.yaml` or `.env` for API keys (if using live BTC feeds).
* **Frontend**: TailwindCSS variables for theming; Chart.js for charts.
* **Simulation Parameters**: Set via dashboard sliders and dropdowns.

---

## **Contributing**

1. Fork the repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature-name`)
5. Open a Pull Request

---

## **License**

This project is licensed under **Apache 2.0** — see the LICENSE file for details.

---
