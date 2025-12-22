from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import plaid

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