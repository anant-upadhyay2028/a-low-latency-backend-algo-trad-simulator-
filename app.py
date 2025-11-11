from flask import Flask, jsonify, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np
import random

app = Flask(__name__)

# NSE universe
INDIA = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS",
    "BHARTIARTL.NS","ITC.NS","ASIANPAINT.NS","HINDUNILVR.NS","TATAMOTORS.NS",
    "TITAN.NS","SUNPHARMA.NS","MARUTI.NS","M&M.NS","DRREDDY.NS","ONGC.NS"
]

def get_prices(stocks, days):
    df = yf.download(
        stocks, period=f"{days+150}d", interval="1d",
        auto_adjust=True, group_by="ticker", progress=False
    )
    close = {}
    for s in stocks:
        try:
            close[s] = df[s]["Close"]
        except Exception:
            pass
    return pd.DataFrame(close).dropna()

def run_backtest(n=8, days=60, capital=10000.0, seed=42):
    # choose tickers by seed (so changing seed changes basket)
    rng = random.Random(seed)
    picks = rng.sample(INDIA, k=min(n, len(INDIA)))

    prices = get_prices(picks, days)
    if prices.empty:
        return None

    # indicators & signals (SMA cross)
    sma10 = prices.rolling(10).mean()
    sma30 = prices.rolling(30).mean()
    signal = (sma10 > sma30).astype(int)

    # daily portfolio return = equal-weighted active signals (T-1)
    returns = prices.pct_change()
    daily_ret = (signal.shift(1) * returns).mean(axis=1)

    equity = (1.0 + daily_ret.fillna(0)).cumprod() * capital

    # CLEAN for JSON
    equity = equity.fillna(method="ffill").fillna(method="bfill")
    equity = equity.replace([np.inf, -np.inf, np.nan], 0)

    total_return = round((equity.iloc[-1] / capital - 1) * 100, 2)
    sharpe = round((daily_ret.mean() / (daily_ret.std() + 1e-12)) * np.sqrt(252), 2)
    mdd = round((equity / equity.cummax() - 1).min() * 100, 2)

    latest = signal.iloc[-1].replace({1: "LONG", 0: "FLAT"}).to_dict()

    return {
        "tickers": picks,
        "dates": equity.index.strftime("%Y-%m-%d").tolist(),
        "values": equity.values.tolist(),
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "signals": latest
    }

@app.route("/api/portfolio")
def api_portfolio():
    # read query params (with defaults)
    n = int(request.args.get("n", 8))
    days = int(request.args.get("days", 60))
    amount = float(request.args.get("amount", 10000))
    seed = int(request.args.get("seed", 42))

    result = run_backtest(n=n, days=days, capital=amount, seed=seed)
    if result is None:
        return jsonify({"error": "Data unavailable"}), 400
    return jsonify(result)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
