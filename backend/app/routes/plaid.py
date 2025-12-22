from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services import plaid_service, market_data
from app.database import get_db
from app.models.user import User, Holding
from datetime import datetime, timezone

router = APIRouter(prefix="/plaid", tags=["plaid"])

class ExchangeTokenRequest(BaseModel):
    public_token: str

@router.get("/create_link_token")
async def create_link_token():
    link_token = plaid_service.create_link_token()
    return {"link_token": link_token}

@router.post("/exchange_public_token")
async def exchange_token(request: ExchangeTokenRequest):
    access_token = plaid_service.exchange_public_token(request.public_token)
    return {"access_token": access_token}

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
