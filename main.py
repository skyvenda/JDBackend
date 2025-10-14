from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uvicorn
import os

from database import get_db, engine
from models import Base, User, Jornal, Subscription
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

@app.get("/")
async def root():
    return {"message": "Jornal Destaque API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
