from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging

from config import DATABASE_URL


# Ensure we use SQLAlchemy-friendly scheme (config.py normalizes postgres:// -> postgresql://)
SQLALCHEMY_DATABASE_URL =DATABASE_URL

# Use pool_pre_ping so SQLAlchemy checks connections before using them (helps with dropped connections)
engine_kwargs = {
    "pool_pre_ping": True,
}

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
except Exception as e:
    logging.critical("Failed to create SQLAlchemy engine: %s", str(e))
    # Re-raise to fail fast in deployment; config.py already enforces DATABASE_URL presence
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


