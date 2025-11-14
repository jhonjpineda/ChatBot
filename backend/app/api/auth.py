"""
API de autenticación y gestión de usuarios.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.services.auth_service import AuthService
from app.models.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    Token, User, UserRole
)
from app.core.dependencies import (
    get_current_user, require_admin,
    require_owner_or_admin
)

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Registra un nuevo usuario.
    Por defecto crea usuarios con rol VIEWER.
    Solo ADMIN puede crear usuarios con otros roles.
    """
    auth_service = AuthService()

    try:
        # Registrar usuario
        user = auth_service.register(user_data)

        # Generar token
        access_token = auth_service.create_access_token(user)

        # Respuesta sin password
        user_response = UserResponse(
            user_id=user.user_id,
            email=user.email,
            username=user.username,
            role=user.role,
            organization_id=user.organization_id,
            active=user.active,
            created_at=user.created_at,
            allowed_bots=user.allowed_bots
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Autentica un usuario y devuelve un JWT token.
    """
    auth_service = AuthService()

    user = auth_service.login(credentials)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar token
    access_token = auth_service.create_access_token(user)

    # Respuesta sin password
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        role=user.role,
        organization_id=user.organization_id,
        active=user.active,
        created_at=user.created_at,
        allowed_bots=user.allowed_bots
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual.
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        organization_id=current_user.organization_id,
        active=current_user.active,
        created_at=current_user.created_at,
        allowed_bots=current_user.allowed_bots
    )

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_owner_or_admin)
):
    """
    Lista todos los usuarios.
    Solo ADMIN puede ver todos. OWNER solo ve los de su organización.
    """
    auth_service = AuthService()

    # Si es admin, ve todos. Si es owner, solo de su organización
    organization_id = None if current_user.role == UserRole.ADMIN else current_user.organization_id

    users = auth_service.list_users(organization_id=organization_id)

    return [
        UserResponse(
            user_id=u.user_id,
            email=u.email,
            username=u.username,
            role=u.role,
            organization_id=u.organization_id,
            active=u.active,
            created_at=u.created_at,
            allowed_bots=u.allowed_bots
        )
        for u in users
    ]

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_owner_or_admin)
):
    """
    Actualiza un usuario.
    Solo ADMIN u OWNER pueden actualizar usuarios.
    """
    auth_service = AuthService()

    # Verificar permisos
    target_user = auth_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Owner solo puede editar usuarios de su organización
    if current_user.role == UserRole.OWNER:
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes editar usuarios de otra organización"
            )

    updated_user = auth_service.update_user(user_id, user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return UserResponse(
        user_id=updated_user.user_id,
        email=updated_user.email,
        username=updated_user.username,
        role=updated_user.role,
        organization_id=updated_user.organization_id,
        active=updated_user.active,
        created_at=updated_user.created_at,
        allowed_bots=updated_user.allowed_bots
    )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Elimina un usuario.
    Solo ADMIN puede eliminar usuarios.
    """
    auth_service = AuthService()

    # No permitir auto-eliminación
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )

    success = auth_service.delete_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return None
