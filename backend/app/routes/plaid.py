from fastapi import APIRouter
from pydantic import BaseModel
from app.services import plaid_service

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