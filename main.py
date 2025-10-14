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

# Criar as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jornal Destaque API", version="1.0.0")

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
