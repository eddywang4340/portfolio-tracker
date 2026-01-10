from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy.engine import Engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portfolio.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30  # 30 second timeout (default is 5)
    },
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True to see SQL queries (helpful for debugging)
)

# Enable WAL (Write-Ahead Logging) mode for better concurrency
# This allows multiple readers while a writer is active
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
    cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes, still safe
    cursor.execute("PRAGMA cache_size=10000")  # Increase cache for better performance
    cursor.execute("PRAGMA busy_timeout=30000")  # 30 second busy timeout
    cursor.close()

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
