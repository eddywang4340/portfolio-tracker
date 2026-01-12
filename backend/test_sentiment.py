import requests
import json

BASE_URL = "http://localhost:8000"

print("=== Testing Sentiment Analysis ===\n")

# Test 1: Single stock sentiment
print("Test 1: Single Stock Sentiment (AAPL)")
print("-" * 50)
response = requests.get(f"{BASE_URL}/plaid/ml/sentiment/AAPL")
if response.status_code == 200:
    data = response.json()
    print(f"Sentiment:        {data['sentiment'].upper()}")
    print(f"Sentiment Score:  {data['score']}")
    print(f"Articles Analyzed: {data['articles_analyzed']}")
    print(f"\nTop Headlines:")
    for i, headline in enumerate(data['top_headlines'], 1):
        print(f"  {i}. {headline}")
else:
    print(f"Error: {response.text}")

print("\n" + "="*50 + "\n")

# Test 2: Full portfolio insights (ML + Sentiment)
print("Test 2: Full Portfolio Insights (ML Predictions + Sentiment)")
print("-" * 50)

# Create or use test portfolio
response = requests.post(f"{BASE_URL}/plaid/create_test_portfolio")
if response.status_code == 200:
    user_data = response.json()
    user_id = user_data["user_id"]
    print(f"✓ Using test portfolio (User ID: {user_id})\n")
    
    # Get full insights
    response = requests.get(f"{BASE_URL}/plaid/ml/portfolio-insights/{user_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"Insights for {data['insights_count']} stocks:\n")
        
        for insight in data['insights']:
            symbol = insight['symbol']
            pred = insight['prediction']
            sent = insight['sentiment']
            
            # Determine recommendation
            price_up = pred['change_pct'] > 0
            sent_positive = sent['sentiment'] == 'positive'
            
            if price_up and sent_positive:
                recommendation = "🟢 STRONG BUY"
            elif price_up or sent_positive:
                recommendation = "🟡 HOLD/BUY"
            elif not price_up and not sent_positive:
                recommendation = "🔴 CONSIDER SELLING"
            else:
                recommendation = "🟡 HOLD"
            
            print(f"\n{symbol} - {recommendation}")
            print(f"  Price Prediction: ${pred['current_price']:.2f} → ${pred['predicted_price']:.2f} ({pred['change_pct']:+.2f}%)")
            print(f"  News Sentiment: {sent['sentiment'].upper()} (score: {sent['score']})")
            print(f"  Top Headline: {sent['top_headlines'][0] if sent['top_headlines'] else 'N/A'}")
    else:
        print(f"Error: {response.text}")
else:
    print(f"Error creating test portfolio: {response.text}")

print("\n✓ Sentiment analysis tests completed!")