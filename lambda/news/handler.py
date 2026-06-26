"""
Lambda: /news endpoint
Returns news headlines with sentiment scoring
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.news_service import get_rss_news, get_news_for_ticker
from app.services.sentiment_service import analyze_news_sentiment


def lambda_handler(event, context):
    """
    API Gateway calls this function.
    Expects: { "ticker": "AAPL" } or empty for market news
    """
    try:
        body = json.loads(event.get("body", "{}"))
    except:
        body = event.get("queryStringParameters", {}) or {}

    ticker = body.get("ticker", None)

    # Get sentiment-scored news
    sentiment_data = analyze_news_sentiment(ticker=ticker, max_articles=10)

    # Clean articles for JSON response
    articles = []
    for article in sentiment_data.get("articles", []):
        articles.append({
            "title": article.get("title"),
            "source": article.get("source"),
            "link": article.get("link"),
            "sentiment": article.get("sentiment"),
        })

    response = {
        "ticker": ticker or "MARKET",
        "overall_score": sentiment_data.get("overall_score"),
        "overall_label": sentiment_data.get("overall_label"),
        "total_articles": sentiment_data.get("total_articles"),
        "articles": articles,
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response),
    }
