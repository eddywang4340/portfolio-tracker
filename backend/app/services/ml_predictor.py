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
    
    def calculate_confidence(self, X_test_scaled, current_price):
        """
        Calculate prediction confidence based on:
        1. Variance among individual tree predictions
        2. Coefficient of variation (relative standard deviation)
        3. 95% prediction interval
        """
        tree_predictions = np.array([tree.predict(X_test_scaled)[0] for tree in self.model.estimators_])
        prediction_std = np.std(tree_predictions)
        mean_prediction = np.mean(tree_predictions)
        relative_std = (prediction_std / abs(mean_prediction)) * 100 if mean_prediction != 0 else 100

        # Calculate confidence score (inverse of relative std)
        # Lower variance among trees = higher confidence
        if relative_std < 0.5:
            confidence_score = 95
            confidence_label = "high"
        elif relative_std < 1.0:
            confidence_score = 85
            confidence_label = "high"
        elif relative_std < 2.0:
            confidence_score = 70
            confidence_label = "medium"
        elif relative_std < 3.0:
            confidence_score = 55
            confidence_label = "medium"
        else:
            confidence_score = 40
            confidence_label = "low"

        # Calculate 95% prediction interval
        z_score = 1.96  # 95% confidence interval
        margin = z_score * prediction_std

        return {
            "score": int(confidence_score),
            "label": confidence_label,
            "std": float(prediction_std),
            "relative_std_pct": float(relative_std),
            "prediction_interval": {
                "lower": float(mean_prediction - margin),
                "upper": float(mean_prediction + margin)
            }
        }
    
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

        # Calculate confidence metrics
        confidence_data = self.calculate_confidence(X_test_scaled, current_price)

        return {
            "current_price": float(current_price),
            "predicted_price": float(prediction),
            "change_pct": float(((prediction - current_price) / current_price) * 100),
            "confidence": confidence_data["label"],
            "confidence_score": confidence_data["score"],
            "prediction_interval": confidence_data["prediction_interval"],
            "confidence_details": {
                "std_deviation": confidence_data["std"],
                "relative_std_pct": confidence_data["relative_std_pct"]
            }
        }