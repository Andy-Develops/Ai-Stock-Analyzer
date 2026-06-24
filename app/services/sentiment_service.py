"""
Sentiment Analysis Service
===========================
Scores news headlines as Bullish, Bearish, or Neutral.
Uses TextBlob for basic sentiment (free, no API key).
"""

from textblob import TextBlob
from app.services.news_service import get_rss_news, get_news_for_ticker


BULLISH_WORDS = [
    "surge", "soar", "rally", "record high", "beat expectations",
    "upgrade", "growth", "profit", "breakthrough", "deal",
    "partnership", "expansion", "bullish", "outperform", "buy",
    "strong", "positive", "gain", "boom", "skyrocket",
]

BEARISH_WORDS = [
    "crash", "plunge", "decline", "miss expectations", "downgrade",
    "loss", "layoff", "recall", "investigation", "lawsuit",
    "bearish", "underperform", "sell", "weak", "negative",
    "drop", "fall", "risk", "debt", "bankruptcy",
]


def analyze_sentiment(text):
    """
    Score a single piece of text for sentiment.
    Returns score (0-1), label, and confidence.
    """
    blob = TextBlob(text)
    base_score = blob.sentiment.polarity

    text_lower = text.lower()
    bullish_hits = sum(1 for word in BULLISH_WORDS if word in text_lower)
    bearish_hits = sum(1 for word in BEARISH_WORDS if word in text_lower)

    keyword_boost = (bullish_hits - bearish_hits) * 0.15
    raw_score = base_score + keyword_boost
    final_score = max(0.0, min(1.0, (raw_score + 1) / 2))

    if final_score >= 0.6:
        label = "Bullish"
    elif final_score <= 0.4:
        label = "Bearish"
    else:
        label = "Neutral"

    confidence = abs(final_score - 0.5) * 2

    return {
        "score": round(final_score, 3),
        "label": label,
        "confidence": round(confidence, 3),
    }


def analyze_news_sentiment(ticker=None, max_articles=10):
    """
    Analyze sentiment for multiple news articles.
    If ticker provided, only analyzes news for that stock.
    """
    if ticker:
        articles = get_news_for_ticker(ticker, max_articles=max_articles)
    else:
        articles = get_rss_news(max_articles=max_articles)

    results = []
    for article in articles:
        sentiment = analyze_sentiment(article["title"])
        article["sentiment"] = sentiment
        results.append(article)

    # Calculate overall sentiment score
    if results:
        avg_score = sum(r["sentiment"]["score"] for r in results) / len(results)
    else:
        avg_score = 0.5

    if avg_score >= 0.6:
        overall_label = "Bullish"
    elif avg_score <= 0.4:
        overall_label = "Bearish"
    else:
        overall_label = "Neutral"

    return {
        "ticker": ticker or "MARKET",
        "overall_score": round(avg_score, 3),
        "overall_label": overall_label,
        "total_articles": len(results),
        "articles": results,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("   AI STOCK ANALYZER - Sentiment Test")
    print("=" * 50)

    # Test 1: Single headlines
    print("\n TESTING INDIVIDUAL HEADLINES:")
    print("-" * 50)

    test_headlines = [
        "Apple reports record iPhone sales, stock surges",
        "Tesla recalls 500,000 vehicles over safety concerns",
        "Fed holds interest rates steady, markets unchanged",
        "Nvidia breakthrough AI chip sends stock soaring",
        "Boeing faces new investigation after crash report",
    ]

    for headline in test_headlines:
        result = analyze_sentiment(headline)
        emoji = "🟢" if result["label"] == "Bullish" else "🔴" if result["label"] == "Bearish" else "🟡"
        print(f"\n  {emoji} {result['label']} ({result['score']})")
        print(f"     \"{headline}\"")

    # Test 2: Analyze live news
    print("\n\n LIVE MARKET SENTIMENT:")
    print("-" * 50)
    market = analyze_news_sentiment()
    print(f"  Overall: {market['overall_label']} ({market['overall_score']})")
    print(f"  Based on {market['total_articles']} articles")

    print("\n" + "=" * 50)
    print("Sentiment Service is working!")
    print("=" * 50)
    print("-" * 50)
    market = analyze_news_sentiment()
    print(f"  Overall: {market['overall_label']} ({market['overall_score']})")
    print(f"  Based on {market['total_articles']} articles")

    print("\n" + "=" * 50)
    print("Sentiment Service is working!")
    print("=" * 50)
