from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import User, TokenSession, UserType
from database import get_db
import secrets

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MAX_DEVICES_PER_USER

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token de acesso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Verifica e decodifica o token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return {"user_id": user_id, "email": email}
    except JWTError:
        raise credentials_exception

def check_device_limit(user_id: int, db: Session, device_info: str = None):
    """Verifica se o usuário pode criar mais sessões (máximo 2 dispositivos)"""
    # Remove sessões expiradas
    expired_sessions = db.query(TokenSession).filter(
        TokenSession.user_id == user_id,
        TokenSession.expires_at < datetime.utcnow()
    ).all()
    
    for session in expired_sessions:
        session.is_active = False
    
    db.commit()
    
    # Conta sessões ativas
    active_sessions = db.query(TokenSession).filter(
        TokenSession.user_id == user_id,
        TokenSession.is_active == True,
        TokenSession.expires_at > datetime.utcnow()
    ).count()
    
    if active_sessions >= MAX_DEVICES_PER_USER:
        # Remove a sessão mais antiga
        oldest_session = db.query(TokenSession).filter(
            TokenSession.user_id == user_id,
            TokenSession.is_active == True
        ).order_by(TokenSession.created_at.asc()).first()
        
        if oldest_session:
            oldest_session.is_active = False
            db.commit()

def create_token_session(user_id: int, token: str, db: Session, device_info: str = None):
    """Cria uma nova sessão de token"""
    check_device_limit(user_id, db, device_info)
    
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_session = TokenSession(
        user_id=user_id,
        token=token,
        device_info=device_info,
        expires_at=expires_at
    )
    
    db.add(token_session)
    db.commit()
    return token_session

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtém o usuário atual baseado no token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials, credentials_exception)
    
    # Verifica se a sessão do token está ativa
    token_session = db.query(TokenSession).filter(
        TokenSession.token == credentials.credentials,
        TokenSession.is_active == True,
        TokenSession.expires_at > datetime.utcnow()
    ).first()
    
    if not token_session:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Verifica se o usuário atual é admin"""
    if current_user.tipo_usuario != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def authenticate_user(email: str, password: str, db: Session):
    """Autentica usuário com email e senha"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.senha):
        return False
    return user
