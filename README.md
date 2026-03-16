# 📈 Live Financial Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-377AB?style=flat&logo=python)](https://python.org)
[![Dash](https://img.shields.io/badge/Dash-Plotly-FF6B6B?style=flat&logo=plotly)](https://dash.plotly.com)
[![Live Data](https://img.shields.io/badge/Data-Yahoo%20Finance-6C3483?style=flat)](https://finance.yahoo.com)

> Real-time stock market analytics dashboard built with Python, Dash, and Plotly.

---

## ✨ Features

- **Live KPI Cards** — Real-time price, daily change, and volume for top stocks
- **Candlestick / Line Chart** — Interactive price chart with volume overlay
- **Multi-Stock Comparison** — Normalized performance comparison (base=100)
- **Today's Movers** — Ranked best/worst performers of the day
- **Auto Refresh** — Data refreshes every 60 seconds

## 🛠 Tech Stack

| Tech | Purpose |
|------|---------|
| Python | Backend & data processing |
| Dash | Web framework |
| Plotly | Interactive charts |
| yfinance | Live market data (free, no API key) |
| Pandas | Data manipulation |
| Bootstrap | Responsive layout |

## 🚀 Getting Started

```bash
# 1. Clone
git clone https://github.com/YOUR_USER/live-dashboard.git
cd live-dashboard

# 2. Install
pip install -r requirements.txt

# 3. Run
python app.py

# 4. Open
http://localhost:8050
```

## 📁 Structure

```
live-dashboard/
├── app.py              # Main application
├── assets/
│   └── style.css       # Custom dark theme
├── requirements.txt
└── README.md
```

## 📊 Stocks Covered

AAPL · MSFT · GOOGL · AMZN · NVDA · META · TSLA

---

*Built for portfolio purposes · Data from Yahoo Finance*
