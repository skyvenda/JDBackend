import os
import logging
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Configurações do banco de dados (obrigatório: não usar SQLite in production)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definido. Configure a variável de ambiente com a URL do PostgreSQL. "
        "On Railway, add the PostgreSQL plugin and ensure the DATABASE_URL is set for the environment."
    )

# Normalize scheme: SQLAlchemy >=1.4 expects 'postgresql://' rather than 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    logging.warning(
        "DATABASE_URL uses deprecated 'postgres://' scheme — normalizing to 'postgresql://'."
    )
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Basic format validation and helpful hint for Railway internal hostnames
try:
    parsed = urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname or ""
    if not parsed.scheme or not parsed.hostname or not parsed.path:
        raise ValueError("DATABASE_URL parece estar incompleta")
    # No special handling for internal-only Railway hostnames here; DATABASE_URL should be a
    # valid, reachable Postgres URL (public or internal depending on deployment). Any DNS
    # resolution/connectivity errors will surface during startup when the app attempts to
    # connect and will be logged by the retry logic in main.py.
except Exception as e:
    raise RuntimeError(
        "DATABASE_URL inválida. Verifique a formatação: postgresql://user:pass@host:port/dbname. "
        f"Erro: {e}"
    )

# Configurações de upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "40485760"))  # 10MB

# Configurações de dispositivo
MAX_DEVICES_PER_USER = 2
