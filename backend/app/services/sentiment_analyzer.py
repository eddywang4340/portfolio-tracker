from newsapi import NewsApiClient
from transformers import pipeline
import os
import torch

class SentimentAnalyzer:
    def __init__(self):
        self.news_api = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
        self.sentiment_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    
    def analyze_stock_sentiment(self, symbol: str):
        """Get news sentiment for a stock"""
        try:
            articles = self.news_api.get_everything(
                q=symbol,
                language='en',
                sort_by='publishedAt',
                page_size=10
            )
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return {"sentiment": "neutral", 
                    "score": 0, 
                    "articles_analyzed": 0,
                    "top_headlines": [],
                    "error": "Failed to fetch news"}

        if not articles or 'articles' not in articles or not articles['articles']:
            return {"sentiment": "neutral", "score": 0, "articles_analyzed": 0, "top_headlines": []}
        
        # Analyze sentiment
        sentiments: list[float] = []
        headlines: list[str] = []

        for article in articles['articles'][:10]:
            title = article.get('title') or ""
            description = article.get('description') or ""

            if not title and not description:
                continue

            text = f"{title} {description}".strip()
            if len(text) < 10:
                continue

            if title and len(headlines) < 3:
                headlines.append(title)

            if len(sentiments) < 5:
                try:
                    result = self.sentiment_model(text[:512])[0]  # Truncate to first 512 chars
                    score = result['score'] if result['label'] == 'positive' else -result['score']
                    sentiments.append(score)
                except Exception as e:
                    print(f"Error analyzing sentiment for article: {str(e)}")
                    continue
        
        if not sentiments:
            return {"sentiment": "neutral", "score": 0, "articles_analyzed": 0, "top_headlines": headlines}
        avg_sentiment = sum(sentiments) / len(sentiments)

        return {
            "sentiment": "positive" if avg_sentiment > 0.2 else "negative" if avg_sentiment < -0.2 else "neutral",
            "score": round(avg_sentiment, 2),
            "articles_analyzed": len(sentiments),
            "top_headlines": headlines
        }