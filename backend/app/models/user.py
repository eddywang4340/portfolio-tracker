from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    plaid_access_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    symbol = Column(String)
    quantity = Column(Float)
    cost_basis = Column(Float)
    current_price = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))