"""
Lambda: /analyze endpoint
Returns stock price data + ML prediction + technical indicators
"""

import json
import sys
import os

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.stock_data import get_daily_change, get_stock_history
from app.models.xgboost_model import predict_direction


def lambda_handler(event, context):
    """
    API Gateway calls this function.
    Expects: { "ticker": "AAPL" }
    """
    # Get ticker from request
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        body = event.get("queryStringParameters", {}) or {}

    ticker = body.get("ticker", "AAPL").upper()

    # Get price data
    price_data = get_daily_change(ticker)

    # Get ML prediction
    prediction = predict_direction(ticker)

    # Build response
    response = {
        "ticker": ticker,
        "price": price_data,
        "prediction": {
            "direction": prediction.get("prediction"),
            "confidence": prediction.get("confidence"),
            "model_accuracy": prediction.get("model_accuracy"),
            "timeframe": prediction.get("timeframe"),
            "indicators": prediction.get("indicators", {}),
            "top_features": prediction.get("top_features", []),
        },
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response),
    }
