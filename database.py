import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to local default if .env is missing or DATABASE_URL not set
    DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/kinetrexa_db"

# Create the SQLAlchemy engine
# pool_pre_ping checks connection health before issuing queries, which prevents stale connection errors
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# SessionLocal is the session factory to establish database operations session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models to inherit from
Base = declarative_base()

# Dependency to get db session in API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
