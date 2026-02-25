"""
Configuración de la base de datos y sesiones
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

from app.config import get_settings
from app.models.models import Base

logger = logging.getLogger(__name__)

settings = get_settings()

# Crear engine
# Usar PyMySQL en lugar de MySQLdb
if settings.database_url.startswith("mysql+pymysql://"):
    database_url = settings.database_url
else:
    database_url = settings.database_url.replace("mysql://", "mysql+pymysql://")

engine = create_engine(
    database_url,
    echo=settings.database_echo,
    poolclass=NullPool,
    connect_args={"charset": "utf8mb4"},
)

# Crear session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_session() -> Session:
    """Obtener sesión de base de datos (no-async)"""
    return SessionLocal()


def close_db():
    """Cerrar conexión de base de datos"""
    engine.dispose()
