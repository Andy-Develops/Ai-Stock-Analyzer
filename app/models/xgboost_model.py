"""
XGBoost Stock Prediction Model
================================
Predicts whether a stock will go UP or DOWN in the next 7 days.
Uses historical price data + technical indicators as features.
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from app.services.stock_data import get_stock_history


def build_features(ticker, period="2y"):
    """
    Create features (inputs) for the ML model from historical data.
    These are the patterns the model learns from.
    """
    df = get_stock_history(ticker, period=period)

    if df.empty:
        return pd.DataFrame()

    # Feature 1: Daily return (percent change day to day)
    df["daily_return"] = df["Close"].pct_change()

    # Feature 2: 7-day moving average
    df["ma_7"] = df["Close"].rolling(window=7).mean()

    # Feature 3: 21-day moving average
    df["ma_21"] = df["Close"].rolling(window=21).mean()

    # Feature 4: Price vs 7-day MA (above or below trend)
    df["price_vs_ma7"] = df["Close"] / df["ma_7"]

    # Feature 5: Price vs 21-day MA
    df["price_vs_ma21"] = df["Close"] / df["ma_21"]

    # Feature 6: Volatility (how much it swings over 7 days)
    df["volatility_7"] = df["daily_return"].rolling(window=7).std()

    # Feature 7: Volume change
    df["volume_change"] = df["Volume"].pct_change()

    # Feature 8: RSI (Relative Strength Index - overbought/oversold)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # TARGET: Will price be higher in 7 days? (1 = yes, 0 = no)
    df["target"] = (df["Close"].shift(-7) > df["Close"]).astype(int)

    # Drop rows with NaN values
    df.dropna(inplace=True)

    return df


def train_model(ticker, period="2y"):
    """
    Train the XGBoost model on historical data.
    Returns the trained model and its accuracy score.
    """
    df = build_features(ticker, period=period)

    if df.empty:
        return None, 0

    # Select features (what the model looks at)
    feature_cols = [
        "daily_return", "price_vs_ma7", "price_vs_ma21",
        "volatility_7", "volume_change", "rsi",
    ]

    X = df[feature_cols]
    y = df["target"]

    # Split: 80% training, 20% testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Train XGBoost
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    # Test accuracy
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    return model, accuracy


def predict_direction(ticker, period="2y"):
    """
    Predict if stock will go UP or DOWN in next 7 days.
    Returns prediction and confidence.
    """
    model, accuracy = train_model(ticker, period=period)

    if model is None:
        return {"prediction": "Unknown", "confidence": 0}

    # Get latest features for prediction
    df = build_features(ticker, period=period)
    feature_cols = [
        "daily_return", "price_vs_ma7", "price_vs_ma21",
        "volatility_7", "volume_change", "rsi",
    ]

    latest = df[feature_cols].iloc[-1:]
    prediction = model.predict(latest)[0]
    probability = model.predict_proba(latest)[0]

    return {
        "ticker": ticker.upper(),
        "prediction": "UP" if prediction == 1 else "DOWN",
        "confidence": round(float(max(probability)) * 100, 1),
        "model_accuracy": round(accuracy * 100, 1),
        "timeframe": "7 days",
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("   AI STOCK ANALYZER - Prediction Model Test")
    print("=" * 50)

    ticker = "AAPL"
    print(f"\nTraining model for {ticker}...")
    print("(Using 2 years of historical data)")
    print("-" * 50)

    # Run prediction
    result = predict_direction(ticker)

    if result["prediction"] != "Unknown":
        emoji = "📈" if result["prediction"] == "UP" else "📉"
        print(f"\n  {emoji} PREDICTION: {ticker} will go {result['prediction']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Model Accuracy: {result['model_accuracy']}%")
        print(f"  Timeframe: Next {result['timeframe']}")
    else:
        print("  Could not generate prediction")

    print("\n" + "=" * 50)
    print("Prediction Model is working!")
    print("=" * 50)
