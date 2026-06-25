"""
XGBoost Stock Prediction Model - ENHANCED
==========================================
Pro-level technical indicators:
- RSI (14), MACD (12,26,9), Bollinger Bands (20,2)
- ATR (14), OBV, Multi-timeframe MAs (9,21,50,200)
- Volume analysis, momentum scoring
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from app.services.stock_data import get_stock_history


def calculate_rsi(series, period=14):
    """RSI - Relative Strength Index (standard: 14 period)"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD - Moving Average Convergence Divergence
    Standard settings: 12 fast, 26 slow, 9 signal
    """
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger(series, period=20, std_dev=2):
    """Bollinger Bands - Standard: 20 period, 2 std deviations"""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    # Percent B: where price is relative to bands (0=lower, 1=upper)
    percent_b = (series - lower) / (upper - lower)
    return upper, middle, lower, percent_b


def calculate_atr(high, low, close, period=14):
    """ATR - Average True Range (volatility measure)"""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def build_features(ticker, period="5y"):
    """
    ENHANCED feature engineering with pro-level indicators.
    Uses 5 years of data for better pattern recognition.
    """
    df = get_stock_history(ticker, period=period)

    if df.empty:
        return pd.DataFrame()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # === MOVING AVERAGES (pro standard timeframes) ===
    df["ma_9"] = close.rolling(window=9).mean()
    df["ma_21"] = close.rolling(window=21).mean()
    df["ma_50"] = close.rolling(window=50).mean()
    df["ma_200"] = close.rolling(window=200).mean()

    # Price vs MAs (above = bullish, below = bearish)
    df["price_vs_ma9"] = close / df["ma_9"]
    df["price_vs_ma21"] = close / df["ma_21"]
    df["price_vs_ma50"] = close / df["ma_50"]
    df["price_vs_ma200"] = close / df["ma_200"]

    # MA crossovers (golden cross / death cross signals)
    df["ma9_vs_ma21"] = df["ma_9"] / df["ma_21"]
    df["ma50_vs_ma200"] = df["ma_50"] / df["ma_200"]

    # === RSI (14 period - standard) ===
    df["rsi"] = calculate_rsi(close, period=14)

    # === MACD (12, 26, 9 - standard) ===
    macd_line, signal_line, histogram = calculate_macd(close, 12, 26, 9)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_histogram"] = histogram

    # === BOLLINGER BANDS (20 period, 2 std dev) ===
    upper, middle, lower, percent_b = calculate_bollinger(close, 20, 2)
    df["bollinger_pct_b"] = percent_b
    df["bollinger_width"] = (upper - lower) / middle

    # === ATR (14 period - volatility) ===
    df["atr"] = calculate_atr(high, low, close, period=14)
    df["atr_percent"] = df["atr"] / close * 100

    # === VOLUME ANALYSIS ===
    df["volume_ma_20"] = volume.rolling(window=20).mean()
    df["volume_ratio"] = volume / df["volume_ma_20"]
    # OBV (On Balance Volume)
    df["obv"] = (np.sign(close.diff()) * volume).cumsum()
    df["obv_ma"] = df["obv"].rolling(window=20).mean()
    df["obv_signal"] = df["obv"] / df["obv_ma"]

    # === MOMENTUM ===
    df["daily_return"] = close.pct_change()
    df["return_3d"] = close.pct_change(periods=3)
    df["return_5d"] = close.pct_change(periods=5)
    df["return_10d"] = close.pct_change(periods=10)
    df["volatility_14"] = df["daily_return"].rolling(window=14).std()

    # === TARGET: Will price be higher in 7 days? ===
    df["target"] = (close.shift(-7) > close).astype(int)

    # Drop NaN rows
    df.dropna(inplace=True)

    return df


def train_model(ticker, period="5y"):
    """
    ENHANCED XGBoost training with optimized hyperparameters.
    Pro settings: more trees, controlled depth, lower learning rate.
    """
    df = build_features(ticker, period=period)

    if df.empty:
        return None, 0, []

    # All features the model uses
    feature_cols = [
        "price_vs_ma9", "price_vs_ma21", "price_vs_ma50", "price_vs_ma200",
        "ma9_vs_ma21", "ma50_vs_ma200",
        "rsi", "macd", "macd_signal", "macd_histogram",
        "bollinger_pct_b", "bollinger_width",
        "atr_percent",
        "volume_ratio", "obv_signal",
        "daily_return", "return_3d", "return_5d", "return_10d",
        "volatility_14",
    ]

    X = df[feature_cols]
    y = df["target"]

    # Split: 80% training, 20% testing (no shuffle - time series!)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # ENHANCED XGBoost settings (pro-tuned)
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Test accuracy
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    # Feature importance (which indicators matter most)
    importance = dict(zip(feature_cols, model.feature_importances_))
    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]

    return model, accuracy, top_features


def predict_direction(ticker, period="5y"):
    """
    ENHANCED prediction with multiple timeframes and feature importance.
    """
    model, accuracy, top_features = train_model(ticker, period=period)

    if model is None:
        return {"prediction": "Unknown", "confidence": 0}

    # Get latest features
    df = build_features(ticker, period=period)
    feature_cols = [
        "price_vs_ma9", "price_vs_ma21", "price_vs_ma50", "price_vs_ma200",
        "ma9_vs_ma21", "ma50_vs_ma200",
        "rsi", "macd", "macd_signal", "macd_histogram",
        "bollinger_pct_b", "bollinger_width",
        "atr_percent",
        "volume_ratio", "obv_signal",
        "daily_return", "return_3d", "return_5d", "return_10d",
        "volatility_14",
    ]

    latest = df[feature_cols].iloc[-1:]
    prediction = model.predict(latest)[0]
    probability = model.predict_proba(latest)[0]

    # Get current indicator values for context
    latest_row = df.iloc[-1]

    return {
        "ticker": ticker.upper(),
        "prediction": "UP" if prediction == 1 else "DOWN",
        "confidence": round(float(max(probability)) * 100, 1),
        "model_accuracy": round(accuracy * 100, 1),
        "timeframe": "7 days",
        "top_features": top_features,
        "indicators": {
            "rsi": round(float(latest_row["rsi"]), 1),
            "macd_histogram": round(float(latest_row["macd_histogram"]), 4),
            "bollinger_pct_b": round(float(latest_row["bollinger_pct_b"]), 3),
            "volume_ratio": round(float(latest_row["volume_ratio"]), 2),
            "atr_percent": round(float(latest_row["atr_percent"]), 2),
        },
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("   AI STOCK ANALYZER - ENHANCED Prediction Test")
    print("=" * 50)

    ticker = "AAPL"
    print(f"\nTraining ENHANCED model for {ticker}...")
    print("(Using 5 years of data + pro indicators)")
    print("-" * 50)

    # Run prediction
    result = predict_direction(ticker)

    if result["prediction"] != "Unknown":
        emoji = "📈" if result["prediction"] == "UP" else "📉"
        print(f"\n  {emoji} PREDICTION: {ticker} will go {result['prediction']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Model Accuracy: {result['model_accuracy']}%")
        print(f"  Timeframe: Next {result['timeframe']}")

        print(f"\n  📊 CURRENT INDICATORS:")
        indicators = result["indicators"]
        print(f"     RSI: {indicators['rsi']} {'(Overbought!)' if indicators['rsi'] > 70 else '(Oversold!)' if indicators['rsi'] < 30 else '(Normal)'}")
        print(f"     MACD Histogram: {indicators['macd_histogram']} {'(Bullish momentum)' if indicators['macd_histogram'] > 0 else '(Bearish momentum)'}")
        print(f"     Bollinger %B: {indicators['bollinger_pct_b']} {'(Near upper band)' if indicators['bollinger_pct_b'] > 0.8 else '(Near lower band)' if indicators['bollinger_pct_b'] < 0.2 else '(Mid range)'}")
        print(f"     Volume Ratio: {indicators['volume_ratio']}x average")
        print(f"     ATR%: {indicators['atr_percent']}% daily volatility")

        print(f"\n  🏆 TOP 5 FEATURES (what matters most):")
        for feature, importance in result["top_features"]:
            bar = "█" * int(importance * 50)
            print(f"     {feature:20s} {bar} ({round(importance*100,1)}%)")
    else:
        print("  Could not generate prediction")

    print("\n" + "=" * 50)
    print("Enhanced Prediction Model is working!")
    print("=" * 50)
