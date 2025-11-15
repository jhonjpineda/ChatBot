"""
Dependencies para autenticación y autorización con PostgreSQL
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.auth_service_db import AuthServiceDB
from app.database.models import User
from app.schemas.user import UserRole

security = HTTPBearer()


def get_current_user_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT.
    Trabaja con PostgreSQL.

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials

    # Decodificar token
    payload = AuthServiceDB.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener usuario de la base de datos
    user_id = payload.get("sub")
    auth_service = AuthServiceDB(db)
    user = auth_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que esté activo
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    # Verificar que esté aprobado
    if user.pending_approval:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta está pendiente de aprobación"
        )

    return user


def require_admin_db(current_user: User = Depends(get_current_user_db)) -> User:
    """
    Dependency que requiere que el usuario sea ADMIN.

    Raises:
        HTTPException: Si el usuario no es ADMIN
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de ADMIN"
        )
    return current_user


def require_owner_or_admin_db(current_user: User = Depends(get_current_user_db)) -> User:
    """
    Dependency que requiere que el usuario sea OWNER o ADMIN.

    Raises:
        HTTPException: Si el usuario no es OWNER ni ADMIN
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de OWNER o ADMIN"
        )
    return current_user


def require_editor_or_above_db(current_user: User = Depends(get_current_user_db)) -> User:
    """
    Dependency que requiere que el usuario sea EDITOR, OWNER o ADMIN.

    Raises:
        HTTPException: Si el usuario es VIEWER
    """
    if current_user.role == UserRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de EDITOR o superior"
        )
    return current_user


def check_bot_access_db(bot_id: str, current_user: User = Depends(get_current_user_db)) -> bool:
    """
    Verifica si el usuario tiene acceso a un bot específico.

    Reglas:
    - ADMIN: acceso a todos
    - OWNER: acceso a todos de su organización
    - EDITOR/VIEWER: acceso solo a bots en allowed_bots (si está definido)

    Args:
        bot_id: ID del bot a verificar
        current_user: Usuario actual

    Returns:
        True si tiene acceso

    Raises:
        HTTPException: Si no tiene acceso
    """
    # Admin siempre tiene acceso
    if current_user.role == UserRole.ADMIN:
        return True

    # Owner y Editor/Viewer con allowed_bots
    if current_user.allowed_bots is None:
        # None = acceso a todos los bots
        return True

    if bot_id not in current_user.allowed_bots:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tienes acceso al bot '{bot_id}'"
        )

    return True
