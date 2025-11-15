"""
API de autenticación y gestión de usuarios con PostgreSQL
Incluye sistema de aprobación de usuarios
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.connection import get_db
from app.services.auth_service_db import AuthServiceDB
from app.schemas.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    Token, UserRole, UserApprovalUpdate, PendingUserResponse
)
from app.core.dependencies import (
    get_current_user_db, require_admin_db,
    require_owner_or_admin_db
)

router = APIRouter()


# ============================================================================
# Autenticación
# ============================================================================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.

    **Importante:**
    - El usuario queda en estado `pending_approval=True`
    - Un ADMIN debe aprobar el usuario antes de que pueda acceder
    - Se retorna un mensaje de confirmación (NO un token)

    Solo usuarios con rol VIEWER pueden registrarse públicamente.
    Para crear usuarios con otros roles, usa el endpoint de creación de usuarios (solo ADMIN).
    """
    auth_service = AuthServiceDB(db)

    # Solo permitir registro público como VIEWER
    if user_data.role != UserRole.VIEWER:
        user_data.role = UserRole.VIEWER

    try:
        user = auth_service.register(user_data, auto_approve=False)

        return {
            "message": "Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador.",
            "user_id": str(user.user_id),
            "email": user.email,
            "pending_approval": True
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve un JWT token.

    Requisitos:
    - Usuario debe estar aprobado (`pending_approval=False`)
    - Usuario debe estar activo (`active=True`)
    """
    auth_service = AuthServiceDB(db)

    try:
        user = auth_service.login(credentials)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generar token
        access_token = auth_service.create_access_token(user)

        # Respuesta
        user_response = UserResponse.from_orm(user)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user_db)):
    """Obtiene la información del usuario actual"""
    return UserResponse.from_orm(current_user)


# ============================================================================
# Gestión de usuarios
# ============================================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    include_pending: bool = False,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Lista usuarios aprobados.

    Args:
        include_pending: Si True, incluye usuarios pendientes (solo ADMIN)

    Permisos:
    - ADMIN: Ve todos los usuarios
    - OWNER: Solo usuarios de su organización
    """
    auth_service = AuthServiceDB(db)

    # Owner solo puede incluir pending de su org
    if include_pending and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo ADMIN puede ver usuarios pendientes de todas las organizaciones"
        )

    # Si es admin, ve todos. Si es owner, solo de su organización
    organization_id = None if current_user.role == UserRole.ADMIN else str(current_user.organization_id)

    users = auth_service.list_users(
        organization_id=organization_id,
        include_pending=include_pending
    )

    return [UserResponse.from_orm(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreate,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario (solo ADMIN/OWNER).

    A diferencia de `/register`:
    - Crea usuarios pre-aprobados (`pending_approval=False`)
    - Puede crear usuarios con cualquier rol
    - Solo accesible por ADMIN/OWNER

    Permisos:
    - ADMIN: Puede crear usuarios en cualquier organización
    - OWNER: Solo en su propia organización
    """
    auth_service = AuthServiceDB(db)

    # Owner solo puede crear en su organización
    if current_user.role == UserRole.OWNER:
        user_data.organization_id = current_user.organization_id

    try:
        user = auth_service.register(user_data, auto_approve=True)
        return UserResponse.from_orm(user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """Actualiza un usuario (solo ADMIN/OWNER)"""
    auth_service = AuthServiceDB(db)

    # Verificar que el usuario exista
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

    return UserResponse.from_orm(updated_user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user = Depends(require_admin_db),
    db: Session = Depends(get_db)
):
    """Elimina un usuario (solo ADMIN)"""
    auth_service = AuthServiceDB(db)

    # No permitir auto-eliminación
    if user_id == str(current_user.user_id):
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


# ============================================================================
# Sistema de aprobación de usuarios
# ============================================================================

@router.get("/users/pending/list", response_model=List[PendingUserResponse])
async def list_pending_users(
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Lista usuarios pendientes de aprobación.

    Permisos:
    - ADMIN: Ve todos los pendientes
    - OWNER: Solo pendientes de su organización
    """
    auth_service = AuthServiceDB(db)

    # Si es admin, ve todos. Si es owner, solo de su organización
    organization_id = None if current_user.role == UserRole.ADMIN else str(current_user.organization_id)

    pending_users = auth_service.get_pending_users(organization_id=organization_id)

    # Calcular horas de espera
    now = datetime.utcnow()
    result = []
    for user in pending_users:
        hours_waiting = (now - user.created_at).total_seconds() / 3600
        result.append(
            PendingUserResponse(
                user_id=user.user_id,
                email=user.email,
                username=user.username,
                role=user.role,
                created_at=user.created_at,
                hours_waiting=round(hours_waiting, 1)
            )
        )

    return result


@router.get("/users/pending/count", response_model=dict)
async def get_pending_count(
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Obtiene el número de usuarios pendientes de aprobación.

    Útil para mostrar badge de notificación en el frontend.
    """
    auth_service = AuthServiceDB(db)

    organization_id = None if current_user.role == UserRole.ADMIN else str(current_user.organization_id)

    count = auth_service.get_pending_users_count(organization_id=organization_id)

    return {"pending_count": count}


@router.post("/users/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: str,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Aprueba un usuario pendiente.

    El usuario podrá hacer login después de ser aprobado.

    Permisos:
    - ADMIN: Puede aprobar cualquier usuario
    - OWNER: Solo usuarios de su organización
    """
    auth_service = AuthServiceDB(db)

    # Verificar que el usuario exista
    target_user = auth_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Owner solo puede aprobar usuarios de su organización
    if current_user.role == UserRole.OWNER:
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes aprobar usuarios de otra organización"
            )

    try:
        approved_user = auth_service.approve_user(user_id, str(current_user.user_id))
        if not approved_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return UserResponse.from_orm(approved_user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/users/{user_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_user(
    user_id: str,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """
    Rechaza y elimina un usuario pendiente.

    El usuario será eliminado de la base de datos.

    Permisos:
    - ADMIN: Puede rechazar cualquier usuario
    - OWNER: Solo usuarios de su organización
    """
    auth_service = AuthServiceDB(db)

    # Verificar que el usuario exista
    target_user = auth_service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Owner solo puede rechazar usuarios de su organización
    if current_user.role == UserRole.OWNER:
        if target_user.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes rechazar usuarios de otra organización"
            )

    try:
        success = auth_service.reject_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Activación/Desactivación de usuarios
# ============================================================================

@router.post("/users/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """Activa un usuario desactivado"""
    auth_service = AuthServiceDB(db)

    user = auth_service.activate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return UserResponse.from_orm(user)


@router.post("/users/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    current_user = Depends(require_owner_or_admin_db),
    db: Session = Depends(get_db)
):
    """Desactiva un usuario"""
    auth_service = AuthServiceDB(db)

    # No permitir auto-desactivación
    if user_id == str(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )

    user = auth_service.deactivate_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    return UserResponse.from_orm(user)
