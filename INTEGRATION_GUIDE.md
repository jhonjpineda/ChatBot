# 🔗 Guía de Integración del Sistema de Autenticación

Cómo integrar la autenticación en los endpoints existentes.

## 📋 Resumen de Cambios Necesarios

El sistema de autenticación está **listo para usar**, pero los endpoints existentes aún **no están protegidos**. Aquí te mostramos cómo protegerlos gradualmente.

## 🎯 Estrategia de Migración

### Opción A: Todo Público (Estado Actual)
✅ Sin cambios necesarios
- Útil para desarrollo y testing
- Cualquiera puede usar el sistema

### Opción B: Autenticación Opcional
✅ Recomendado para empezar
- Los endpoints funcionan sin auth
- Pero si hay token, lo validan
- Permite migración gradual

### Opción C: Autenticación Requerida
⚠️ Solo cuando estés listo
- Todos los endpoints requieren login
- Mayor seguridad
- Requiere frontend completo

## 🔧 Cómo Proteger Endpoints

### 1. Bots - Ejemplo Completo

**Antes:**
```python
# app/api/bots.py
@router.get("/")
async def list_bots():
    service = BotService()
    return {"bots": service.list_bots()}
```

**Después (Autenticación requerida):**
```python
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

@router.get("/")
async def list_bots(current_user: User = Depends(get_current_user)):
    """Lista bots. Usuarios ven solo bots permitidos, admin ve todos."""
    service = BotService()
    all_bots = service.list_bots()

    # Admin ve todos
    if current_user.role == UserRole.ADMIN:
        return {"bots": all_bots}

    # Otros ven solo bots permitidos
    if current_user.allowed_bots is None:
        return {"bots": all_bots}  # null = todos

    allowed = [b for b in all_bots if b.bot_id in current_user.allowed_bots]
    return {"bots": allowed}
```

**Después (Autenticación opcional):**
```python
from app.core.dependencies import get_optional_user

@router.get("/")
async def list_bots(current_user: User = Depends(get_optional_user)):
    """Lista bots. Si hay usuario, filtra por permisos."""
    service = BotService()
    all_bots = service.list_bots()

    # Sin auth, devuelve todos
    if not current_user:
        return {"bots": all_bots}

    # Con auth, aplica permisos
    if current_user.role == UserRole.ADMIN or current_user.allowed_bots is None:
        return {"bots": all_bots}

    allowed = [b for b in all_bots if b.bot_id in current_user.allowed_bots]
    return {"bots": allowed}
```

### 2. Documentos - Control de Acceso

```python
# app/api/documents.py
from app.core.dependencies import get_current_user, require_editor_or_above
from app.models.user import User
from app.services.auth_service import AuthService

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    bot_id: str = Query(default="default"),
    current_user: User = Depends(require_editor_or_above)  # Editor o superior
):
    """Sube documento. Requiere rol EDITOR o superior."""
    # Verificar acceso al bot
    auth_service = AuthService()
    if not auth_service.user_can_access_bot(current_user, bot_id):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para subir documentos a este bot"
        )

    service = DocumentService()
    doc_info = await service.process_upload(file, bot_id=bot_id)
    return {"message": "Documento cargado", "document": doc_info}

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(require_editor_or_above)  # Editor o superior
):
    """Elimina documento. Requiere rol EDITOR o superior."""
    service = DocumentService()
    service.delete_document(doc_id)
    return {"message": "Documento eliminado"}
```

### 3. Chat - Tracking por Usuario

```python
# app/api/chat.py
from app.core.dependencies import get_optional_user

@router.post("/stream")
def chat_stream_endpoint(
    payload: ChatRequest,
    current_user: User = Depends(get_optional_user)  # Opcional
):
    """
    Chat con streaming.
    Si hay usuario autenticado, registra analytics con user_id.
    """
    # Verificar acceso al bot si hay usuario
    if current_user:
        auth_service = AuthService()
        if not auth_service.user_can_access_bot(current_user, payload.bot_id):
            raise HTTPException(
                status_code=403,
                detail="No tienes acceso a este bot"
            )

    chat_service = get_chat_service()

    # Pasar user_id a analytics si está autenticado
    user_id = current_user.user_id if current_user else None

    return StreamingResponse(
        chat_service.answer_stream(
            payload.question,
            payload.bot_id,
            user_id=user_id  # Nuevo parámetro
        ),
        media_type="text/event-stream"
    )
```

### 4. Analytics - Control por Organización

```python
# app/api/analytics.py
from app.core.dependencies import get_current_user

@router.get("/bot/{bot_id}")
async def get_bot_analytics(
    bot_id: str,
    days: int = Query(default=30),
    current_user: User = Depends(get_current_user)  # Requerido
):
    """Analytics de bot. Solo usuarios con acceso al bot."""
    # Verificar acceso
    auth_service = AuthService()
    if not auth_service.user_can_access_bot(current_user, bot_id):
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a analytics de este bot"
        )

    service = AnalyticsService()
    stats = service.get_bot_stats(bot_id, days=days)
    return {"stats": stats}

@router.get("/global")
async def get_global_analytics(
    days: int = Query(default=30),
    current_user: User = Depends(require_admin)  # Solo admin
):
    """Analytics globales. Solo admin."""
    service = AnalyticsService()
    stats = service.get_global_stats(days=days)
    return {"stats": stats}
```

## 📊 Matriz de Permisos Recomendada

| Endpoint | ADMIN | OWNER | EDITOR | VIEWER | Sin Auth |
|----------|-------|-------|--------|--------|----------|
| **Auth** |
| POST /auth/register | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET /auth/me | ✅ | ✅ | ✅ | ✅ | ❌ |
| GET /auth/users | ✅ | ✅* | ❌ | ❌ | ❌ |
| **Bots** |
| GET /bots | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| POST /bots | ✅ | ✅ | ❌ | ❌ | ❌ |
| PATCH /bots/{id} | ✅ | ✅ | ✅** | ❌ | ❌ |
| DELETE /bots/{id} | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Documentos** |
| GET /documents/list | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| POST /documents/upload | ✅ | ✅ | ✅ | ❌ | ❌ |
| DELETE /documents/{id} | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Chat** |
| POST /chat/stream | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **Analytics** |
| GET /analytics/bot/{id} | ✅ | ✅ | ✅ | ✅ | ❌ |
| GET /analytics/global | ✅ | ❌ | ❌ | ❌ | ❌ |
| GET /analytics/word-cloud | ✅ | ✅ | ✅ | ✅ | ❌ |

**Leyenda:**
- ✅ Permitido
- ❌ Prohibido
- ⚠️ Permitido pero sin control de acceso (estado actual)
- \* Solo usuarios de su organización
- \*\* Solo bots asignados

## 🚀 Plan de Migración Paso a Paso

### Fase 1: Backend Básico (Ya está ✅)
- [x] Modelos de usuario
- [x] Servicio de auth
- [x] Endpoints de auth
- [x] Dependencias de protección

### Fase 2: Protección Opcional (Recomendado empezar aquí)
- [ ] Agregar `get_optional_user` a endpoints críticos
- [ ] Implementar verificación de `user_can_access_bot`
- [ ] Registrar `user_id` en analytics

### Fase 3: Protección Completa
- [ ] Requerir autenticación en todos los endpoints
- [ ] Implementar control granular de permisos
- [ ] Auditoría de todas las acciones

### Fase 4: Frontend
- [ ] Página de login/register
- [ ] Guardar token en localStorage
- [ ] Interceptor de axios
- [ ] Protección de rutas
- [ ] UI de gestión de usuarios (solo admin)

## 💡 Ejemplo: Migración del Endpoint de Chat

### Paso 1: Sin Cambios (Actual)
```python
@router.post("/stream")
def chat_stream_endpoint(payload: ChatRequest):
    # ... código actual ...
```

### Paso 2: Auth Opcional
```python
@router.post("/stream")
def chat_stream_endpoint(
    payload: ChatRequest,
    current_user: User = Depends(get_optional_user)
):
    # Verificar acceso si hay usuario
    if current_user:
        auth_service = AuthService()
        if not auth_service.user_can_access_bot(current_user, payload.bot_id):
            raise HTTPException(status_code=403, detail="Sin acceso a este bot")

    # ... resto del código ...
    # Opcionalmente registrar user_id en analytics
```

### Paso 3: Auth Requerida
```python
@router.post("/stream")
def chat_stream_endpoint(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)  # Ahora requerido
):
    # Siempre verificar acceso
    auth_service = AuthService()
    if not auth_service.user_can_access_bot(current_user, payload.bot_id):
        raise HTTPException(status_code=403, detail="Sin acceso a este bot")

    # ... resto del código ...
    # Siempre registrar user_id en analytics
```

## 🧪 Testing con Auth

```bash
# 1. Login y obtener token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chatbot.com","password":"admin123"}' \
  | python -m json.tool | grep access_token | cut -d'"' -f4)

# 2. Usar en requests
curl http://localhost:8000/bots \
  -H "Authorization: Bearer $TOKEN"

# 3. Test sin token (debería fallar si está protegido)
curl http://localhost:8000/bots
```

## 📝 Notas Importantes

1. **No rompas el sistema actual**: Empieza con `get_optional_user`
2. **Prueba gradualmente**: Protege un endpoint a la vez
3. **Documenta**: Actualiza la API docs cuando cambies permisos
4. **Comunica**: Avisa a los usuarios cuando requieras auth

## 🎯 Siguiente Paso Recomendado

Empieza protegiendo solo los endpoints de escritura:
- POST /documents/upload
- DELETE /documents/{id}
- POST /bots
- PATCH /bots/{id}
- DELETE /bots/{id}

Deja los de lectura abiertos por ahora:
- GET /bots
- GET /documents/list
- POST /chat/stream (lectura virtual)
