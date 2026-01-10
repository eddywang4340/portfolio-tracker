from newsapi import NewsApiClient
from transformers import pipeline
import os

class SentimentAnalyzer:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
        self.sentiment_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    
    def analyze_stock_sentiment(self, symbol: str):
        """Get news sentiment for a stock"""
        articles = self.news_api.get_everything(
            q=symbol,
            language='en',
            sort_by='publishedAt',
            page_size=10
        )

        if not articles['articles']:
            return {"sentiment": "neutral", "score": 0, "articles_analyzed": 0}
        
        # Analyze sentiment
        sentiments = []
        for article in articles['articles'][:5]:
            text = f"{article['title']} {article.get('description', '')}"
            result = self.sentiment_model(text[:512])[0]  # Truncate to first 512 chars

            score = result['score'] if result['label'] == 'positive' else -result['score']
            sentiments.append(score)
        
        avg_sentiment = sum(sentiments) / len(sentiments)

        return {
            "sentiment": "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral",
            "score": round(avg_sentiment, 2),
            "articles_analyzed": len(sentiments),
            "top_headlines": [a['title'] for a in articles['articles'][:3]]
        }