import React, { useState, useEffect } from 'react';
import { getStockPrediction, getStockSentiment } from '../services/api';

interface MLInsightsProps {
    symbol: string;
    currentPrice: number;
}

const MLInsights: React.FC<MLInsightsProps> = ({ symbol, currentPrice }) => {
    const [prediction, setPrediction] = useState<any>(null);
    const [sentiment, setSentiment] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                setLoading(true);
                setError(null);
                const [predData, sentData] = await Promise.all([
                    getStockPrediction(symbol),
                    getStockSentiment(symbol)
                ]);
                setPrediction(predData);
                setSentiment(sentData);
            } catch (error) {
                console.error('Error fetching ML insights:', error);
                setError('Unable to load insights');
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();
    }, [symbol]);

    if (loading) {
        return <div className="ml-insights loading">Loading insights...</div>;
    }

    if (error || !prediction || !sentiment) {
        return <div className="ml-insights error">Unable to load insights</div>;
    }

    const priceChange = prediction.predicted_price - currentPrice;
    const priceChangePercent = prediction.change_pct;
    const isPositive = priceChange > 0;

    const getSentimentLabel = (score: number) => {
        if (score > 0.3) return 'Bullish';
        if (score < -0.3) return 'Bearish';
        return 'Neutral';
    };

    const getSentimentColor = (score: number) => {
        if (score > 0.3) return '#10b981'; // green
        if (score < -0.3) return '#ef4444'; // red
        return '#6b7280'; // gray
    };

    const sentimentScore = sentiment.score || 0;

    return (
        <div className="ml-insights">
        <div className="prediction-section">
            <h4>Price Prediction (Next Day)</h4>
            <div className="prediction-value">
            <span className="current-price">${prediction.current_price.toFixed(2)}</span>
            <span className="arrow">→</span>
            <span className={`predicted-price ${isPositive ? 'positive' : 'negative'}`}>
                ${prediction.predicted_price.toFixed(2)}
            </span>
            <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
                ({isPositive ? '+' : ''}{priceChangePercent.toFixed(2)}%)
            </span>
            </div>
            <div className="confidence">
            Confidence: {prediction.confidence}
            </div>
        </div>

        <div className="sentiment-section">
            <h4>Market Sentiment</h4>
            <div className="sentiment-score" style={{ color: getSentimentColor(sentimentScore) }}>
                <span className="label">{getSentimentLabel(sentimentScore) + ": "}</span>
                <span className="score">{sentimentScore.toFixed(2)}</span>
            </div>
            <div className="sentiment-bar">
            <div 
                className="sentiment-fill"
                style={{
                width: `${((sentimentScore + 1) / 2) * 100}%`,
                backgroundColor: getSentimentColor(sentimentScore)
                }}
            />
            </div>
            <div className="news-count">
            Based on {sentiment.articles_analyzed} recent articles
            </div>
            {sentiment.top_headlines && sentiment.top_headlines.length > 0 && (
            <div className="top-headline" style={{ marginTop: '8px', fontSize: '12px', color: '#6b7280' }}>
                📰 {sentiment.top_headlines[0]}
            </div>
            )}
        </div>
        </div>
    );
};

export default MLInsights;