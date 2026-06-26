"""
Lambda: /market-outlook endpoint
Returns AI market outlook + news-to-stock connections
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.services.news_service import get_rss_news
from app.services.ai_summary import get_market_outlook, connect_news_to_stocks


def lambda_handler(event, context):
    # Get latest news
    news = get_rss_news(max_articles=15)
    headlines = [a["title"] for a in news]

    # AI analysis
    outlook = get_market_outlook(headlines)
    connections = connect_news_to_stocks(headlines)

    response = {
        "outlook": outlook,
        "connections": connections,
        "headlines_analyzed": len(headlines),
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response),
    }
