from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import plaid
from app.models.user import Base
from app.database import engine
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(plaid.router)

@app.get("/")
def root():
    return {"message": "Portfolio Tracker API is running."}