import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator

class StockPredictor:
    """Simple ML model for stock price prediction"""

    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scalar = StandardScaler()
    
    def get_features(self, symbol: str, days: int = 60):
        """Fetch historical data and calculate technical indicators"""
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='3mo')

        if data.empty:
            return None
        
        # Calculate technical indicators
        data['SMA_10'] = SMAIndicator(data['Close'], window=10).sma_indicator()
        data['SMA_20'] = SMAIndicator(data['Close'], window=20).sma_indicator()
        data['EMA_12'] = EMAIndicator(data['Close'], window=12).ema_indicator()
        data['RSI'] = RSIIndicator(data['Close']).rsi()

        # Price changes
        data['Price_Change'] = data['Close'].pct_change()
        data['Volume_Change'] = data['Volume'].pct_change()

        # Lag features (previous days)
        for i in [1, 2, 3, 5]:
            data[f'Close_Lag_{i}'] = data['Close'].shift(i)
        
        data = data.dropna()
        return data
    
    def predict_next_day(self, symbol: str):
        """Predict next day's closing price"""
        df = self.get_features(symbol)

        if df is None or len(df) < 30:
            return None
        
        # Features for training
        features_cols = ['SMA_10', 'SMA_20', 'EMA_12', 'RSI',
                         'Price_Change', 'Volume_Change',
                         'Close_Lag_1', 'Close_Lag_2', 'Close_Lag_3', 'Close_Lag_5']
        X = df[features_cols].values
        Y = df['Close'].values

        # Train on historical data
        X_train, Y_train = X[:-1], Y[1:]
        X_test = X[-1:]

        # Scale and train
        X_train_scaled = self.scalar.fit_transform(X_train)
        X_test_scaled = self.scalar.transform(X_test)

        self.model.fit(X_train_scaled, Y_train)

        # Predict
        prediction = self.model.predict(X_test_scaled)[0]
        current_price = df['Close'].iloc[-1]

        return {
            "current_price": float(current_price),
            "predicted_price": float(prediction),
            "change_pct": float(((prediction - current_price) / current_price) * 100),
            "confidence": "medium" # TODO: Add confidence calculation
        }