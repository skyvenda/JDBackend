from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, Jornal, Subscription, SubscriptionType, SubscriptionRequest, SubscriptionRequestStatus
from schemas import (
    UserCreate, UserLogin, UserResponse, JornalResponse, SubscriptionCreate, Token,
    SubscriptionRequestCreate, SubscriptionRequestResponse
)
from auth import (
    authenticate_user, 
    get_password_hash, 
    get_current_user, 
    create_access_token, 
    create_token_session,
    timedelta
)
from file_handler import get_file_url

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário"""
    
    # Verifica se email já existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Cria o usuário
    hashed_password = get_password_hash(user.senha)
    db_user = User(
        nome=user.nome,
        telefone=user.telefone,
        email=user.email,
        senha=hashed_password,
        tipo_subscricao=user.tipo_subscricao
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login do usuário"""
    user = authenticate_user(user_credentials.email, user_credentials.senha, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Cria token de acesso
    access_token_expires = timedelta(minutes=1440)  # 24 horas
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Cria sessão de token
    create_token_session(user.id, access_token, db)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 86400  # 24 horas em segundos
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtém informações do usuário atual"""
    return current_user

@router.get("/jornais", response_model=List[JornalResponse])
async def list_jornais(
    skip: int = 0, 
    limit: int = 100, 
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Lista jornais disponíveis com filtro por data"""
    query = db.query(Jornal).filter(Jornal.is_active == True)
    
    # Filtro por data
    if data_inicio:
        try:
            data_inicio_dt = datetime.fromisoformat(data_inicio.replace('Z', '+00:00'))
            query = query.filter(Jornal.data_publicacao >= data_inicio_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido")
    
    if data_fim:
        try:
            data_fim_dt = datetime.fromisoformat(data_fim.replace('Z', '+00:00'))
            query = query.filter(Jornal.data_publicacao <= data_fim_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido")
    
    jornais = query.offset(skip).limit(limit).all()
    
    # Converte para response com URLs completas
    jornal_responses = []
    for jornal in jornais:
        jornal_response = JornalResponse(
            id=jornal.id,
            titulo=jornal.titulo,
            capa=get_file_url(jornal.capa) if jornal.capa else None,
            arquivopdf=get_file_url(jornal.arquivopdf),
            data_publicacao=jornal.data_publicacao,
            is_active=jornal.is_active,
            created_at=jornal.created_at,
            updated_at=jornal.updated_at
        )
        jornal_responses.append(jornal_response)
    
    return jornal_responses

@router.get("/public/jornais", response_model=List[JornalResponse])
async def list_public_jornais(
    skip: int = 0,
    limit: int = 100,
    busca: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista jornais públicos (sem login) com busca e filtro de data (AAAA-MM-DD)."""
    query = db.query(Jornal).filter(Jornal.is_active == True)

    if busca:
        query = query.filter(Jornal.titulo.ilike(f"%{busca}%"))

    # Filtro por data (espera formato YYYY-MM-DD)
    if data_inicio:
        try:
            dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            query = query.filter(Jornal.data_publicacao >= dt_inicio)
        except ValueError:
            raise HTTPException(status_code=400, detail="data_inicio inválida. Use AAAA-MM-DD")
    if data_fim:
        try:
            dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
            query = query.filter(Jornal.data_publicacao <= dt_fim)
        except ValueError:
            raise HTTPException(status_code=400, detail="data_fim inválida. Use AAAA-MM-DD")

    jornais = query.order_by(Jornal.data_publicacao.desc()).offset(skip).limit(limit).all()

    jornal_responses = []
    for jornal in jornais:
        jornal_responses.append(JornalResponse(
            id=jornal.id,
            titulo=jornal.titulo,
            capa=get_file_url(jornal.capa) if jornal.capa else None,
            arquivopdf=get_file_url(jornal.arquivopdf),
            data_publicacao=jornal.data_publicacao,
            is_active=jornal.is_active,
            created_at=jornal.created_at,
            updated_at=jornal.updated_at
        ))

    return jornal_responses

@router.get("/jornais/{jornal_id}", response_model=JornalResponse)
async def get_jornal(jornal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtém um jornal específico"""
    jornal = db.query(Jornal).filter(Jornal.id == jornal_id, Jornal.is_active == True).first()
    if not jornal:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    
    # Verifica se o usuário tem acesso ao jornal
    has_access = check_jornal_access(current_user, jornal, db)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este jornal"
        )
    
    # Converte para response com URLs completas
    jornal_response = JornalResponse(
        id=jornal.id,
        titulo=jornal.titulo,
        capa=get_file_url(jornal.capa) if jornal.capa else None,
        arquivopdf=get_file_url(jornal.arquivopdf),
        data_publicacao=jornal.data_publicacao,
        is_active=jornal.is_active,
        created_at=jornal.created_at,
        updated_at=jornal.updated_at
    )
    
    return jornal_response

@router.post("/subscriptions", response_model=dict)
async def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Cria uma assinatura digital"""
    
    # Calcula data de término baseada no tipo de assinatura
    start_date = datetime.utcnow()
    
    if subscription.subscription_type == SubscriptionType.DIARIO:
        end_date = start_date + timedelta(days=1)
    elif subscription.subscription_type == SubscriptionType.SEMANAL:
        end_date = start_date + timedelta(weeks=1)
    elif subscription.subscription_type == SubscriptionType.MENSAL:
        end_date = start_date + timedelta(days=30)
    elif subscription.subscription_type == SubscriptionType.ANUAL:
        end_date = start_date + timedelta(days=365)
    
    # Cria a assinatura
    db_subscription = Subscription(
        user_id=current_user.id,
        subscription_type=subscription.subscription_type,
        start_date=start_date,
        end_date=end_date,
        payment_method="digital"
    )
    
    db.add(db_subscription)
    
    # Atualiza o tipo de assinatura do usuário
    current_user.tipo_subscricao = subscription.subscription_type
    
    db.commit()
    db.refresh(db_subscription)
    
    return {
        "message": "Assinatura criada com sucesso",
        "subscription": db_subscription
    }

@router.get("/my-subscriptions", response_model=List[dict])
async def get_my_subscriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtém as assinaturas do usuário atual"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.is_active == True
    ).all()
    
    result = []
    for sub in subscriptions:
        result.append({
            "id": sub.id,
            "subscription_type": sub.subscription_type,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "is_active": sub.is_active and sub.end_date > datetime.utcnow(),
            "payment_method": sub.payment_method,
            "created_at": sub.created_at
        })
    
    return result

# -------------------- Subscription Requests (Pedidos) --------------------

@router.post("/subscriptions/requests", response_model=SubscriptionRequestResponse)
async def create_subscription_request(
    body: SubscriptionRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um pedido de assinatura para revisão do admin"""

    req = SubscriptionRequest(
        user_id=current_user.id,
        subscription_type=body.subscription_type,
        status=SubscriptionRequestStatus.PENDING,
        payment_reference=body.payment_reference,
    )

    db.add(req)
    db.commit()
    db.refresh(req)
    return req

@router.get("/subscriptions/requests/my", response_model=List[SubscriptionRequestResponse])
async def list_my_subscription_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista pedidos do usuário atual"""
    reqs = db.query(SubscriptionRequest).filter(SubscriptionRequest.user_id == current_user.id).order_by(SubscriptionRequest.created_at.desc()).all()
    return reqs

def check_jornal_access(user: User, jornal: Jornal, db: Session) -> bool:
    """Verifica se o usuário tem acesso ao jornal"""
    
    # Se o usuário tem uma assinatura ativa
    if user.tipo_subscricao:
        active_subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.is_active == True,
            Subscription.end_date > datetime.utcnow()
        ).first()
        
        if active_subscription:
            return True
    
    # Se o jornal é do dia atual (acesso gratuito)
    jornal_date = jornal.data_publicacao.date()
    today = datetime.utcnow().date()
    
    if jornal_date == today:
        return True
    
    return False

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout do usuário (invalida sessões ativas)"""
    from models import TokenSession
    
    # Marca todas as sessões do usuário como inativas
    sessions = db.query(TokenSession).filter(
        TokenSession.user_id == current_user.id,
        TokenSession.is_active == True
    ).all()
    
    for session in sessions:
        session.is_active = False
    
    db.commit()
    
    return {"message": "Logout realizado com sucesso"}
