"""
Servicio de autenticación con PostgreSQL y SQLAlchemy
Incluye sistema de aprobación de usuarios
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os
from dotenv import load_dotenv
import uuid

from app.database.models import User as UserModel
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserRole
from app.schemas.user import PendingUserResponse

load_dotenv()

# Configuración JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 días

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthServiceDB:
    """Servicio de autenticación con PostgreSQL"""

    def __init__(self, db: Session):
        self.db = db

    # ========================================================================
    # Hash de contraseñas
    # ========================================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)

    # ========================================================================
    # JWT Tokens
    # ========================================================================

    @staticmethod
    def create_access_token(user: UserModel) -> str:
        """Crea un JWT token para un usuario"""
        expires_delta = timedelta(minutes=JWT_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": str(user.user_id),
            "email": user.email,
            "role": user.role,
            "exp": expire
        }

        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decodifica un JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.JWTError:
            return None

    # ========================================================================
    # Registro de usuarios
    # ========================================================================

    def register(self, user_data: UserCreate, auto_approve: bool = False) -> UserModel:
        """
        Registra un nuevo usuario.

        Args:
            user_data: Datos del usuario
            auto_approve: Si True, aprueba automáticamente (para admins creando usuarios)

        Returns:
            Usuario creado

        Nota:
            - Por defecto, usuarios quedan en pending_approval=True
            - Solo admins pueden crear con auto_approve=True
        """
        # Verificar que el email no exista
        existing_user = self.db.query(UserModel).filter(UserModel.email == user_data.email).first()
        if existing_user:
            raise ValueError(f"El email {user_data.email} ya está registrado")

        # Hash de contraseña
        hashed_password = self.hash_password(user_data.password)

        # Crear usuario
        new_user = UserModel(
            user_id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            role=user_data.role,
            organization_id=user_data.organization_id,
            allowed_bots=user_data.allowed_bots,
            pending_approval=not auto_approve,  # Si auto_approve=True, pending=False
            active=True
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    # ========================================================================
    # Login
    # ========================================================================

    def login(self, credentials: UserLogin) -> Optional[UserModel]:
        """
        Autentica un usuario.

        Returns:
            Usuario si las credenciales son válidas, None si no
        """
        user = self.db.query(UserModel).filter(UserModel.email == credentials.email).first()

        if not user:
            return None

        if not self.verify_password(credentials.password, user.password_hash):
            return None

        # Verificar que el usuario esté activo
        if not user.active:
            raise ValueError("Usuario inactivo")

        # Verificar que el usuario esté aprobado
        if user.pending_approval:
            raise ValueError("Tu cuenta está pendiente de aprobación por un administrador")

        return user

    # ========================================================================
    # Gestión de usuarios
    # ========================================================================

    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Obtiene un usuario por su ID"""
        try:
            user_uuid = uuid.UUID(user_id)
            return self.db.query(UserModel).filter(UserModel.user_id == user_uuid).first()
        except ValueError:
            return None

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Obtiene un usuario por su email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def list_users(self, organization_id: Optional[str] = None, include_pending: bool = False) -> List[UserModel]:
        """
        Lista usuarios.

        Args:
            organization_id: Filtrar por organización (None = todos)
            include_pending: Si True, incluye usuarios pendientes de aprobación

        Returns:
            Lista de usuarios
        """
        query = self.db.query(UserModel)

        if organization_id:
            try:
                org_uuid = uuid.UUID(organization_id)
                query = query.filter(UserModel.organization_id == org_uuid)
            except ValueError:
                pass

        if not include_pending:
            query = query.filter(UserModel.pending_approval == False)

        return query.all()

    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserModel]:
        """Actualiza un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Actualizar campos
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.role is not None:
            user.role = user_update.role
        if user_update.active is not None:
            user.active = user_update.active
        if user_update.allowed_bots is not None:
            user.allowed_bots = user_update.allowed_bots
        if user_update.organization_id is not None:
            user.organization_id = user_update.organization_id

        user.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True

    # ========================================================================
    # Sistema de aprobación de usuarios
    # ========================================================================

    def get_pending_users(self, organization_id: Optional[str] = None) -> List[UserModel]:
        """
        Obtiene usuarios pendientes de aprobación.

        Args:
            organization_id: Filtrar por organización (None = todos)

        Returns:
            Lista de usuarios pendientes
        """
        query = self.db.query(UserModel).filter(UserModel.pending_approval == True)

        if organization_id:
            try:
                org_uuid = uuid.UUID(organization_id)
                query = query.filter(UserModel.organization_id == org_uuid)
            except ValueError:
                pass

        return query.order_by(UserModel.created_at.asc()).all()

    def approve_user(self, user_id: str, admin_id: str) -> Optional[UserModel]:
        """
        Aprueba un usuario pendiente.

        Args:
            user_id: ID del usuario a aprobar
            admin_id: ID del admin que aprueba

        Returns:
            Usuario aprobado
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        if not user.pending_approval:
            raise ValueError("El usuario ya está aprobado")

        # Aprobar
        user.pending_approval = False
        try:
            user.approved_by = uuid.UUID(admin_id)
        except ValueError:
            user.approved_by = None
        user.approved_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user)

        return user

    def reject_user(self, user_id: str) -> bool:
        """
        Rechaza y elimina un usuario pendiente.

        Args:
            user_id: ID del usuario a rechazar

        Returns:
            True si se eliminó exitosamente
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        if not user.pending_approval:
            raise ValueError("Solo se pueden rechazar usuarios pendientes de aprobación")

        # Eliminar
        self.db.delete(user)
        self.db.commit()

        return True

    def get_pending_users_count(self, organization_id: Optional[str] = None) -> int:
        """Obtiene el número de usuarios pendientes"""
        query = self.db.query(UserModel).filter(UserModel.pending_approval == True)

        if organization_id:
            try:
                org_uuid = uuid.UUID(organization_id)
                query = query.filter(UserModel.organization_id == org_uuid)
            except ValueError:
                pass

        return query.count()

    def activate_user(self, user_id: str) -> Optional[UserModel]:
        """Activa un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.active = True
        self.db.commit()
        self.db.refresh(user)

        return user

    def deactivate_user(self, user_id: str) -> Optional[UserModel]:
        """Desactiva un usuario"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.active = False
        self.db.commit()
        self.db.refresh(user)

        return user
