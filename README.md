# AI Stock Analyzer & Predictor

A full-stack AI-powered stock analysis platform with real-time market data, NLP sentiment analysis, XGBoost ML predictions, and OpenAI-powered insights.

## Features

- Live Stock Data - Real-time prices, volume, moving averages via Yahoo Finance
- News Feed - Real-time financial headlines from CNBC, MarketWatch, Yahoo Finance
- Sentiment Analysis - NLP scoring of news (Bullish/Bearish/Neutral)
- ML Predictions - XGBoost model predicts 7-day price direction
- AI Brain - GPT-4o-mini connects news to stocks and explains market impact
- Interactive Dashboard - Streamlit web UI with charts and live data

## Tech Stack

- Frontend: Streamlit
- Stock Data: yfinance
- News: RSS (feedparser), Finnhub, NewsAPI
- Sentiment: TextBlob + custom financial keywords
- ML Model: XGBoost, scikit-learn
- AI/LLM: OpenAI GPT-4o-mini
- Infrastructure: AWS EC2 -> Lambda + Amplify
- Language: Python 3.9

## Run

streamlit run app/main.py --server.port 8501

## Architecture

User -> Streamlit Dashboard
         - Stock Data Service (yfinance)
         - News Service (RSS feeds)
         - Sentiment Service (TextBlob + NLP)
         - AI Summary (OpenAI GPT-4o-mini)
         - Prediction Model (XGBoost)

## Roadmap

- Stripe subscription integration
- User authentication
- Portfolio tracking
- Real-time WebSocket price updates
- Deploy to AWS Lambda + Amplify

## Disclaimer

Not financial advice. For educational and portfolio demonstration purposes only.

## Built By

Andrew Hitt - AWS Data Center Technician | Cloud Practitioner | Aspiring Solutions Architect
