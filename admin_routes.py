from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import User, Jornal, Subscription, SubscriptionType, UserType, SubscriptionRequest, SubscriptionRequestStatus
from schemas import (
    UserCreate, UserUpdate, UserResponse, JornalCreate, JornalUpdate, JornalResponse, SubscriptionCreate, JornalCreateForm,
    SubscriptionRequestResponse, AdminModerateRequest
)
from auth import get_current_admin_user, get_password_hash, create_access_token, create_token_session, timedelta
from file_handler import save_uploaded_file, delete_file, get_file_url

router = APIRouter()

@router.post("/create-admin", response_model=UserResponse)
async def create_admin(user: UserCreate, db: Session = Depends(get_db)):
    """Cria usuário admin automaticamente"""
    
    # Verifica se já existe um admin
    existing_admin = db.query(User).filter(User.tipo_usuario == UserType.ADMIN).first()
    if existing_admin:
        # Se o email enviado é do mesmo admin, retorna o admin existente (idempotente)
        if existing_admin.email == user.email:
            return existing_admin
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin já existe no sistema"
        )
    
    # Verifica se email já existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Cria o admin
    hashed_password = get_password_hash(user.senha)
    db_user = User(
        nome=user.nome,
        telefone=user.telefone,
        email=user.email,
        senha=hashed_password,
        tipo_subscricao=user.tipo_subscricao,
        tipo_usuario=UserType.ADMIN
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/jornais", response_model=JornalResponse)
async def create_jornal(
    titulo: str = Form(...),
    capa: Optional[UploadFile] = File(None),
    arquivopdf: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Cria um novo jornal com upload de arquivos"""
    
    # Salva o arquivo PDF (obrigatório)
    pdf_path = await save_uploaded_file(arquivopdf, "pdf")
    
    # Salva a capa se fornecida
    capa_path = None
    if capa:
        capa_path = await save_uploaded_file(capa, "cover")
    
    # Cria o jornal no banco
    db_jornal = Jornal(
        titulo=titulo,
        capa=capa_path,
        arquivopdf=pdf_path
    )
    
    db.add(db_jornal)
    db.commit()
    db.refresh(db_jornal)
    
    # Converte para response com URLs completas
    jornal_response = JornalResponse(
        id=db_jornal.id,
        titulo=db_jornal.titulo,
        capa=get_file_url(db_jornal.capa) if db_jornal.capa else None,
        arquivopdf=get_file_url(db_jornal.arquivopdf),
        data_publicacao=db_jornal.data_publicacao,
        is_active=db_jornal.is_active,
        created_at=db_jornal.created_at,
        updated_at=db_jornal.updated_at
    )
    
    return jornal_response

@router.get("/jornais", response_model=List[JornalResponse])
async def list_jornais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Lista todos os jornais"""
    jornais = db.query(Jornal).offset(skip).limit(limit).all()
    
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

@router.get("/jornais/{jornal_id}", response_model=JornalResponse)
async def get_jornal(jornal_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Obtém um jornal específico"""
    jornal = db.query(Jornal).filter(Jornal.id == jornal_id).first()
    if not jornal:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    
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

@router.put("/jornais/{jornal_id}", response_model=JornalResponse)
async def update_jornal(
    jornal_id: int,
    titulo: Optional[str] = Form(None),
    capa: Optional[UploadFile] = File(None),
    arquivopdf: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Atualiza um jornal com upload de arquivos"""
    jornal = db.query(Jornal).filter(Jornal.id == jornal_id).first()
    if not jornal:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    
    # Atualiza título se fornecido
    if titulo:
        jornal.titulo = titulo
    
    # Atualiza capa se fornecida
    if capa:
        # Remove arquivo antigo se existir
        if jornal.capa:
            delete_file(jornal.capa)
        # Salva nova capa
        jornal.capa = await save_uploaded_file(capa, "cover")
    
    # Atualiza PDF se fornecido
    if arquivopdf:
        # Remove arquivo antigo se existir
        if jornal.arquivopdf:
            delete_file(jornal.arquivopdf)
        # Salva novo PDF
        jornal.arquivopdf = await save_uploaded_file(arquivopdf, "pdf")
    
    db.commit()
    db.refresh(jornal)
    
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

@router.delete("/jornais/{jornal_id}")
async def delete_jornal(jornal_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Remove um jornal (soft delete)"""
    jornal = db.query(Jornal).filter(Jornal.id == jornal_id).first()
    if not jornal:
        raise HTTPException(status_code=404, detail="Jornal não encontrado")
    
    # Remove arquivos físicos
    if jornal.capa:
        delete_file(jornal.capa)
    if jornal.arquivopdf:
        delete_file(jornal.arquivopdf)
    
    jornal.is_active = False
    db.commit()
    return {"message": "Jornal removido com sucesso"}

@router.get("/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Lista todos os usuários"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Obtém um usuário específico"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Atualiza um usuário"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Remove um usuário (soft delete)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.tipo_usuario == UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Não é possível remover um admin")
    
    user.is_active = False
    db.commit()
    return {"message": "Usuário removido com sucesso"}

@router.post("/subscriptions", response_model=dict)
async def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Cria uma assinatura para um usuário (para pagamento físico)"""
    
    # Verifica se o usuário existe
    user = db.query(User).filter(User.id == subscription.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
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
        user_id=subscription.user_id,
        subscription_type=subscription.subscription_type,
        start_date=start_date,
        end_date=end_date,
        payment_method=subscription.payment_method
    )
    
    db.add(db_subscription)
    
    # Atualiza o tipo de assinatura do usuário
    user.tipo_subscricao = subscription.subscription_type
    
    db.commit()
    db.refresh(db_subscription)
    
    return {
        "message": "Assinatura criada com sucesso",
        "subscription": db_subscription
    }

@router.get("/subscriptions", response_model=List[dict])
async def list_subscriptions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
    """Lista todas as assinaturas"""
    subscriptions = db.query(Subscription).offset(skip).limit(limit).all()
    result = []
    
    for sub in subscriptions:
        user = db.query(User).filter(User.id == sub.user_id).first()
        result.append({
            "id": sub.id,
            "user": {
                "id": user.id,
                "nome": user.nome,
                "email": user.email
            } if user else None,
            "subscription_type": sub.subscription_type,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "is_active": sub.is_active,
            "payment_method": sub.payment_method,
            "created_at": sub.created_at
        })
    
    return result

# -------------------- Subscription Requests (Pedidos) --------------------

@router.get("/subscriptions/requests", response_model=List[SubscriptionRequestResponse])
async def list_subscription_requests(
    status_filter: Optional[SubscriptionRequestStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    query = db.query(SubscriptionRequest)
    if status_filter:
        query = query.filter(SubscriptionRequest.status == status_filter)
    reqs = query.order_by(SubscriptionRequest.created_at.desc()).offset(skip).limit(limit).all()
    return reqs

@router.post("/subscriptions/requests/{request_id}/approve", response_model=SubscriptionRequestResponse)
async def approve_subscription_request(
    request_id: int,
    body: AdminModerateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    req = db.query(SubscriptionRequest).filter(SubscriptionRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if req.status != SubscriptionRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Pedido já processado")

    # Ativa assinatura do usuário conforme tipo solicitado (12 meses p/ anual; coerente com lógica existente)
    start_date = datetime.utcnow()
    if req.subscription_type == SubscriptionType.DIARIO:
        end_date = start_date + timedelta(days=1)
    elif req.subscription_type == SubscriptionType.SEMANAL:
        end_date = start_date + timedelta(weeks=1)
    elif req.subscription_type == SubscriptionType.MENSAL:
        end_date = start_date + timedelta(days=30)
    elif req.subscription_type == SubscriptionType.ANUAL:
        end_date = start_date + timedelta(days=365)
    else:
        end_date = start_date + timedelta(days=30)

    sub = Subscription(
        user_id=req.user_id,
        subscription_type=req.subscription_type,
        start_date=start_date,
        end_date=end_date,
        payment_method="fisico"
    )
    db.add(sub)

    # Atualiza usuário
    user = db.query(User).filter(User.id == req.user_id).first()
    if user:
        user.tipo_subscricao = req.subscription_type

    req.status = SubscriptionRequestStatus.APPROVED
    req.observacao_admin = body.observacao_admin
    req.approved_by = current_admin.id
    req.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(req)
    return req

@router.post("/subscriptions/requests/{request_id}/reject", response_model=SubscriptionRequestResponse)
async def reject_subscription_request(
    request_id: int,
    body: AdminModerateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    req = db.query(SubscriptionRequest).filter(SubscriptionRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if req.status != SubscriptionRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Pedido já processado")

    req.status = SubscriptionRequestStatus.REJECTED
    req.observacao_admin = body.observacao_admin
    req.approved_by = current_admin.id
    req.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(req)
    return req
