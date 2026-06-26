"""
AI Summary Service - ENHANCED
==============================
GPT-4o-mini powered stock analysis with pro-level prompts.
Thinks like a Wall Street analyst.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

# System prompt - this makes the AI think like a pro analyst
SYSTEM_PROMPT = """You are a senior Wall Street equity analyst with 20 years of experience.
You specialize in technical analysis, fundamental analysis, and market sentiment.

Your analysis style:
- Data-driven, never speculative without evidence
- You identify specific catalysts (what could move the stock)
- You assess risk on a 1-10 scale (10 = extremely risky)
- You consider macro factors (Fed policy, sector rotation, geopolitics)
- You give clear actionable insights, not vague statements
- You always mention timeframe for your thesis
- You flag when sentiment contradicts technicals (divergence)

Important rules:
- Never guarantee returns
- Always mention key risks
- Be specific with numbers when possible
- If news is mixed, say so clearly
"""


def analyze_stock(ticker, price_data, news_headlines, indicators=None):
    """
    ENHANCED: Full Wall Street-style stock analysis.
    Now includes technical indicators and risk scoring.
    """
    indicators_text = ""
    if indicators:
        indicators_text = f"""
TECHNICAL INDICATORS:
- RSI (14): {indicators.get('rsi', 'N/A')} {'(OVERBOUGHT >70)' if indicators.get('rsi', 50) > 70 else '(OVERSOLD <30)' if indicators.get('rsi', 50) < 30 else '(Normal range)'}
- MACD Histogram: {indicators.get('macd_histogram', 'N/A')} {'(Bullish momentum)' if indicators.get('macd_histogram', 0) > 0 else '(Bearish momentum)'}
- Bollinger %B: {indicators.get('bollinger_pct_b', 'N/A')} {'(Near upper band - stretched)' if indicators.get('bollinger_pct_b', 0.5) > 0.8 else '(Near lower band - compressed)' if indicators.get('bollinger_pct_b', 0.5) < 0.2 else '(Mid range)'}
- Volume vs Average: {indicators.get('volume_ratio', 'N/A')}x
- ATR%: {indicators.get('atr_percent', 'N/A')}% daily volatility
"""

    prompt = f"""Analyze {ticker} stock with this data:

PRICE DATA:
- Current Price: ${price_data.get('current_price', 'N/A')}
- Daily Change: ${price_data.get('dollar_change', 'N/A')} ({price_data.get('percent_change', 'N/A')}%)
- Previous Close: ${price_data.get('previous_close', 'N/A')}
{indicators_text}
RECENT NEWS:
{chr(10).join(f'- {h}' for h in news_headlines[:10])}

Provide your analysis in this EXACT format:
VERDICT: [BULLISH/BEARISH/NEUTRAL]
RISK LEVEL: [1-10]/10
CONFIDENCE: [LOW/MEDIUM/HIGH]
TIMEFRAME: [your recommended hold period]

ANALYSIS: [3-4 sentences on what's happening and why]

KEY CATALYSTS: [2-3 specific things that could move this stock]

RISKS: [2-3 specific risks to watch]

ACTION: [What should an investor do right now - specific and actionable]"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI analysis unavailable: {e}"


def connect_news_to_stocks(headlines):
    """
    ENHANCED: AI identifies affected stocks with impact severity.
    """
    prompt = f"""Analyze these financial headlines. For EACH headline that affects specific stocks:

HEADLINES:
{chr(10).join(f'- {h}' for h in headlines[:10])}

For each relevant headline, respond in this format:
HEADLINE: [the headline]
TICKERS: [affected symbols, comma separated]
IMPACT: [STRONG BULLISH / BULLISH / BEARISH / STRONG BEARISH]
SECTOR: [affected sector]
WHY: [one sentence explanation]
TIMEFRAME: [immediate / short-term / long-term]

Only include headlines that clearly affect specific stocks or sectors.
Be specific about WHY and which direction."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI connection unavailable: {e}"


def get_market_outlook(headlines):
    """
    ENHANCED: Comprehensive market outlook with sector rotation analysis.
    """
    prompt = f"""Based on these financial headlines, provide a market outlook:

HEADLINES:
{chr(10).join(f'- {h}' for h in headlines[:15])}

Respond in this EXACT format:
MARKET MOOD: [RISK-ON / RISK-OFF / MIXED]
DIRECTION: [BULLISH / BEARISH / NEUTRAL] for next 1-2 weeks

TOP SECTORS TO WATCH:
1. [Sector] - [why, one sentence]
2. [Sector] - [why, one sentence]
3. [Sector] - [why, one sentence]

SECTORS TO AVOID:
1. [Sector] - [why, one sentence]

KEY MACRO FACTORS: [2-3 sentences on big picture drivers]

WILD CARD: [One thing most people are missing that could change everything]"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.5,
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
    from app.models.xgboost_model import predict_direction

    print("=" * 50)
    print("   AI STOCK ANALYZER - ENHANCED AI Brain Test")
    print("=" * 50)

    # Get real data
    ticker = "AAPL"
    print(f"\nGathering data for {ticker}...")

    price_data = get_daily_change(ticker)
    news = get_rss_news(max_articles=10)
    headlines = [a["title"] for a in news]

    # Get indicators from prediction model
    prediction = predict_direction(ticker)
    indicators = prediction.get("indicators", {})

    # Test 1: Full Stock Analysis
    print("\n\n🧠 AI STOCK ANALYSIS:")
    print("-" * 50)
    analysis = analyze_stock(ticker, price_data, headlines, indicators)
    print(analysis)

    # Test 2: News → Stock Connections
    print("\n\n🔗 NEWS → STOCK CONNECTIONS:")
    print("-" * 50)
    connections = connect_news_to_stocks(headlines)
    print(connections)

    # Test 3: Market Outlook
    print("\n\n🌍 MARKET OUTLOOK:")
    print("-" * 50)
    outlook = get_market_outlook(headlines)
    print(outlook)

    print("\n" + "=" * 50)
    print("Enhanced AI Brain is working!")
    print("=" * 50)


def detect_divergence(ml_prediction, ai_analysis):
    """
    Detects when ML model and AI sentiment disagree.
    Returns a warning message if divergence is found.
    """
    ml_direction = ml_prediction.get("prediction", "Unknown").upper()

    # Check AI analysis for bearish/bullish keywords
    ai_text = ai_analysis.lower()
    if "bearish" in ai_text or "risk-off" in ai_text:
        ai_direction = "DOWN"
    elif "bullish" in ai_text or "risk-on" in ai_text:
        ai_direction = "UP"
    else:
        ai_direction = "NEUTRAL"

    # Check for divergence
    if ml_direction == "UP" and ai_direction == "DOWN":
        return {
            "divergence": True,
            "type": "TECH BULLISH / SENTIMENT BEARISH",
            "message": "Technical indicators suggest upward momentum, but news sentiment is bearish. This often means the stock is running on momentum that could reverse if negative news intensifies. Consider waiting for confirmation before entering a long position.",
            "risk_level": "ELEVATED",
        }
    elif ml_direction == "DOWN" and ai_direction == "UP":
        return {
            "divergence": True,
            "type": "TECH BEARISH / SENTIMENT BULLISH",
            "message": "Technical indicators show weakness, but news sentiment is positive. This could be a buying opportunity if the positive catalysts are strong enough to reverse the technical trend. Watch for a technical bounce confirmation.",
            "risk_level": "MODERATE",
        }
    else:
        return {
            "divergence": False,
            "type": "ALIGNED",
            "message": f"Technical analysis and news sentiment are aligned ({ml_direction}). Higher conviction signal.",
            "risk_level": "NORMAL",
        }
