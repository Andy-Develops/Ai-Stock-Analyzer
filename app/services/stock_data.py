"""
Stock Data Service
==================
Pulls real-time and historical stock data from Yahoo Finance.
No API key needed - completely free!
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time


def get_stock_history(ticker, period="6mo", interval="1d"):
    """
    Get historical price data using yf.download (more reliable).
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        data.reset_index(inplace=True)
        if hasattr(data.columns, 'levels'):
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        return data
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return pd.DataFrame()


def get_daily_change(ticker):
    """
    Get today's price change.
    """
    try:
        data = yf.download(ticker, period="5d", progress=False)

        if data.empty or len(data) < 2:
            return {"dollar_change": 0, "percent_change": 0}

        current = float(data["Close"].iloc[-1].iloc[0]) if hasattr(data["Close"].iloc[-1], 'iloc') else float(data["Close"].iloc[-1])
        previous = float(data["Close"].iloc[-2].iloc[0]) if hasattr(data["Close"].iloc[-2], 'iloc') else float(data["Close"].iloc[-2])

        dollar_change = current - previous
        percent_change = (dollar_change / previous) * 100

        return {
            "current_price": round(current, 2),
            "previous_close": round(previous, 2),
            "dollar_change": round(dollar_change, 2),
            "percent_change": round(percent_change, 2),
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"dollar_change": 0, "percent_change": 0}


def get_moving_averages(ticker, period="1y"):
    """
    Calculate moving averages (used for trend analysis).
    """
    history = get_stock_history(ticker, period=period)

    if history.empty:
        return history

    history["MA_20"] = history["Close"].rolling(window=20).mean()
    history["MA_50"] = history["Close"].rolling(window=50).mean()
    history["MA_200"] = history["Close"].rolling(window=200).mean()

    return history


def get_stock_info(ticker):
    """
    Get basic info about a stock.
    Uses download() first (reliable), then tries .info for extras.
    """
    try:
        data = yf.download(ticker, period="5d", progress=False)

        if data.empty:
            return {"ticker": ticker.upper(), "error": "No data found"}

        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else data.iloc[-1]

        current_price = float(latest["Close"].iloc[0]) if hasattr(latest["Close"], 'iloc') else float(latest["Close"])
        prev_price = float(prev["Close"].iloc[0]) if hasattr(prev["Close"], 'iloc') else float(prev["Close"])
        high = float(latest["High"].iloc[0]) if hasattr(latest["High"], 'iloc') else float(latest["High"])
        low = float(latest["Low"].iloc[0]) if hasattr(latest["Low"], 'iloc') else float(latest["Low"])
        open_price = float(latest["Open"].iloc[0]) if hasattr(latest["Open"], 'iloc') else float(latest["Open"])
        volume = int(latest["Volume"].iloc[0]) if hasattr(latest["Volume"], 'iloc') else int(latest["Volume"])

        result = {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "previous_close": round(prev_price, 2),
            "day_high": round(high, 2),
            "day_low": round(low, 2),
            "open": round(open_price, 2),
            "volume": volume,
            "name": ticker.upper(),
            "sector": "N/A",
            "market_cap": 0,
        }

        # Try to get extra info (might rate limit, thats ok)
        time.sleep(1)
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            result["name"] = info.get("longName", ticker.upper())
            result["sector"] = info.get("sector", "N/A")
            result["market_cap"] = info.get("marketCap", 0)
            result["pe_ratio"] = info.get("trailingPE", "N/A")
            result["52_week_high"] = info.get("fiftyTwoWeekHigh", 0)
            result["52_week_low"] = info.get("fiftyTwoWeekLow", 0)
        except:
            pass

        return result

    except Exception as e:
        print(f"Error fetching info for {ticker}: {e}")
        return {"ticker": ticker.upper(), "error": str(e)}


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("   AI STOCK ANALYZER - Data Service Test")
    print("=" * 50)

    ticker = "AAPL"
    print(f"\nFetching data for: {ticker}")
    print("-" * 50)

    # Test 1: History (most reliable)
    print("\n LAST 5 DAYS:")
    history = get_stock_history(ticker, period="5d")
    if not history.empty:
        print(history.tail().to_string(index=False))
    else:
        print("  Could not fetch history")

    # Test 2: Daily change
    print("\n TODAY'S MOVEMENT:")
    change = get_daily_change(ticker)
    direction = "UP" if change["dollar_change"] >= 0 else "DOWN"
    print(f"  {direction} ${abs(change['dollar_change'])} ({change['percent_change']}%)")

    # Test 3: Moving averages
    print("\n MOVING AVERAGES (last row):")
    ma = get_moving_averages(ticker, period="1y")
    if not ma.empty:
        last = ma.iloc[-1]
        print(f"  20-day MA: ${round(float(last.get('MA_20', 0)), 2)}")
        print(f"  50-day MA: ${round(float(last.get('MA_50', 0)), 2)}")
        print(f"  200-day MA: ${round(float(last.get('MA_200', 0)), 2)}")

    print("\n" + "=" * 50)
    print("Stock Data Service is working!")
    print("=" * 50)
