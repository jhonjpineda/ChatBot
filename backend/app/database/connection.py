"""
Configuración de conexión a PostgreSQL con SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db"
)

# Configuración del engine con pool de conexiones
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=int(os.getenv("DATABASE_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "20")),
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"  # Log SQL queries en desarrollo
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.
    Uso en FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Se ejecuta al iniciar la aplicación.
    """
    from app.database.base import Base
    # Importar todos los modelos para que SQLAlchemy los registre
    from app.database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos creadas exitosamente")
