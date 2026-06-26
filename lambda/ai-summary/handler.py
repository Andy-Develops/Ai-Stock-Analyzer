"""
Lambda: /ai-summary endpoint
Returns AI-powered stock analysis
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.stock_data import get_daily_change
from app.services.news_service import get_rss_news
from app.models.xgboost_model import predict_direction
from app.services.ai_summary import analyze_stock, detect_divergence


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        body = event.get("queryStringParameters", {}) or {}

    ticker = body.get("ticker", "AAPL").upper()

    # Gather data
    price_data = get_daily_change(ticker)
    news = get_rss_news(max_articles=10)
    headlines = [a["title"] for a in news]
    prediction = predict_direction(ticker)
    indicators = prediction.get("indicators", {})

    # AI analysis
    analysis = analyze_stock(ticker, price_data, headlines, indicators)

    # Divergence detection
    divergence = detect_divergence(prediction, analysis)

    response = {
        "ticker": ticker,
        "analysis": analysis,
        "divergence": divergence,
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response),
    }
