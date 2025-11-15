"""
Schemas Pydantic para usuarios y autenticación
Trabajan con modelos SQLAlchemy de app/database/models.py
"""
from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"        # Acceso total al sistema
    OWNER = "owner"        # Puede crear/editar bots y usuarios de su organización
    EDITOR = "editor"      # Puede editar bots y documentos
    VIEWER = "viewer"      # Solo lectura


# ============================================================================
# Schemas de Request (Entrada)
# ============================================================================

class UserCreate(BaseModel):
    """Datos para crear usuario (registro)"""
    email: EmailStr
    username: str
    password: str = Field(min_length=6, description="Mínimo 6 caracteres")
    role: UserRole = UserRole.VIEWER
    organization_id: Optional[UUID4] = None
    allowed_bots: Optional[List[str]] = None


class UserLogin(BaseModel):
    """Datos para login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Datos para actualizar usuario"""
    username: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None
    allowed_bots: Optional[List[str]] = None
    organization_id: Optional[UUID4] = None


class UserApprovalUpdate(BaseModel):
    """Datos para aprobar/rechazar usuario"""
    approved: bool = Field(description="True para aprobar, False para rechazar")


# ============================================================================
# Schemas de Response (Salida)
# ============================================================================

class UserResponse(BaseModel):
    """Respuesta de usuario (sin password)"""
    user_id: UUID4
    email: EmailStr
    username: str
    role: UserRole
    organization_id: Optional[UUID4]
    active: bool
    pending_approval: bool
    approved_at: Optional[datetime]
    created_at: datetime
    allowed_bots: Optional[List[str]]

    class Config:
        from_attributes = True  # Para trabajar con modelos SQLAlchemy


class PendingUserResponse(BaseModel):
    """Respuesta simplificada para usuarios pendientes"""
    user_id: UUID4
    email: EmailStr
    username: str
    role: UserRole
    created_at: datetime
    hours_waiting: float

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: UUID4
    email: str
    role: UserRole
