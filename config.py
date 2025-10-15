import os
from dotenv import load_dotenv

load_dotenv()

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Configurações do banco de dados (obrigatório: não usar SQLite)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definido. Configure a variável de ambiente com a URL do PostgreSQL."
    )

# Configurações de upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "40485760"))  # 10MB

# Configurações de dispositivo
MAX_DEVICES_PER_USER = 2
