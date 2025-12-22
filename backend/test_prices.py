import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=== Testing Live Price Updates ===\n")

# Step 1: Create test portfolio
print("Step 1: Creating test portfolio...")
response = requests.post(f"{BASE_URL}/plaid/create_test_portfolio")
if response.status_code != 200:
    print(f"Error: {response.text}")
    exit()

data = response.json()
user_id = data["user_id"]
print(f"✓ Created user {user_id} with {data['holdings_created']} test holdings\n")

# Step 2: Check BEFORE prices
print("Step 2: Holdings BEFORE price update:")
response = requests.get(f"{BASE_URL}/plaid/portfolio/{user_id}/holdings")
if response.status_code != 200:
    print(f"Error: {response.text}")
    exit()

holdings_before = response.json()["holdings"]
for h in holdings_before:
    price_display = "None" if h['current_price'] is None else f"${h['current_price']:.2f}"
    print(f"  {h['symbol']:<6} - Price: {price_display}")

# Step 3: Update prices
print("\nStep 3: Updating prices from market data API...")
print("(This may take a few seconds...)")
response = requests.post(f"{BASE_URL}/plaid/update_prices/{user_id}")
if response.status_code != 200:
    print(f"Error: {response.text}")
    exit()

result = response.json()
print(f"✓ {result['status']} ({result['holdings_updated']} holdings)\n")

# Small delay to ensure DB is updated
time.sleep(1)

# Step 4: Check AFTER prices
print("Step 4: Holdings AFTER price update:")
response = requests.get(f"{BASE_URL}/plaid/portfolio/{user_id}/holdings")
if response.status_code != 200:
    print(f"Error: {response.text}")
    exit()

holdings_after = response.json()["holdings"]
total_value = 0

for h in holdings_after:
    if h['current_price']:
        price_display = f"${h['current_price']:.2f}"
        value = h['quantity'] * h['current_price']
        total_value += value
        gain_loss = value - h['cost_basis']
        gain_loss_pct = (gain_loss / h['cost_basis'] * 100) if h['cost_basis'] > 0 else 0
        
        print(f"  {h['symbol']:<6} - Price: {price_display:>10} | Qty: {h['quantity']:>5} | Value: ${value:>10.2f} | G/L: {gain_loss_pct:>6.2f}%")
    else:
        print(f"  {h['symbol']:<6} - Price: None (API error)")

print(f"\nTotal Portfolio Value: ${total_value:.2f}")
print("✓ Price update test completed!")