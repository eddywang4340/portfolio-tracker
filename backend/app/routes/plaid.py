from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services import plaid_service, market_data
from app.database import get_db
from app.models.user import User, Holding
from datetime import datetime, timezone
from app.services.ml_predictor import StockPredictor
from app.services.sentiment_analyzer import SentimentAnalyzer

router = APIRouter(prefix="/plaid", tags=["plaid"])

class ExchangeTokenRequest(BaseModel):
    public_token: str

@router.get("/create_link_token")
async def create_link_token():
    link_token = plaid_service.create_link_token()
    return {"link_token": link_token}

@router.post("/exchange_public_token")
async def exchange_token(request: ExchangeTokenRequest, db: Session = Depends(get_db)):
    access_token = plaid_service.exchange_public_token(request.public_token)
    user = User(plaid_access_token=access_token)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "access_token": access_token}

@router.post("/sync_portfolio")
async def sync_portfolio(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}
    
    holdings = plaid_service.get_holdings(user.plaid_access_token)

    # Clear old holdings
    db.query(Holding).filter(Holding.user_id == user.id).delete()

    # Insert new holdings
    for holding in holdings:
        db_holding = Holding(
            user_id=user.id,
            symbol=holding['symbol'],
            quantity=holding['quantity'],
            cost_basis=holding['cost_basis']
        )
        db.add(db_holding)
    db.commit()
    return {"status": "Portfolio synced successfully", "number_of_holdings": len(holdings)}

@router.get("/portfolio/{user_id}/holdings")
async def get_holdings_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get all holdings for a user"""
    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
    
    return {
        "user_id": user_id,
        "holdings": [
            {
                "symbol": h.symbol,
                "quantity": h.quantity,
                "cost_basis": h.cost_basis,
                "current_price": h.current_price
            }
            for h in holdings
        ]
    }

@router.post("/update_prices/{user_id}")
async def update_prices(user_id: int, db: Session = Depends(get_db)):
    """Update current prices for all holdings"""
    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()

    for holding in holdings:
        current_price = market_data.get_current_price(holding.symbol)
        if current_price:
            holding.current_price = current_price
            holding.last_updated = datetime.now(timezone.utc)
    
    db.commit()
    return {"status": "prices updated", "holdings_updated": len(holdings)}

@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: int, db: Session = Depends(get_db)):
    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
    total_value = 0
    total_cost = 0
    positions = []

    for holding in holdings:
        current_value = holding.quantity * (holding.current_price or 0)
        total_value += current_value
        total_cost += holding.cost_basis

        positions.append({
            "symbol": holding.symbol,
            "quantity": holding.quantity,
            "current_price": holding.current_price,
            "current_value": current_value,
            "cost_basis": holding.cost_basis,
            "gain_loss": current_value - holding.cost_basis,
            "gain_loss_pct": ((current_value - holding.cost_basis) / holding.cost_basis * 100) if holding.cost_basis > 0 else 0
        })

    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_value - total_cost,
        "total_gain_loss_pct": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
        "positions": positions
        }

@router.post("/create_test_portfolio")
async def create_test_portfolio(db: Session = Depends(get_db)):
    """Create a test user with fake portfolio data (DEV ONLY)"""
    
    # Create test user
    user = User(plaid_access_token="test-token")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add fake holdings
    test_holdings = [
        {"symbol": "AAPL", "quantity": 10, "cost_basis": 1500.00},
        {"symbol": "GOOGL", "quantity": 5, "cost_basis": 700.00},
        {"symbol": "MSFT", "quantity": 15, "cost_basis": 4500.00},
        {"symbol": "TSLA", "quantity": 3, "cost_basis": 750.00},
    ]
    
    for h in test_holdings:
        holding = Holding(
            user_id=user.id,
            symbol=h["symbol"],
            quantity=h["quantity"],
            cost_basis=h["cost_basis"]
        )
        db.add(holding)
    
    db.commit()
    
    return {
        "user_id": user.id,
        "holdings_created": len(test_holdings),
        "message": "Test portfolio created"
    }

@router.get("/ml/predict/{symbol}")
async def predict_stock_price(symbol: str):
    """Get ML price prediction for a single stock"""
    try:
        predictor = StockPredictor()
        result = predictor.predict_next_day(symbol)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to generate prediction for {symbol}. Insufficient data or invalid symbol."
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/ml/portfolio-predictions/{user_id}")
async def get_portfolio_predictions(user_id: int, db: Session = Depends(get_db)):
    """Get ML predictions for all holdings in a user's portfolio"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    holdings = db.query(Holding).filter(Holding.user_id == user.id).all()

    if not holdings:
        raise HTTPException(status_code=404, detail="No holdings found for this user")

    predictor = StockPredictor()
    predictions = []

    for holding in holdings:
        try:
            prediction = predictor.predict_next_day(holding.symbol)
            if prediction:
                predictions.append({
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "current_price": prediction['current_price'],
                    "predicted_price": prediction['predicted_price'],
                    "change_pct": prediction['change_pct'],
                    "confidence": prediction['confidence'],
                    "potential_gain_loss": (prediction['predicted_price'] - prediction['current_price']) * holding.quantity
                })
        except Exception as e:
            print(f"Error predicting for {holding.symbol}: {str(e)}")
            continue
    
    return {
        "user_id": user.id,
        "predictions_count": len(predictions),
        "predictions": predictions
    }

@router.get("/ml/sentiment/{symbol}")
async def get_stock_sentiment(symbol: str):
    """Get news sentiment analysis for a stock"""
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_stock_sentiment(symbol)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/ml/portfolio-insights/{user_id}")
async def get_portfolio_insights(user_id: int, db: Session = Depends(get_db)):
    """Get sentiment insights for all holdings in a user's portfolio"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    holdings = db.query(Holding).filter(Holding.user_id == user.id).all()

    if not holdings:
        raise HTTPException(status_code=404, detail="No holdings found for this user")
    
    predictor = StockPredictor()
    analyzer = SentimentAnalyzer()
    insights = []

    for holding in holdings:
        try:
            prediction = predictor.predict_next_day(holding.symbol)
            sentiment = analyzer.analyze_stock_sentiment(holding.symbol)
            if prediction:
                insights.append({
                    "symbol": holding.symbol,
                    "quantity": holding.quantity,
                    "prediction": prediction,
                    "sentiment": sentiment
                })
        except Exception as e:
            print(f"Error analyzing {holding.symbol}: {str(e)}")
            continue
    
    return {
        "user_id": user.id,
        "insights_count": len(insights),
        "insights": insights
    }