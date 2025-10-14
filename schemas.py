from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models import SubscriptionType, UserType, SubscriptionRequestStatus
from fastapi import UploadFile, File

# Schemas para User
class UserBase(BaseModel):
    nome: str
    telefone: str
    email: EmailStr

class UserCreate(UserBase):
    senha: str
    tipo_subscricao: Optional[SubscriptionType] = None

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo_subscricao: Optional[SubscriptionType] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    tipo_subscricao: Optional[SubscriptionType]
    tipo_usuario: UserType
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas para Jornal
class JornalBase(BaseModel):
    titulo: str
    capa: Optional[str] = None
    arquivopdf: str

class JornalCreate(JornalBase):
    pass

class JornalCreateForm(BaseModel):
    titulo: str
    
    class Config:
        from_attributes = True

class JornalUpdate(BaseModel):
    titulo: Optional[str] = None
    capa: Optional[str] = None
    arquivopdf: Optional[str] = None
    is_active: Optional[bool] = None

class JornalResponse(JornalBase):
    id: int
    data_publicacao: datetime
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Schemas para Subscription
class SubscriptionCreate(BaseModel):
    user_id: int
    subscription_type: SubscriptionType
    payment_method: str = "digital"

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    subscription_type: SubscriptionType
    start_date: datetime
    end_date: datetime
    is_active: bool
    payment_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schemas para SubscriptionRequest (pedido)
class SubscriptionRequestCreate(BaseModel):
    subscription_type: SubscriptionType
    payment_reference: Optional[str] = None

class SubscriptionRequestResponse(BaseModel):
    id: int
    user_id: int
    subscription_type: SubscriptionType
    status: SubscriptionRequestStatus
    payment_reference: Optional[str]
    observacao_admin: Optional[str]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class AdminModerateRequest(BaseModel):
    observacao_admin: Optional[str] = None

# Schema para Token
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
