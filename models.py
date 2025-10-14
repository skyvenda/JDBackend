from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class SubscriptionType(enum.Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    ANUAL = "anual"

class UserType(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)
    tipo_subscricao = Column(Enum(SubscriptionType), nullable=True)
    tipo_usuario = Column(Enum(UserType), default=UserType.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Jornal(Base):
    __tablename__ = "jornais"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    capa = Column(String(500), nullable=True)  # URL da imagem da capa
    arquivopdf = Column(String(500), nullable=False)  # URL do arquivo PDF
    data_publicacao = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subscription_type = Column(Enum(SubscriptionType), nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    payment_method = Column(String(50), default="digital")  # digital ou fisico
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SubscriptionRequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class SubscriptionRequest(Base):
    __tablename__ = "subscription_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    subscription_type = Column(Enum(SubscriptionType), nullable=False)
    status = Column(Enum(SubscriptionRequestStatus), default=SubscriptionRequestStatus.PENDING, nullable=False)
    payment_reference = Column(String(255), nullable=True)
    observacao_admin = Column(Text, nullable=True)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TokenSession(Base):
    __tablename__ = "token_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(Text, nullable=False)
    device_info = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
