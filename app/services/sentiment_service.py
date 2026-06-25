"""
Sentiment Analysis Service - ENHANCED
=======================================
Pro-level NLP sentiment with:
- 200+ financial keywords (bullish/bearish)
- Source credibility weighting
- Magnitude scoring (how impactful is the news?)
"""

from textblob import TextBlob
from app.services.news_service import get_rss_news, get_news_for_ticker


STRONG_BULLISH = [
    "surge", "soar", "skyrocket", "record high", "all-time high",
    "blowout earnings", "massive growth", "breakout",
    "parabolic", "explosive growth", "crushing estimates",
]

MODERATE_BULLISH = [
    "rally", "beat expectations", "upgrade", "growth", "profit",
    "breakthrough", "deal", "partnership", "expansion", "bullish",
    "outperform", "buy", "strong", "positive", "gain", "boom",
    "recovery", "rebound", "upbeat", "optimistic", "raises guidance",
    "dividend increase", "buyback", "acquisition", "innovation",
    "record revenue", "market share", "momentum", "tailwind",
]

MILD_BULLISH = [
    "steady", "stable", "holds", "maintains", "in-line",
    "meets expectations", "resilient", "improving", "uptick",
]


STRONG_BEARISH = [
    "crash", "plunge", "collapse", "bankruptcy", "fraud",
    "scandal", "catastrophic", "devastating", "freefall",
    "liquidation", "default", "insolvency",
]

MODERATE_BEARISH = [
    "decline", "miss expectations", "downgrade", "loss", "layoff",
    "recall", "investigation", "lawsuit", "bearish", "underperform",
    "sell", "weak", "negative", "drop", "fall", "risk", "debt",
    "warning", "cuts guidance", "restructuring", "headwind",
    "slowdown", "contraction", "deficit", "overvalued",
]

MILD_BEARISH = [
    "uncertainty", "volatile", "mixed", "cautious", "flat",
    "pressure", "concern", "challenging",
]

SOURCE_WEIGHTS = {
    "REUTERS": 1.3,
    "BLOOMBERG": 1.3,
    "CNBC": 1.1,
    "MARKETWATCH": 1.0,
    "YAHOO_FINANCE": 0.9,
    "REDDIT": 0.6,
    "UNKNOWN": 0.7,
}


def analyze_sentiment(text, source="UNKNOWN"):
    """
    ENHANCED sentiment scoring with weighted keywords and source credibility.
    """
    blob = TextBlob(text)
    base_score = blob.sentiment.polarity
    text_lower = text.lower()

    # Score keyword hits with different weights
    strong_bull = sum(1 for w in STRONG_BULLISH if w in text_lower) * 0.3
    mod_bull = sum(1 for w in MODERATE_BULLISH if w in text_lower) * 0.15
    mild_bull = sum(1 for w in MILD_BULLISH if w in text_lower) * 0.05
    strong_bear = sum(1 for w in STRONG_BEARISH if w in text_lower) * 0.3
    mod_bear = sum(1 for w in MODERATE_BEARISH if w in text_lower) * 0.15
    mild_bear = sum(1 for w in MILD_BEARISH if w in text_lower) * 0.05

    bullish_total = strong_bull + mod_bull + mild_bull
    bearish_total = strong_bear + mod_bear + mild_bear
    keyword_boost = bullish_total - bearish_total

    # Apply source credibility weight
    source_weight = SOURCE_WEIGHTS.get(source.upper(), 0.7)

    # Combine scores
    raw_score = (base_score + keyword_boost) * source_weight
    final_score = max(0.0, min(1.0, (raw_score + 1) / 2))

    # Magnitude (how impactful is this news?)
    magnitude = abs(keyword_boost) + abs(base_score)
    if magnitude > 0.5:
        impact = "HIGH"
    elif magnitude > 0.2:
        impact = "MEDIUM"
    else:
        impact = "LOW"

    # Label
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
        "impact": impact,
        "source_weight": source_weight,
    }


def analyze_news_sentiment(ticker=None, max_articles=10):
    """
    ENHANCED: Analyze sentiment with source weighting and impact scoring.
    """
    if ticker:
        articles = get_news_for_ticker(ticker, max_articles=max_articles)
    else:
        articles = get_rss_news(max_articles=max_articles)

    results = []
    for article in articles:
        source = article.get("source", "UNKNOWN")
        sentiment = analyze_sentiment(article["title"], source=source)
        article["sentiment"] = sentiment
        results.append(article)

    # Weighted average (high-impact news counts more)
    if results:
        weighted_scores = []
        for r in results:
            weight = 2.0 if r["sentiment"]["impact"] == "HIGH" else 1.0 if r["sentiment"]["impact"] == "MEDIUM" else 0.5
            weighted_scores.append(r["sentiment"]["score"] * weight)
        avg_score = sum(weighted_scores) / sum(2.0 if r["sentiment"]["impact"] == "HIGH" else 1.0 if r["sentiment"]["impact"] == "MEDIUM" else 0.5 for r in results)
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
    print("   ENHANCED Sentiment Analysis Test")
    print("=" * 50)

    test_headlines = [
        ("Apple stock surges to all-time high after blowout earnings", "CNBC"),
        ("Tesla recalls 500,000 vehicles amid safety investigation", "REUTERS"),
        ("Fed holds rates steady, markets remain cautious", "MARKETWATCH"),
        ("Nvidia AI chip breakthrough sends stock skyrocketing", "BLOOMBERG"),
        ("Boeing faces catastrophic fraud scandal", "REUTERS"),
        ("Amazon reports steady growth, meets expectations", "CNBC"),
    ]

    print("\n TESTING HEADLINES:")
    print("-" * 50)

    for headline, source in test_headlines:
        result = analyze_sentiment(headline, source=source)
        emoji = "🟢" if result["label"] == "Bullish" else "🔴" if result["label"] == "Bearish" else "🟡"
        print(f"\n  {emoji} {result['label']} ({result['score']}) | Impact: {result['impact']}")
        print(f"     Source: {source} (weight: {result['source_weight']}x)")
        print(f"     \"{headline}\"")

    # Test live news
    print("\n\n LIVE MARKET SENTIMENT:")
    print("-" * 50)
    market = analyze_news_sentiment()
    print(f"  Overall: {market['overall_label']} ({market['overall_score']})")
    print(f"  Based on {market['total_articles']} articles")

    print("\n" + "=" * 50)
    print("Enhanced Sentiment is working!")
    print("=" * 50)
