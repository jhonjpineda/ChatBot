"""
Dependencias de FastAPI para autenticación.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.services.auth_service import AuthService
from app.models.user import User, UserRole

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependencia que obtiene el usuario actual desde el token JWT.
    Lanza excepción si el token es inválido.
    """
    auth_service = AuthService()
    token = credentials.credentials

    token_data = auth_service.decode_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_user_by_id(token_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Dependencia opcional que obtiene el usuario si hay token,
    pero no falla si no hay token.
    """
    if credentials is None:
        return None

    auth_service = AuthService()
    token = credentials.credentials

    token_data = auth_service.decode_token(token)

    if token_data is None:
        return None

    user = auth_service.get_user_by_id(token_data.user_id)

    return user if user and user.active else None

def require_role(allowed_roles: list[UserRole]):
    """
    Decorador de dependencia que requiere roles específicos.
    Uso: current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OWNER]))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de estos roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker

# Shortcuts para roles comunes
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Solo admins"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user

def require_owner_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Owners o admins"""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de owner o administrador"
        )
    return current_user

def require_editor_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Editors, owners o admins"""
    if current_user.role not in [UserRole.ADMIN, UserRole.OWNER, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de editor o superior"
        )
    return current_user
