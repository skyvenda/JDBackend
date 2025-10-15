from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uvicorn
import os

from database import get_db, engine, SessionLocal
from models import Base, User, Jornal, Subscription, UserType
from schemas import UserCreate, UserLogin, JornalCreate, JornalUpdate, UserUpdate
from auth import create_access_token, verify_token, get_password_hash, verify_password
from admin_routes import router as admin_router
from user_routes import router as user_router
from config import UPLOAD_DIR

import time
import logging
from sqlalchemy.exc import OperationalError


def create_tables_with_retry(retries: int = 5, base=Base, engine=engine):
    """Attempt to create DB tables with retries and exponential backoff.

    Raises the last exception if all attempts fail.
    """
    delay = 1
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            base.metadata.create_all(bind=engine)
            logging.info("Database tables created (or already exist).")
            return
        except Exception as e:
            last_exc = e
            logging.error(
                "Attempt %d/%d: failed to create tables: %s",
                attempt,
                retries,
                str(e),
            )
            # If it's an operational error (like DNS failure), wait and retry
            time.sleep(delay)
            delay *= 2
    # all attempts failed
    logging.critical("Could not create database tables after %d attempts.", retries)
    # Re-raise the last exception so the platform can surface the failure
    raise last_exc

app = FastAPI(title="Jornal Destaque API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    """Ensure DB tables exist on startup. Use retries to tolerate transient DNS/DB startup issues (e.g., Railway)."""
    try:
        create_tables_with_retry()
    except Exception as e:
        # Log helpful advice for deployment platforms like Railway
        import sys

        logging.critical(
            "Failed to initialize database on startup: %s",
            str(e),
        )
        logging.critical(
            "Check that DATABASE_URL env var is set and that the host is reachable (for Railway, ensure you have the correct DATABASE_URL and the addon/database is running)."
        )
        # Re-raise so the process exits with non-zero status and the platform can restart or surface the issue
        raise

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(user_router, prefix="/user", tags=["user"])

# Servir arquivos estáticos
if os.path.exists(UPLOAD_DIR):
    app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

security = HTTPBearer()

@app.on_event("startup")
def ensure_default_admin():
    """Create a default admin user if none exists. Uses env vars for credentials.

    ENV:
      ADMIN_NAME, ADMIN_PHONE, ADMIN_EMAIL, ADMIN_PASSWORD
    Defaults are safe for local dev but should be overridden in production.
    """
    admin_name = os.getenv("ADMIN_NAME")
    admin_phone = os.getenv("ADMIN_PHONE")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.tipo_usuario == UserType.ADMIN).first()
        if existing_admin:
            return

        # If there's no admin, create one or promote existing email to admin
        user = db.query(User).filter(User.email == admin_email).first()
        if user:
            user.tipo_usuario = UserType.ADMIN
            # Update password if provided
            if admin_password:
                user.senha = get_password_hash(admin_password)
        else:
            user = User(
                nome=admin_name,
                telefone=admin_phone,
                email=admin_email,
                senha=get_password_hash(admin_password),
                tipo_usuario=UserType.ADMIN,
                is_active=True,
            )
            db.add(user)
        db.commit()
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Jornal Destaque API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
