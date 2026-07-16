# Live Financial Dashboard

Real-time stock market dashboard built with Python, Dash and Plotly. Pulls live data from Yahoo Finance and refreshes automatically.

**Live demo:** https://live-dashboard-41pf.onrender.com

## Features

- KPI cards with live price, daily change and volume for major tech stocks
- Interactive candlestick / line chart with volume overlay
- Multi-stock comparison, normalized to a common baseline (base = 100)
- "Today's Movers" – ranked best and worst performers of the day
- Auto-refresh every 60 seconds, no API key needed
- Custom dark theme, responsive layout, deployed on Render

## Stocks covered

AAPL · MSFT · GOOGL · AMZN · NVDA · META · TSLA

## Run locally

```bash
git clone https://github.com/tomertir/live-dashboard.git
cd live-dashboard
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8050

## Stack

| Layer | Tool |
|---|---|
| Data | yfinance (Yahoo Finance) |
| Processing | Pandas |
| Charts | Plotly |
| Web app | Dash |
| Styling | Bootstrap + custom CSS |
| Deployment | Render |
