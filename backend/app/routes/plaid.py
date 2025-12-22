from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.services import plaid_service
from app.database import get_db
from app.models.user import User, Holding

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