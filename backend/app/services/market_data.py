import yfinance as yf

def get_current_price(symbol: str):  # Note: not async anymore
    """Get current stock price using Yahoo Finance (no API key needed)"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d')
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            return float(current_price)
        else:
            return None
    except Exception as e:
        print(f"Error fetching {symbol}: {str(e)}")
        return None