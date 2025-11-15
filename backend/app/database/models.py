"""
Modelos SQLAlchemy para PostgreSQL
Basados en el diseño en DATABASE_DESIGN.md
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, Date,
    ForeignKey, ARRAY, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database.base import Base


class Organization(Base):
    """Modelo de Organización - Multi-tenancy"""
    __tablename__ = "organizations"

    organization_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    active = Column(Boolean, default=True)
    max_bots = Column(Integer, default=10)
    max_users = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    bots = relationship("Bot", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """Modelo de Usuario con sistema de aprobación"""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.organization_id", ondelete="SET NULL"))

    active = Column(Boolean, default=True)

    # Sistema de aprobación
    pending_approval = Column(Boolean, default=True, index=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"))
    approved_at = Column(DateTime(timezone=True))

    allowed_bots = Column(ARRAY(String))  # Array de bot_ids permitidos

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "role IN ('admin', 'owner', 'editor', 'viewer')",
            name="check_user_role"
        ),
    )

    # Relaciones
    organization = relationship("Organization", back_populates="users")
    approver = relationship("User", remote_side=[user_id], foreign_keys=[approved_by])
    bots_created = relationship("Bot", back_populates="creator", foreign_keys="Bot.created_by")
    conversations = relationship("Conversation", back_populates="user")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    documents_uploaded = relationship("Document", back_populates="uploader", foreign_keys="Document.uploaded_by")


class Bot(Base):
    """Modelo de Bot con configuración RAG precisa"""
    __tablename__ = "bots"

    bot_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    model_provider = Column(String(50), default='ollama')
    model_name = Column(String(100), default='llama3')

    # Configuración RAG precisa
    retrieval_threshold = Column(Float, default=0.3, comment="Mínimo de similitud para considerar un documento")
    max_sources = Column(Integer, default=5)
    strict_mode = Column(Boolean, default=True, comment="Si TRUE, solo responde con docs; si FALSE, puede usar conocimiento general")
    fallback_response = Column(Text, default='Lo siento, no tengo información sobre eso en mi base de conocimiento.')

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.organization_id", ondelete="CASCADE"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"))
    active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    organization = relationship("Organization", back_populates="bots")
    creator = relationship("User", back_populates="bots_created", foreign_keys=[created_by])
    documents = relationship("Document", back_populates="bot", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="bot", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsDaily", back_populates="bot", cascade="all, delete-orphan")


class Document(Base):
    """Modelo de Documento con metadata de procesamiento"""
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(String(100), ForeignKey("bots.bot_id", ondelete="CASCADE"), nullable=False, index=True)

    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    file_path = Column(Text, nullable=False)

    # Metadata de procesamiento
    chunks_count = Column(Integer, default=0)
    processing_status = Column(String(50), default='completed', index=True)
    error_message = Column(Text)

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    bot = relationship("Bot", back_populates="documents")
    uploader = relationship("User", back_populates="documents_uploaded", foreign_keys=[uploaded_by])


class Conversation(Base):
    """Modelo de Conversación con metadata RAG y feedback"""
    __tablename__ = "conversations"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(String(100), ForeignKey("bots.bot_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    session_id = Column(String(255), index=True)

    # Mensajes
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)

    # Metadata RAG
    sources_used = Column(Integer, default=0)
    similarity_scores = Column(ARRAY(Float))
    document_ids = Column(ARRAY(UUID(as_uuid=True)))

    # Performance
    response_time_ms = Column(Integer)
    tokens_used = Column(Integer)

    # Feedback
    user_feedback = Column(String(20))  # 'positive', 'negative', null
    feedback_comment = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relaciones
    bot = relationship("Bot", back_populates="conversations")
    user = relationship("User", back_populates="conversations")

    # Índice compuesto para búsquedas por bot y fecha
    __table_args__ = (
        Index('idx_conversations_bot_created', 'bot_id', 'created_at'),
    )


class AnalyticsDaily(Base):
    """Modelo de Analytics diarios pre-agregados"""
    __tablename__ = "analytics_daily"

    analytics_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_id = Column(String(100), ForeignKey("bots.bot_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    # Métricas diarias
    total_interactions = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    avg_response_time_ms = Column(Float)
    total_tokens_used = Column(Integer, default=0)

    # Feedback
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)

    # Fuentes RAG
    avg_sources_used = Column(Float)
    avg_similarity_score = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    bot = relationship("Bot", back_populates="analytics")

    # Constraint único para bot + date
    __table_args__ = (
        Index('idx_analytics_bot_date', 'bot_id', 'date'),
    )


class UserSession(Base):
    """Modelo de Sesión de Usuario para control JWT"""
    __tablename__ = "user_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(500))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    user = relationship("User", back_populates="sessions")
