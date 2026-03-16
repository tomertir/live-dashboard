

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf #Yahoo Finance
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Live Financial Dashboard"
)
server = app.server

#Constants
STOCKS = {
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN":  "Amazon",
    "NVDA":  "NVIDIA",
    "META":  "Meta",
    "TSLA":  "Tesla",
}

COLORS = {
    "bg":        "#0d1117",
    "card":      "#161b22",
    "border":    "#30363d",
    "accent":    "#58a6ff",
    "green":     "#3fb950",
    "red":       "#f85149",
    "yellow":    "#d29922",
    "text":      "#e6edf3",
    "subtext":   "#8b949e",
}

#Helper: fetch data
def get_stock_data(ticker: str, period: str = "1mo") -> pd.DataFrame:
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()

def get_quick_info(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2:
            return {}
        prev_close = hist["Close"].iloc[-2]
        curr_close = hist["Close"].iloc[-1]
        change = curr_close - prev_close
        pct    = (change / prev_close) * 100
        vol    = hist["Volume"].iloc[-1]
        return {
            "price":  round(float(curr_close), 2),
            "change": round(float(change), 2),
            "pct":    round(float(pct), 2),
            "volume": int(vol),
        }
    except Exception as e:
        print(f"Error quick info {ticker}: {e}")
        return {}

#KPI Card
def kpi_card(ticker: str, info: dict) -> dbc.Col:
    name   = STOCKS.get(ticker, ticker)
    price  = info.get("price", "—")
    change = info.get("change", 0)
    pct    = info.get("pct", 0)
    vol    = info.get("volume", 0)

    pos    = change >= 0
    arrow  = "▲" if pos else "▼"
    color  = COLORS["green"] if pos else COLORS["red"]
    vol_str = f"{vol/1_000_000:.1f}M" if vol > 1_000_000 else f"{vol:,}"

    return dbc.Col(
        html.Div([
            html.Div([
                html.Span(ticker, style={"fontSize": "11px", "color": COLORS["accent"],
                                         "fontWeight": "700", "letterSpacing": "1.5px"}),
                html.Span(name,   style={"fontSize": "11px", "color": COLORS["subtext"],
                                         "marginLeft": "8px"}),
            ]),
            html.Div(f"${price:,.2f}" if isinstance(price, float) else "—",
                     style={"fontSize": "26px", "fontWeight": "700",
                            "color": COLORS["text"], "margin": "4px 0"}),
            html.Div([
                html.Span(f"{arrow} {abs(change):.2f} ({abs(pct):.2f}%)",
                          style={"color": color, "fontSize": "13px", "fontWeight": "600"}),
            ]),
            html.Div(f"Vol: {vol_str}",
                     style={"color": COLORS["subtext"], "fontSize": "11px", "marginTop": "4px"}),
        ], style={
            "background":    COLORS["card"],
            "border":        f"1px solid {COLORS['border']}",
            "borderRadius":  "10px",
            "padding":       "18px 20px",
            "transition":    "all 0.2s",
            "cursor":        "default",
        }),
        width=12, md=6, lg=4, xl=3,
        style={"marginBottom": "16px"}
    )

#Layout
app.layout = html.Div([

    dcc.Interval(id="interval", interval=60_000, n_intervals=0),  # refresh every 60s
    dcc.Store(id="store-period", data="1mo"),

    #Header
    html.Div([
        html.Div([
            html.H1("📈 Live Financial Dashboard",
                    style={"color": COLORS["text"], "fontSize": "22px",
                           "fontWeight": "700", "margin": 0}),
            html.Span(id="last-updated", style={"color": COLORS["subtext"], "fontSize": "12px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "20px"}),

        html.Div([
            html.Span("Auto-refresh: 60s", style={"color": COLORS["subtext"], "fontSize": "12px"}),
            html.Div(style={
                "width": "8px", "height": "8px", "borderRadius": "50%",
                "background": COLORS["green"], "display": "inline-block",
                "marginLeft": "6px", "animation": "pulse 2s infinite"
            }),
        ]),
    ], style={
        "background":   COLORS["card"],
        "border":       f"1px solid {COLORS['border']}",
        "padding":      "16px 24px",
        "display":      "flex",
        "justifyContent": "space-between",
        "alignItems":   "center",
        "marginBottom": "20px",
        "borderRadius": "10px",
    }),

    #KPI Cards
    html.H2("Market Overview", style={"color": COLORS["text"], "fontSize": "14px",
                                       "fontWeight": "600", "marginBottom": "12px",
                                       "textTransform": "uppercase", "letterSpacing": "1px"}),
    dbc.Row(id="kpi-cards", style={"marginBottom": "24px"}),

    #Main Chart + Controls
    html.Div([
        # Left controls
        html.Div([
            html.Label("Select Stock", style={"color": COLORS["subtext"], "fontSize": "12px",
                                               "fontWeight": "600", "marginBottom": "6px",
                                               "display": "block"}),
            dcc.Dropdown(
                id="stock-select",
                options=[{"label": f"{k} — {v}", "value": k} for k, v in STOCKS.items()],
                value="AAPL",
                clearable=False,
                style={"marginBottom": "16px"},
            ),
            html.Label("Time Period", style={"color": COLORS["subtext"], "fontSize": "12px",
                                              "fontWeight": "600", "marginBottom": "6px",
                                              "display": "block"}),
            dcc.RadioItems(
                id="period-select",
                options=[
                    {"label": "1W",  "value": "5d"},
                    {"label": "1M",  "value": "1mo"},
                    {"label": "3M",  "value": "3mo"},
                    {"label": "6M",  "value": "6mo"},
                    {"label": "1Y",  "value": "1y"},
                ],
                value="1mo",
                inline=False,
                style={"color": COLORS["text"]},
                labelStyle={"display": "block", "marginBottom": "6px",
                            "cursor": "pointer", "fontSize": "13px", "color": "#e6edf3"},
            ),
            html.Hr(style={"borderColor": COLORS["border"], "margin": "16px 0"}),
            html.Label("Chart Type", style={"color": COLORS["subtext"], "fontSize": "12px",
                                             "fontWeight": "600", "marginBottom": "6px",
                                             "display": "block"}),
            dcc.RadioItems(
                id="chart-type",
                options=[
                    {"label": "Candlestick", "value": "candle"},
                    {"label": "Line",        "value": "line"},
                ],
                value="candle",
                inline=False,
                style={"color": COLORS["text"]},
                labelStyle={"display": "block", "marginBottom": "6px",
                            "cursor": "pointer", "fontSize": "13px", "color": "#e6edf3"},
            ),
        ], style={
            "width": "180px",
            "flexShrink": "0",
            "background": COLORS["card"],
            "border":     f"1px solid {COLORS['border']}",
            "borderRadius": "10px",
            "padding":    "16px",
        }),

        # Main chart
        html.Div([
            dcc.Graph(id="main-chart", style={"height": "420px"},
                      config={"displayModeBar": True, "scrollZoom": True}),
        ], style={"flex": "1", "minWidth": 0}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

    #Comparison Chart
    html.Div([
        html.H2("Multi-Stock Comparison",
                style={"color": COLORS["text"], "fontSize": "14px",
                       "fontWeight": "600", "marginBottom": "12px",
                       "textTransform": "uppercase", "letterSpacing": "1px"}),
        dcc.Dropdown(
            id="compare-stocks",
            options=[{"label": f"{k} — {v}", "value": k} for k, v in STOCKS.items()],
            value=["AAPL", "MSFT", "NVDA"],
            multi=True,
            style={"marginBottom": "12px"},
        ),
        dcc.Graph(id="compare-chart", style={"height": "350px"},
                  config={"displayModeBar": True}),
    ], style={
        "background":   COLORS["card"],
        "border":       f"1px solid {COLORS['border']}",
        "borderRadius": "10px",
        "padding":      "20px",
        "marginBottom": "24px",
    }),

    #Top Movers
    html.Div([
        html.H2("Today's Movers",
                style={"color": COLORS["text"], "fontSize": "14px",
                       "fontWeight": "600", "marginBottom": "16px",
                       "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(id="movers-cards"),
    ], style={
        "background":   COLORS["card"],
        "border":       f"1px solid {COLORS['border']}",
        "borderRadius": "10px",
        "padding":      "20px",
    }),

    # Footer
    html.Div("Data: Yahoo Finance  •  Refreshes every 60s  •  Tomer Tirosh",
             style={"color": COLORS["subtext"], "fontSize": "11px",
                    "textAlign": "center", "marginTop": "24px", "paddingBottom": "16px"}),

], style={
    "background": COLORS["bg"],
    "minHeight":  "100vh",
    "padding":    "20px",
    "fontFamily": "'IBM Plex Mono', 'Fira Code', monospace",
})

#Callbacks

# 1. KPI Cards
@app.callback(
    Output("kpi-cards", "children"),
    Output("last-updated", "children"),
    Input("interval", "n_intervals"),
)
def update_kpi(n):
    cards = []
    for ticker in list(STOCKS.keys())[:8]:
        info = get_quick_info(ticker)
        if info:
            cards.append(kpi_card(ticker, info))
    now = datetime.now().strftime("%H:%M:%S")
    return cards, f"Last updated: {now}"


# 2. Main Chart
@app.callback(
    Output("main-chart", "figure"),
    Input("stock-select", "value"),
    Input("period-select", "value"),
    Input("chart-type", "value"),
    Input("interval", "n_intervals"),
)
def update_main_chart(ticker, period, chart_type, n):
    df = get_stock_data(ticker, period)
    name = STOCKS.get(ticker, ticker)

    fig = go.Figure()

    if df.empty:
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(color=COLORS["subtext"], size=16))
    elif chart_type == "candle":
        fig.add_trace(go.Candlestick(
            x=df["Date"], open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name=ticker,
            increasing_line_color=COLORS["green"],
            decreasing_line_color=COLORS["red"],
        ))
        # Volume bar chart on secondary y-axis
        fig.add_trace(go.Bar(
            x=df["Date"], y=df["Volume"], name="Volume",
            marker_color=COLORS["accent"], opacity=0.3,
            yaxis="y2",
        ))
        fig.update_layout(yaxis2=dict(
            overlaying="y", side="right",
            showgrid=False, showticklabels=False,
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["Close"],
            mode="lines", name=ticker,
            line=dict(color=COLORS["accent"], width=2),
            fill="tozeroy",
            fillcolor="rgba(88,166,255,0.08)",
        ))

    fig.update_layout(
        title=dict(text=f"{ticker}  ·  {name}", font=dict(color=COLORS["text"], size=14)),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        xaxis=dict(
            showgrid=True, gridcolor=COLORS["border"],
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"]),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


# 3. Comparison Chart (normalized to 100)
@app.callback(
    Output("compare-chart", "figure"),
    Input("compare-stocks", "value"),
    Input("period-select", "value"),
    Input("interval", "n_intervals"),
)
def update_compare(tickers, period, n):
    fig = go.Figure()
    palette = [COLORS["accent"], COLORS["green"], COLORS["yellow"],
               COLORS["red"], "#c9d1d9", "#a371f7", "#f78166"]

    if not tickers:
        return fig

    for i, ticker in enumerate(tickers):
        df = get_stock_data(ticker, period)
        if df.empty:
            continue
        normalized = (df["Close"] / df["Close"].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df["Date"], y=normalized,
            mode="lines", name=ticker,
            line=dict(color=palette[i % len(palette)], width=2),
        ))

    fig.add_hline(y=100, line_dash="dash", line_color=COLORS["border"])
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        xaxis=dict(showgrid=True, gridcolor=COLORS["border"]),
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"],
                   title="Normalized (base=100)"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    return fig


# 4. Movers Cards
@app.callback(
    Output("movers-cards", "children"),
    Input("interval", "n_intervals"),
)
def update_movers(n):
    data = []
    for ticker in STOCKS:
        info = get_quick_info(ticker)
        if info:
            info["ticker"] = ticker
            info["name"]   = STOCKS[ticker]
            data.append(info)

    if not data:
        return html.Div("Loading…", style={"color": COLORS["subtext"]})

    data.sort(key=lambda x: x.get("pct", 0), reverse=True)

    cards = []
    for d in data:
        pos   = d["pct"] >= 0
        color = COLORS["green"] if pos else COLORS["red"]
        bg    = "rgba(63,185,80,0.08)" if pos else "rgba(248,81,73,0.08)"
        arrow = "▲" if pos else "▼"
        cards.append(
            html.Div([
                html.Div([
                    html.Span(d["ticker"], style={"color": COLORS["accent"],
                                                   "fontWeight": "700", "fontSize": "13px"}),
                    html.Span(d["name"],   style={"color": COLORS["subtext"],
                                                   "fontSize": "11px", "marginLeft": "6px"}),
                ]),
                html.Div(f"${d['price']:,.2f}",
                         style={"color": COLORS["text"], "fontWeight": "700",
                                "fontSize": "18px", "margin": "4px 0"}),
                html.Div(f"{arrow} {abs(d['pct']):.2f}%",
                         style={"color": color, "fontWeight": "600", "fontSize": "13px"}),
            ], style={
                "background":   bg,
                "border":       f"1px solid {color}40",
                "borderRadius": "8px",
                "padding":      "14px 16px",
                "minWidth":     "140px",
                "flex":         "1",
            })
        )

    return html.Div(cards, style={
        "display": "flex", "flexWrap": "wrap", "gap": "12px",
    })


#Run
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
