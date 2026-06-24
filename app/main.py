"""
AI Stock Analyzer - Main Dashboard
====================================
Run with: streamlit run app/main.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stock_data import get_stock_history, get_daily_change
from app.services.news_service import get_rss_news, get_news_for_ticker
from app.services.sentiment_service import analyze_sentiment, analyze_news_sentiment
from app.models.xgboost_model import predict_direction

# Page config
st.set_page_config(
    page_title="AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
)

# Title
st.title("📈 AI Stock Analyzer")
st.markdown("*Real-time stock data, news sentiment, and AI predictions*")
st.markdown("---")

# Sidebar - Stock Input
st.sidebar.header("🔍 Stock Lookup")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL").upper()
analyze_btn = st.sidebar.button("🚀 Analyze Stock", use_container_width=True)

if analyze_btn or ticker:
    # Create columns for layout
    col1, col2 = st.columns(2)

    # --- LEFT COLUMN: Price Data ---
    with col1:
        st.subheader(f"💰 {ticker} Price Data")
        with st.spinner("Fetching price data..."):
            change = get_daily_change(ticker)

        if change.get("dollar_change", 0) >= 0:
            st.metric(
                label="Current Price",
                value=f"${change.get('current_price', 'N/A')}",
                delta=f"${change.get('dollar_change', 0)} ({change.get('percent_change', 0)}%)",
            )
        else:
            st.metric(
                label="Current Price",
                value=f"${change.get('current_price', 'N/A')}",
                delta=f"${change.get('dollar_change', 0)} ({change.get('percent_change', 0)}%)",
            )

        # Price chart
        st.subheader("📊 6-Month Price Chart")
        with st.spinner("Loading chart..."):
            history = get_stock_history(ticker, period="6mo")
        if not history.empty:
            st.line_chart(history.set_index("Date")["Close"])

    # --- RIGHT COLUMN: Prediction ---
    with col2:
        st.subheader("🤖 AI Prediction")
        with st.spinner("Training model & predicting..."):
            prediction = predict_direction(ticker)

        if prediction["prediction"] != "Unknown":
            emoji = "📈" if prediction["prediction"] == "UP" else "📉"
            st.markdown(f"### {emoji} {prediction['prediction']} in next 7 days")
            st.write(f"**Confidence:** {prediction['confidence']}%")
            st.write(f"**Model Accuracy:** {prediction['model_accuracy']}%")
        else:
            st.write("Could not generate prediction")

# --- NEWS & SENTIMENT SECTION ---
st.markdown("---")
st.subheader(f"📰 News & Sentiment for {ticker}")

col3, col4 = st.columns([2, 1])

with col3:
    with st.spinner("Fetching news..."):
        sentiment_data = analyze_news_sentiment(ticker)

    if sentiment_data["articles"]:
        for article in sentiment_data["articles"][:5]:
            s = article["sentiment"]
            emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
            st.markdown(f"{emoji} **{s['label']}** ({s['score']}) — {article['title']}")
            st.caption(f"Source: {article['source']}")
    else:
        st.write("No ticker-specific news found. Showing market news:")
        market_news = get_rss_news(max_articles=5)
        for article in market_news:
            s = analyze_sentiment(article["title"])
            emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
            st.markdown(f"{emoji} **{s['label']}** ({s['score']}) — {article['title']}")

with col4:
    st.markdown("### Overall Sentiment")
    score = sentiment_data["overall_score"]
    label = sentiment_data["overall_label"]

    if label == "Bullish":
        st.success(f"🟢 {label} ({score})")
    elif label == "Bearish":
        st.error(f"🔴 {label} ({score})")
    else:
        st.warning(f"🟡 {label} ({score})")

    st.write(f"Based on {sentiment_data['total_articles']} articles")

# --- FOOTER ---
st.markdown("---")
st.markdown("### 📊 Market News Feed")

with st.spinner("Loading market news..."):
    market_news = get_rss_news(max_articles=10)

for article in market_news[:10]:
    s = analyze_sentiment(article["title"])
    emoji = "🟢" if s["label"] == "Bullish" else "🔴" if s["label"] == "Bearish" else "🟡"
    st.markdown(f"{emoji} [{article['title']}]({article['link']}) — *{article['source']}*")

st.markdown("---")
st.caption("Built by Andrew Hitt | AI Stock Analyzer v1.0")
st.caption("⚠️ Not financial advice. For educational purposes only.")
