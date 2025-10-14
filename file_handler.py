import os
import uuid
from fastapi import UploadFile, HTTPException
from config import UPLOAD_DIR, MAX_FILE_SIZE
from typing import Tuple

# Tipos de arquivo permitidos
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
ALLOWED_PDF_TYPES = {"application/pdf"}

def create_upload_directories():
    """Cria os diretórios de upload se não existirem"""
    os.makedirs(f"{UPLOAD_DIR}/covers", exist_ok=True)
    os.makedirs(f"{UPLOAD_DIR}/pdfs", exist_ok=True)

def validate_file_size(file: UploadFile) -> None:
    """Valida o tamanho do arquivo"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo permitido: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

def validate_image_file(file: UploadFile) -> None:
    """Valida se o arquivo é uma imagem válida"""
    validate_file_size(file)
    
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido para capa. Tipos aceitos: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

def validate_pdf_file(file: UploadFile) -> None:
    """Valida se o arquivo é um PDF válido"""
    validate_file_size(file)
    
    if file.content_type not in ALLOWED_PDF_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não permitido para PDF. Tipo aceito: {', '.join(ALLOWED_PDF_TYPES)}"
        )

def generate_unique_filename(original_filename: str) -> str:
    """Gera um nome único para o arquivo"""
    file_extension = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

async def save_uploaded_file(file: UploadFile, file_type: str) -> str:
    """
    Salva arquivo enviado e retorna o caminho relativo
    
    Args:
        file: Arquivo enviado
        file_type: Tipo do arquivo ('cover' ou 'pdf')
    
    Returns:
        str: Caminho relativo do arquivo salvo
    """
    create_upload_directories()
    
    # Valida o arquivo baseado no tipo
    if file_type == "cover":
        validate_image_file(file)
        subfolder = "covers"
    elif file_type == "pdf":
        validate_pdf_file(file)
        subfolder = "pdfs"
    else:
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido")
    
    # Gera nome único
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, subfolder, unique_filename)
    
    # Salva o arquivo
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Retorna o caminho relativo com separador POSIX
        return f"{subfolder}/{unique_filename}"
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

def delete_file(file_path: str) -> bool:
    """
    Remove um arquivo do sistema
    
    Args:
        file_path: Caminho relativo do arquivo
    
    Returns:
        bool: True se removido com sucesso, False caso contrário
    """
    try:
        full_path = os.path.join(UPLOAD_DIR, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False

def get_file_url(file_path: str, base_url: str = "http://localhost:8000") -> str:
    """
    Gera URL completa para acessar o arquivo
    
    Args:
        file_path: Caminho relativo do arquivo
        base_url: URL base da API
    
    Returns:
        str: URL completa do arquivo
    """
    if not file_path:
        return None
    # Normaliza separadores para URL
    normalized_path = file_path.replace('\\', '/')
    return f"{base_url}/files/{normalized_path}"

def get_file_size_mb(file_path: str) -> float:
    """
    Obtém o tamanho do arquivo em MB
    
    Args:
        file_path: Caminho relativo do arquivo
    
    Returns:
        float: Tamanho em MB
    """
    try:
        full_path = os.path.join(UPLOAD_DIR, file_path)
        if os.path.exists(full_path):
            size_bytes = os.path.getsize(full_path)
            return round(size_bytes / (1024 * 1024), 2)
        return 0.0
    except Exception:
        return 0.0
