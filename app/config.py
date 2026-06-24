"""
AI Stock Analyzer - Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================
# API KEYS
# ============================================================

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# AWS Bedrock (alternative to OpenAI)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "StockAnalyzer/1.0")

# ============================================================
# AI SETTINGS
# ============================================================

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
OPENAI_MODEL = "gpt-4o-mini"
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

# ============================================================
# APP SETTINGS
# ============================================================

CACHE_EXPIRY_MINUTES = 15
NEWS_CACHE_EXPIRY_MINUTES = 10
DEFAULT_TICKER = "AAPL"
DEFAULT_PERIOD = "6mo"
DEFAULT_INTERVAL = "1d"
PREDICTION_DAYS = 30
TRAINING_PERIOD = "2y"
MAX_NEWS_ARTICLES = 20
NEWS_LOOKBACK_DAYS = 7

# Sentiment thresholds
SENTIMENT_BULLISH_THRESHOLD = 0.6
SENTIMENT_BEARISH_THRESHOLD = 0.4

# ============================================================
# RSS FEEDS (free, no key needed)
# ============================================================

RSS_FEEDS = {
    "reuters": "https://www.reutersagency.com/feed/?best-topics=business-finance",
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
    "marketwatch": "http://feeds.marketwatch.com/marketwatch/topstories/",
}

# ============================================================
# VALIDATION
# ============================================================

def validate_config():
    """Check that required API keys are set."""
    warnings = []

    if not FINNHUB_API_KEY:
        warnings.append("FINNHUB_API_KEY not set")
    if AI_PROVIDER == "openai" and not OPENAI_API_KEY:
        warnings.append("OPENAI_API_KEY not set")
    if not NEWSAPI_KEY:
        warnings.append("NEWSAPI_KEY not set")
    if not REDDIT_CLIENT_ID:
        warnings.append("REDDIT_CLIENT_ID not set")

    if warnings:
        print("Missing keys:")
        for w in warnings:
            print(f"  - {w}")
        print("Add them to your .env file")
    else:
        print("All API keys configured!")

    return len(warnings) == 0
