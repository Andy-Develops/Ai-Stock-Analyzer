import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// UPDATE THIS after you deploy API Gateway
const API_URL = process.env.REACT_APP_API_URL || "https://9xt1z2hp06.execute-api.us-east-1.amazonaws.com/prod";

function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [news, setNews] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [outlook, setOutlook] = useState(null);

  const analyzeStock = async () => {
    setLoading(true);
    try {
      const [analyzeRes, newsRes, aiRes, outlookRes] = await Promise.all([
        axios.post(`${API_URL}/analyze`, { ticker }),
        axios.post(`${API_URL}/news`, { ticker }),
        axios.post(`${API_URL}/ai-summary`, { ticker }),
        axios.post(`${API_URL}/market-outlook`),
      ]);
      setData(analyzeRes.data);
      setNews(newsRes.data);
      setAiAnalysis(aiRes.data);
      setOutlook(outlookRes.data);
    } catch (err) {
      console.error("Error:", err);
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="header">
        <h1>📈 AI Stock Analyzer</h1>
        <p>Real-time data • AI analysis • ML predictions • News sentiment</p>
      </header>

      <div className="search-bar">
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="Enter ticker (AAPL, TSLA, NVDA...)"
        />
        <button onClick={analyzeStock} disabled={loading}>
          {loading ? "Analyzing..." : "🚀 Analyze"}
        </button>
      </div>

      <div className="quick-picks">
        {["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL"].map((t) => (
          <button key={t} onClick={() => { setTicker(t); }} className="pick-btn">
            {t}
          </button>
        ))}
      </div>

      {loading && <div className="loading">🔄 Analyzing {ticker}... (training ML model + AI analysis)</div>}

      {data && (
        <div className="results">
          {/* Price + Prediction Row */}
          <div className="row">
            <div className="card">
              <h2>💰 {data.ticker} Price</h2>
              <div className="price">${data.price?.current_price}</div>
              <div className={data.price?.dollar_change >= 0 ? "change-up" : "change-down"}>
                ${data.price?.dollar_change} ({data.price?.percent_change}%)
              </div>
            </div>

            <div className="card">
              <h2>🤖 ML Prediction</h2>
              <div className="prediction">
                {data.prediction?.direction === "UP" ? "📈" : "📉"} {data.prediction?.direction}
              </div>
              <p>Confidence: {data.prediction?.confidence}%</p>
              <p>Model Accuracy: {data.prediction?.model_accuracy}%</p>
              <h3>Technical Indicators</h3>
              <ul>
                <li>RSI: {data.prediction?.indicators?.rsi}</li>
                <li>MACD: {data.prediction?.indicators?.macd_histogram}</li>
                <li>Bollinger %B: {data.prediction?.indicators?.bollinger_pct_b}</li>
                <li>Volume: {data.prediction?.indicators?.volume_ratio}x avg</li>
                <li>ATR%: {data.prediction?.indicators?.atr_percent}%</li>
              </ul>
            </div>
          </div>

          {/* AI Analysis */}
          {aiAnalysis && (
            <div className="card full-width">
              <h2>🧠 AI Analysis</h2>
              <pre className="analysis-text">{aiAnalysis.analysis}</pre>
              {aiAnalysis.divergence?.divergence && (
                <div className="divergence-alert">
                  ⚠️ DIVERGENCE: {aiAnalysis.divergence.type}
                  <p>{aiAnalysis.divergence.message}</p>
                </div>
              )}
              {!aiAnalysis.divergence?.divergence && (
                <div className="aligned-alert">
                  ✅ SIGNALS ALIGNED: {aiAnalysis.divergence?.message}
                </div>
              )}
            </div>
          )}

          {/* News Sentiment */}
          {news && (
            <div className="card full-width">
              <h2>📰 News Sentiment — {news.overall_label} ({news.overall_score})</h2>
              <div className="articles">
                {news.articles?.map((article, i) => (
                  <div key={i} className="article">
                    <span className="sentiment-badge">
                      {article.sentiment?.label === "Bullish" ? "🟢" : article.sentiment?.label === "Bearish" ? "🔴" : "🟡"}
                      {article.sentiment?.label} ({article.sentiment?.score})
                    </span>
                    <span className="article-title">{article.title}</span>
                    <span className="article-source">{article.source}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Market Outlook */}
          {outlook && (
            <div className="card full-width">
              <h2>🌍 Market Outlook</h2>
              <pre className="analysis-text">{outlook.outlook}</pre>
              <h3>🔗 News → Stock Connections</h3>
              <pre className="analysis-text">{outlook.connections}</pre>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>Built by Andrew Hitt | AI Stock Analyzer v2.0</p>
        <p>⚠️ Not financial advice. For educational purposes only.</p>
      </footer>
    </div>
  );
}

export default App;
