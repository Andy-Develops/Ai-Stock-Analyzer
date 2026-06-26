"""
AI Stock Analyzer - ENHANCED Dashboard v2.0
=============================================
Run with: streamlit run app/main.py
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stock_data import get_stock_history, get_daily_change
from app.services.news_service import get_rss_news, get_news_for_ticker
from app.services.sentiment_service import analyze_sentiment, analyze_news_sentiment
from app.models.xgboost_model import predict_direction
from app.services.ai_summary import analyze_stock, connect_news_to_stocks, get_market_outlook, detect_divergence

st.set_page_config(
    page_title="AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 AI Stock Analyzer & Predictor")
st.markdown("*Real-time data • AI-powered analysis • ML predictions • News sentiment*")
st.markdown("---")

# Sidebar
st.sidebar.header("🔍 Stock Lookup")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()
analyze_btn = st.sidebar.button("🚀 Analyze Stock", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Picks")
col_a, col_b = st.sidebar.columns(2)
with col_a:
    if st.sidebar.button("AAPL"):
        ticker = "AAPL"
    if st.sidebar.button("NVDA"):
        ticker = "NVDA"
    if st.sidebar.button("TSLA"):
        ticker = "TSLA"
with col_b:
    if st.sidebar.button("MSFT"):
        ticker = "MSFT"
    if st.sidebar.button("AMZN"):
        ticker = "AMZN"
    if st.sidebar.button("GOOGL"):
        ticker = "GOOGL"

if analyze_btn or ticker:
    # === ROW 1: Price + Prediction ===
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"�� {ticker} Price Data")
        with st.spinner("Fetching price data..."):
            change = get_daily_change(ticker)

        if change.get("current_price"):
            st.metric(
                label="Current Price",
                value=f"${change.get('current_price', 'N/A')}",
                delta=f"${change.get('dollar_change', 0)} ({change.get('percent_change', 0)}%)",
            )

        st.markdown("**�� 6-Month Price Chart**")
        with st.spinner("Loading chart..."):
            history = get_stock_history(ticker, period="6mo")
        if not history.empty:
            st.line_chart(history.set_index("Date")["Close"])

    with col2:
        st.subheader("�� ML Prediction (XGBoost)")
        with st.spinner("Training model on 5 years of data..."):
            prediction = predict_direction(ticker)

        if prediction["prediction"] != "Unknown":
            emoji = "��" if prediction["prediction"] == "UP" else "��"
            st.markdown(f"### {emoji} {prediction['prediction']} in next 7 days")

            m1, m2 = st.columns(2)
            m1.metric("Confidence", f"{prediction['confidence']}%")
            m2.metric("Model Accuracy", f"{prediction['model_accuracy']}%")

            st.markdown("**�� Technical Indicators:**")
            indicators = prediction.get("indicators", {})
            if indicators:
                rsi = indicators.get("rsi", 50)
                rsi_status = "�� Overbought" if rsi > 70 else "�� Oversold" if rsi < 30 else "�� Normal"
                macd_h = indicators.get("macd_histogram", 0)
                macd_status = "�� Bullish" if macd_h > 0 else "�� Bearish"
                boll = indicators.get("bollinger_pct_b", 0.5)
                boll_status = "�� Stretched" if boll > 0.8 else "�� Compressed" if boll < 0.2 else "�� Mid"

                st.markdown(f"- **RSI (14):** {rsi} {rsi_status}")
                st.markdown(f"- **MACD:** {macd_h} {macd_status}")
                st.markdown(f"- **Bollinger %B:** {boll} {boll_status}")
                st.markdown(f"- **Volume:** {indicators.get('volume_ratio', 'N/A')}x avg")
                st.markdown(f"- **ATR%:** {indicators.get('atr_percent', 'N/A')}%")

            if prediction.get("top_features"):
                st.markdown("**�� Top Predictive Features:**")
                for feature, importance in prediction["top_features"][:3]:
                    st.markdown(f"- {feature}: {round(importance*100,1)}%")
        else:
            st.write("Could not generate prediction")

    # === AI ANALYSIS ===
    st.markdown("---")
    st.subheader(f"�� AI Analysis — {ticker}")
    with st.spinner("AI is analyzing..."):
        news = get_rss_news(max_articles=10)
        headlines = [a["title"] for a in news]
        indicators = prediction.get("indicators", {})
        analysis = analyze_stock(ticker, change, headlines, indicators)
    st.markdown(analysis)

    # === DIVERGENCE ALERT ===
    divergence = detect_divergence(prediction, analysis)
    if divergence["divergence"]:
        st.markdown("---")
        st.warning(f"⚠️ **DIVERGENCE DETECTED: {divergence['type']}**")
        st.markdown(f"> {divergence['message']}")
        st.markdown(f"**Risk Level:** {divergence['risk_level']}")
    else:
        st.success(f"✅ **SIGNALS ALIGNED:** {divergence['message']}")

    # === NEWS & SENTIMENT ===
    st.markdown("---")
    col3, col4 = st.columns([2, 1])

    with col3:
        st.subheader(f"📰 News Sentiment — {ticker}")
        with st.spinner("Analyzing news sentiment..."):
            sentiment_data = analyze_news_sentiment(ticker)

        if sentiment_data["articles"]:
            for article in sentiment_data["articles"][:5]:
                s = article["sentiment"]
                emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
                impact_badge = f"**[{s['impact']}]**" if s.get("impact") else ""
                st.markdown(f"{emoji} {s['label']} ({s['score']}) {impact_badge} — {article['title']}")
                st.caption(f"Source: {article['source']} (credibility: {s.get('source_weight', 'N/A')}x)")
        else:
            st.write("No ticker-specific news. Showing market news:")
            market_news = get_rss_news(max_articles=5)
            for article in market_news:
                s = analyze_sentiment(article["title"], article.get("source", "UNKNOWN"))
                emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
                st.markdown(f"{emoji} {s['label']} ({s['score']}) — {article['title']}")

    with col4:
        st.subheader("📊 Sentiment Score")
        score = sentiment_data["overall_score"]
        label = sentiment_data["overall_label"]

        if label == "Bullish":
            st.success(f"🟢 {label} ({score})")
        elif label == "Bearish":
            st.error(f"🔴 {label} ({score})")
        else:
            st.warning(f"🟡 {label} ({score})")

        st.write(f"Based on {sentiment_data['total_articles']} articles")
        st.markdown("---")
        st.markdown("**Legend:**")
        st.markdown("- 🟢 > 0.6 = Bullish")
        st.markdown("- 🟡 0.4-0.6 = Neutral")
        st.markdown("- 🔴 < 0.4 = Bearish")

    # === MARKET OUTLOOK ===
    st.markdown("---")
    st.subheader("🌍 AI Market Outlook")
    with st.spinner("Generating market outlook..."):
        outlook = get_market_outlook(headlines)
    st.markdown(outlook)

    # === NEWS → STOCK CONNECTIONS ===
    st.markdown("---")
    st.subheader("🔗 News → Stock Connections")
    with st.spinner("AI connecting news to stocks..."):
        connections = connect_news_to_stocks(headlines)
    st.markdown(connections)

# === FOOTER ===
st.markdown("---")
st.markdown("### 📰 Live Market Feed")

with st.spinner("Loading market news..."):
    market_news = get_rss_news(max_articles=10)

for article in market_news[:10]:
    s = analyze_sentiment(article["title"], article.get("source", "UNKNOWN"))
    emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
    st.markdown(f"{emoji} [{article['title']}]({article['link']}) — *{article['source']}*")

st.markdown("---")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.caption("Built by Andrew Hitt | AI Stock Analyzer v2.0")
with col_f2:
    st.caption("⚠️ Not financial advice. For educational purposes only.")
