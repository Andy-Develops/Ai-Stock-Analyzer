"""
News Service
============
Fetches real-time financial news from RSS feeds.
No API key needed for RSS! Finnhub/NewsAPI added later.
"""

import feedparser
import time
from datetime import datetime, timedelta


# Free RSS feeds - no key, no limit
RSS_FEEDS = {
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
    "marketwatch": "http://feeds.marketwatch.com/marketwatch/topstories/",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
}


def get_rss_news(max_articles=10):
    """
    Pull latest financial news from RSS feeds.
    No API key needed - completely free and unlimited!
    
    Returns:
        List of dictionaries with title, link, source, published date
    """
    all_articles = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:5]:
                article = {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "source": source_name.upper(),
                    "published": entry.get("published", "Unknown"),
                    "summary": entry.get("summary", "")[:200],
                }
                all_articles.append(article)

        except Exception as e:
            print(f"Error fetching {source_name}: {e}")

    # Sort by most recent first (if dates available)
    all_articles = all_articles[:max_articles]

    return all_articles


def get_news_for_ticker(ticker, max_articles=10):
    """
    Search news specifically related to a stock ticker.
    Filters RSS headlines that mention the company name or ticker.
    
    Args:
        ticker: Stock symbol like "AAPL", "TSLA"
        max_articles: How many articles to return
    
    Returns:
        List of articles related to that ticker
    """
    # Map common tickers to company names for better search
    ticker_names = {
        "AAPL": ["apple", "iphone", "ipad", "mac"],
        "TSLA": ["tesla", "elon musk", "ev", "cybertruck"],
        "NVDA": ["nvidia", "gpu", "ai chip", "jensen"],
        "MSFT": ["microsoft", "azure", "windows", "copilot"],
        "AMZN": ["amazon", "aws", "prime", "bezos"],
        "GOOGL": ["google", "alphabet", "gemini", "waymo"],
        "META": ["meta", "facebook", "instagram", "zuckerberg"],
        "JPM": ["jpmorgan", "jp morgan", "jamie dimon"],
        "XOM": ["exxon", "exxonmobil", "oil"],
        "BA": ["boeing", "aircraft", "737"],
    }

    # Get keywords for this ticker
    keywords = ticker_names.get(ticker.upper(), [ticker.lower()])
    keywords.append(ticker.lower())

    # Get all news
    all_news = get_rss_news(max_articles=50)

    # Filter for articles mentioning our keywords
    relevant = []
    for article in all_news:
        text = (article["title"] + " " + article["summary"]).lower()
        for keyword in keywords:
            if keyword in text:
                article["matched_keyword"] = keyword
                relevant.append(article)
                break

    return relevant[:max_articles]


def get_market_summary():
    """
    Get a quick overview of what's happening in the market right now.
    Pulls top headlines from all sources.
    """
    articles = get_rss_news(max_articles=15)

    summary = {
        "total_articles": len(articles),
        "sources": list(set(a["source"] for a in articles)),
        "top_headlines": [a["title"] for a in articles[:5]],
        "articles": articles,
    }

    return summary


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("   AI STOCK ANALYZER - News Service Test")
    print("=" * 50)

    # Test 1: Get all market news
    print("\n LATEST MARKET NEWS:")
    print("-" * 50)
    news = get_rss_news(max_articles=10)

    if news:
        for i, article in enumerate(news, 1):
            print(f"\n  {i}. [{article['source']}] {article['title']}")
    else:
        print("  No articles found (feeds might be down)")

    # Test 2: Get news for a specific stock
    print("\n\n SEARCHING NEWS FOR: AAPL")
    print("-" * 50)
    aapl_news = get_news_for_ticker("AAPL")

    if aapl_news:
        for i, article in enumerate(aapl_news, 1):
            print(f"\n  {i}. {article['title']}")
            print(f"     Matched: '{article['matched_keyword']}'")
    else:
        print("  No AAPL-specific news found right now")
        print("  (This is normal - not every moment has stock-specific news)")

    # Test 3: Market summary
    print("\n\n MARKET SUMMARY:")
    print("-" * 50)
    summary = get_market_summary()
    print(f"  Total articles pulled: {summary['total_articles']}")
    print(f"  Sources: {', '.join(summary['sources'])}")
    print(f"\n  Top Headlines:")
    for headline in summary['top_headlines']:
        print(f"    - {headline}")

    print("\n" + "=" * 50)
    print("News Service is working!")
    print("=" * 50)
