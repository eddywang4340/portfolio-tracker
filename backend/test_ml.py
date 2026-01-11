import requests
import json

BASE_URL = "http://localhost:8000"

print("=== Testing ML Price Predictions ===\n")

# Test 1: Single stock prediction
print("Test 1: Single Stock Prediction (AAPL)")
print("-" * 50)
response = requests.get(f"{BASE_URL}/plaid/ml/predict/AAPL")
if response.status_code == 200:
    data = response.json()
    print(f"Current Price:   ${data['current_price']:.2f}")
    print(f"Predicted Price: ${data['predicted_price']:.2f}")
    print(f"Expected Change: {data['change_pct']:+.2f}%")
    print(f"Confidence:      {data['confidence']}")
else:
    print(f"Error: {response.text}")

print("\n" + "="*50 + "\n")

# Test 2: Portfolio predictions
print("Test 2: Portfolio Predictions")
print("-" * 50)

# First, get or create test portfolio
response = requests.post(f"{BASE_URL}/plaid/create_test_portfolio")
if response.status_code == 200:
    user_data = response.json()
    user_id = user_data["user_id"]
    print(f"✓ Using test portfolio (User ID: {user_id})\n")
    
    # Get predictions for portfolio
    response = requests.get(f"{BASE_URL}/plaid/ml/portfolio-predictions/{user_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"Predictions for {data['predictions_count']} stocks:\n")
        
        total_potential = 0
        for pred in data['predictions']:
            symbol = pred['symbol']
            qty = pred['quantity']
            current = pred['current_price']
            predicted = pred['predicted_price']
            change = pred['change_pct']
            potential = pred['potential_gain_loss']
            total_potential += potential
            
            direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            print(f"{direction} {symbol:<6} | Qty: {qty:>3} | "
                  f"Current: ${current:>7.2f} | Predicted: ${predicted:>7.2f} | "
                  f"Change: {change:>+6.2f}% | Potential: ${potential:>+8.2f}")
        
        print(f"\n{'='*80}")
        print(f"Total Potential Gain/Loss: ${total_potential:+.2f}")
        print(f"{'='*80}")
    else:
        print(f"Error: {response.text}")
else:
    print(f"Error creating test portfolio: {response.text}")

print("\n✓ ML prediction tests completed!")