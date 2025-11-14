"""
Modelos de datos para usuarios y autenticación.
Usando Pydantic para validación, no ORM por simplicidad.
Los datos se guardarán en JSON (users.json).
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"        # Acceso total al sistema
    OWNER = "owner"        # Puede crear/editar bots y usuarios de su organización
    EDITOR = "editor"      # Puede editar bots y documentos
    VIEWER = "viewer"      # Solo lectura

class User(BaseModel):
    """Modelo de usuario"""
    user_id: str
    email: EmailStr
    username: str
    hashed_password: str
    role: UserRole = UserRole.VIEWER
    organization_id: Optional[str] = None  # Para multi-tenancy de organizaciones
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Permisos granulares
    allowed_bots: Optional[List[str]] = None  # None = todos, [] = ninguno, [bot_ids] = específicos

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserCreate(BaseModel):
    """Datos para crear usuario"""
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.VIEWER
    organization_id: Optional[str] = None
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

class UserResponse(BaseModel):
    """Respuesta de usuario (sin password)"""
    user_id: str
    email: EmailStr
    username: str
    role: UserRole
    organization_id: Optional[str]
    active: bool
    created_at: datetime
    allowed_bots: Optional[List[str]]

class Token(BaseModel):
    """Token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: str
    email: str
    role: UserRole
