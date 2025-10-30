  import React, { useState } from 'react';
  import axios from 'axios';
  import './App.css';

  // Base URL for backend
  // Use Docker network hostname when running frontend in Docker
  const API_BASE = process.env.REACT_APP_API_BASE || "http://sentiment-api:5000"; 
  const PREDICT_ENDPOINT = `${API_BASE}/predict`;
  const STATS_ENDPOINT = `${API_BASE}/stats`;

  function App() {
    const [review, setReview] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const [statsLoading, setStatsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('analyze');

    // Helper: Retry requests if backend is not ready yet
    const fetchWithRetry = async (axiosConfig, retries = 10, delay = 1000) => {
      for (let i = 0; i < retries; i++) {
        try {
          const response = await axios(axiosConfig);
          return response;
        } catch (err) {
          if (i === retries - 1) throw err; // last try, throw error
          await new Promise(r => setTimeout(r, delay));
        }
      }
    };

    const analyzeSentiment = async () => {
      if (!review.trim()) return;
      
      setLoading(true);
      setResult(null);
      try {
        const response = await fetchWithRetry({
          method: 'post',
          url: PREDICT_ENDPOINT,
          data: { text: review },
        }, 15, 1000); // 15 retries with 1s interval

        setResult(response.data);
      } catch (error) {
        console.error('Error analyzing sentiment:', error);
        setResult({ error: 'Failed to analyze sentiment. Make sure the backend is running.' });
      }
      setLoading(false);
    };

    const loadStats = async () => {
      setStatsLoading(true);
      try {
        const response = await fetchWithRetry({
          method: 'get',
          url: STATS_ENDPOINT,
        }, 15, 1000);

        setStats(response.data);
      } catch (error) {
        console.error('Error loading stats:', error);
        setStats(null);
      }
      setStatsLoading(false);
    };

    const getSentimentColor = (sentiment) => {
      switch (sentiment) {
        case 'positive': return '#10b981';
        case 'negative': return '#ef4444';
        case 'neutral': return '#6b7280';
        default: return '#6b7280';
      }
    };

    return (
      <div className="app">
        <header className="header">
          <h1>🎬 Movie Sentiment Analyzer</h1>
          <p>Discover the emotion behind movie reviews</p>
        </header>

        <nav className="tabs">
          <button 
            className={activeTab === 'analyze' ? 'active' : ''}
            onClick={() => setActiveTab('analyze')}
          >
            Analyze Review
          </button>
          <button 
            className={activeTab === 'stats' ? 'active' : ''}
            onClick={() => {
              setActiveTab('stats');
              loadStats();
            }}
          >
            Statistics
          </button>
        </nav>

        <main className="main-content">
          {activeTab === 'analyze' && (
            <div className="analyze-section">
              <div className="input-section">
                <textarea
                  value={review}
                  onChange={(e) => setReview(e.target.value)}
                  placeholder="Enter your movie review here... 
  Example: 'This movie was absolutely fantastic! Great acting and storyline.'"
                  rows="6"
                />
                <button 
                  onClick={analyzeSentiment} 
                  disabled={loading || !review.trim()}
                  className="analyze-btn"
                >
                  {loading ? 'Analyzing...' : 'Analyze Sentiment'}
                </button>
              </div>

              {result && !result.error && (
                <div className="result-section">
                  <h3>Analysis Result</h3>
                  <div 
                    className="sentiment-badge"
                    style={{ backgroundColor: getSentimentColor(result.sentiment) }}
                  >
                    {result.sentiment.toUpperCase()}
                  </div>
                  <div className="confidence">
                    Confidence: <strong>{(result.confidence_score * 100).toFixed(1)}%</strong>
                  </div>
                  {result.description && (
                    <div className="description">
                      {result.description}
                    </div>
                  )}
                  <div className="review-text">
                    <strong>Your Review:</strong> "{result.text}"
                  </div>
                </div>
              )}

              {result && result.error && (
                <div className="error-section">
                  {result.error}
                </div>
              )}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="stats-section">
              <h3>📊 API Statistics</h3>
              {statsLoading ? (
                <p>Loading statistics...</p>
              ) : stats ? (
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-number">{stats.statistics?.total_reviews || 0}</div>
                    <div className="stat-label">Total Reviews</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number">
                      {stats.statistics?.sentiment_distribution?.positive || 0}
                    </div>
                    <div className="stat-label">Positive</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number">
                      {stats.statistics?.sentiment_distribution?.negative || 0}
                    </div>
                    <div className="stat-label">Negative</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-number">
                      {stats.statistics?.sentiment_distribution?.neutral || 0}
                    </div>
                    <div className="stat-label">Neutral</div>
                  </div>
                </div>
              ) : (
                <p>Failed to load statistics</p>
              )}
            </div>
          )}
        </main>

        <footer className="footer">
          <p>Powered by VADER Sentiment Analysis & React</p>
        </footer>
      </div>
    );
  }

  export default App;
