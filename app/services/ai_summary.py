"""
AI Summary Service
==================
Uses OpenAI GPT to generate intelligent stock analysis.
This is the BRAIN - it connects news to stocks and explains impact.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"


def analyze_stock(ticker, price_data, news_headlines):
    """
    AI generates a full stock analysis based on price data and news.
    This is the magic - it connects everything together.
    """
    prompt = f"""You are a professional stock analyst. Analyze {ticker} based on this data:

PRICE DATA:
- Current Price: ${price_data.get('current_price', 'N/A')}
- Daily Change: ${price_data.get('dollar_change', 'N/A')} ({price_data.get('percent_change', 'N/A')}%)
- Previous Close: ${price_data.get('previous_close', 'N/A')}

RECENT NEWS HEADLINES:
{chr(10).join(f'- {h}' for h in news_headlines[:10])}

Provide a brief analysis (3-4 sentences) covering:
1. What the news means for this stock
2. Whether sentiment is bullish or bearish
3. Key risk or opportunity to watch

Be concise and actionable. Speak like a financial advisor."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis unavailable: {e}"


def connect_news_to_stocks(headlines):
    """
    THE MAGIC FUNCTION - AI reads news and tells you which stocks
    are affected and how. This is what makes the app smart.
    """
    prompt = f"""You are a financial analyst. Read these headlines and identify:
1. Which stock tickers are affected
2. Whether the impact is Bullish or Bearish
3. Brief explanation why

HEADLINES:
{chr(10).join(f'- {h}' for h in headlines[:10])}

Respond in this format for each relevant headline:
TICKER: [symbol] | IMPACT: [Bullish/Bearish] | WHY: [one sentence]

Only include headlines that clearly affect specific stocks."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI connection unavailable: {e}"


def get_market_outlook(headlines):
    """
    AI gives a quick overall market outlook based on today's news.
    """
    prompt = f"""Based on these financial headlines, give a 2-3 sentence
market outlook for today. Are markets likely bullish or bearish?
What sectors should investors watch?

HEADLINES:
{chr(10).join(f'- {h}' for h in headlines[:10])}

Be concise and professional."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI outlook unavailable: {e}"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    from app.services.news_service import get_rss_news
    from app.services.stock_data import get_daily_change

    print("=" * 50)
    print("   AI STOCK ANALYZER - AI Brain Test")
    print("=" * 50)

    # Get real data
    ticker = "AAPL"
    print(f"\nGathering data for {ticker}...")

    price_data = get_daily_change(ticker)
    news = get_rss_news(max_articles=10)
    headlines = [a["title"] for a in news]

    # Test 1: Stock Analysis
    print("\n AI STOCK ANALYSIS:")
    print("-" * 50)
    analysis = analyze_stock(ticker, price_data, headlines)
    print(f"  {analysis}")

    # Test 2: Connect news to stocks
    print("\n\n NEWS → STOCK CONNECTIONS:")
    print("-" * 50)
    connections = connect_news_to_stocks(headlines)
    print(f"  {connections}")

    # Test 3: Market outlook
    print("\n\n MARKET OUTLOOK:")
    print("-" * 50)
    outlook = get_market_outlook(headlines)
    print(f"  {outlook}")

    print("\n" + "=" * 50)
    print("AI Brain is working!")
    print("=" * 50)
