# Sistema de Autenticación y Autorización

Sistema completo de autenticación con JWT (JSON Web Tokens) y control de acceso basado en roles (RBAC).

## 🔐 Características

- **Autenticación JWT**: Tokens seguros con expiración de 7 días
- **Hashing de contraseñas**: bcrypt para máxima seguridad
- **Control de acceso basado en roles (RBAC)**: 4 niveles de permisos
- **Multi-tenancy**: Soporte para organizaciones aisladas
- **Permisos granulares**: Control de acceso por bot
- **Usuario admin por defecto**: Configuración automática

## 👥 Roles y Permisos

### 1. **ADMIN** (Administrador)
- Acceso total al sistema
- Puede crear/editar/eliminar cualquier usuario
- Puede gestionar todas las organizaciones
- Acceso a todos los bots
- Puede ver analytics globales

### 2. **OWNER** (Propietario)
- Administrador de su organización
- Puede crear/editar usuarios de su organización
- Puede crear y gestionar bots de su organización
- Acceso a analytics de su organización
- No puede acceder a otras organizaciones

### 3. **EDITOR** (Editor)
- Puede editar bots y documentos
- Puede subir/eliminar documentos
- Puede modificar configuraciones de bots
- Acceso de lectura a analytics
- Solo bots asignados (si `allowed_bots` está definido)

### 4. **VIEWER** (Visualizador)
- Solo lectura
- Puede ver bots y usar el chat
- Puede ver analytics
- No puede modificar nada
- Solo bots asignados (si `allowed_bots` está definido)

## 📡 Endpoints de Autenticación

### Registro
```http
POST /auth/register
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "username": "Usuario Ejemplo",
  "password": "password123",
  "role": "viewer",  // opcional, por defecto "viewer"
  "organization_id": "org-123",  // opcional
  "allowed_bots": ["bot1", "bot2"]  // opcional, null = todos
}
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid-aqui",
    "email": "usuario@ejemplo.com",
    "username": "Usuario Ejemplo",
    "role": "viewer",
    "organization_id": "org-123",
    "active": true,
    "created_at": "2025-11-13T20:00:00",
    "allowed_bots": ["bot1", "bot2"]
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

**Respuesta:** Igual que registro

### Obtener usuario actual
```http
GET /auth/me
Authorization: Bearer {token}
```

### Listar usuarios
```http
GET /auth/users
Authorization: Bearer {token}
```
*Requiere rol OWNER o ADMIN*

### Actualizar usuario
```http
PATCH /auth/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "Nuevo Nombre",
  "role": "editor",
  "active": true,
  "allowed_bots": ["bot1", "bot2", "bot3"]
}
```
*Requiere rol OWNER o ADMIN*

### Eliminar usuario
```http
DELETE /auth/users/{user_id}
Authorization: Bearer {token}
```
*Requiere rol ADMIN*

## 🔒 Protección de Endpoints

### Ejemplo básico - Requiere autenticación
```python
from app.core.dependencies import get_current_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hola {current_user.username}"}
```

### Requiere rol específico
```python
from app.core.dependencies import require_admin

@router.post("/admin-only")
async def admin_route(current_user: User = Depends(require_admin)):
    return {"message": "Solo admins pueden ver esto"}
```

### Requiere uno de varios roles
```python
from app.core.dependencies import require_role
from app.models.user import UserRole

@router.post("/editors-or-admins")
async def editor_route(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.EDITOR]))
):
    return {"message": "Editors y admins"}
```

### Autenticación opcional
```python
from app.core.dependencies import get_optional_user

@router.get("/maybe-protected")
async def optional_auth(current_user: User = Depends(get_optional_user)):
    if current_user:
        return {"message": f"Hola {current_user.username}"}
    return {"message": "Hola invitado"}
```

## 🗄️ Almacenamiento

Los usuarios se guardan en `users.json`:
```json
{
  "users": [
    {
      "user_id": "uuid",
      "email": "admin@chatbot.com",
      "username": "Admin",
      "hashed_password": "$2b$12$...",
      "role": "admin",
      "organization_id": null,
      "active": true,
      "created_at": "2025-11-13T20:00:00",
      "updated_at": "2025-11-13T20:00:00",
      "allowed_bots": null
    }
  ]
}
```

## 🚀 Usuario Admin por Defecto

Al iniciar el backend por primera vez, se crea automáticamente:

```
Email: admin@chatbot.com
Password: admin123
Rol: ADMIN
```

**⚠️ IMPORTANTE**: Cambia esta contraseña en producción.

## 🔐 Seguridad

### JWT Secret Key
Por defecto usa una clave de ejemplo. En producción, configura:

```bash
# .env
JWT_SECRET_KEY=tu-clave-super-secreta-generada-con-openssl
```

Genera una clave segura:
```bash
openssl rand -hex 32
```

### Configuración de expiración
Token expira en 7 días por defecto. Modifica en `auth_service.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días
```

## 📱 Uso desde el Frontend

### Login
```typescript
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@ejemplo.com',
    password: 'password123'
  })
});

const data = await response.json();
// Guardar token
localStorage.setItem('token', data.access_token);
localStorage.setItem('user', JSON.stringify(data.user));
```

### Llamadas autenticadas
```typescript
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8000/protected-route', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 🔄 Flujo de Autenticación

1. **Usuario se registra o hace login**
   - POST /auth/register o POST /auth/login
   - Backend valida credenciales
   - Backend genera JWT token
   - Frontend guarda token en localStorage

2. **Usuario hace requests autenticados**
   - Frontend incluye token en header Authorization
   - Backend valida token en cada request
   - Backend extrae user_id del token
   - Backend verifica permisos según rol

3. **Token expira**
   - Después de 7 días, el token deja de ser válido
   - Usuario debe hacer login nuevamente
   - Frontend detecta error 401 y redirige a login

## 🎯 Casos de Uso

### Caso 1: SaaS Multi-tenant
```python
# Organización A
user_a = UserCreate(
    email="admin-a@empresa-a.com",
    username="Admin A",
    password="password",
    role=UserRole.OWNER,
    organization_id="org-a"
)

# Organización B
user_b = UserCreate(
    email="admin-b@empresa-b.com",
    username="Admin B",
    password="password",
    role=UserRole.OWNER,
    organization_id="org-b"
)
```

Cada organización solo ve sus usuarios y bots.

### Caso 2: Control granular de bots
```python
# Editor solo puede acceder a bots específicos
editor = UserCreate(
    email="editor@empresa.com",
    username="Editor",
    password="password",
    role=UserRole.EDITOR,
    allowed_bots=["soporte-tech", "ventas-bot"]  # Solo estos 2
)

# Viewer tiene acceso a todos los bots
viewer = UserCreate(
    email="viewer@empresa.com",
    username="Viewer",
    password="password",
    role=UserRole.VIEWER,
    allowed_bots=None  # null = todos
)
```

## 🛠️ Dependencias Requeridas

Agrega a `requirements.txt`:
```
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

Instala:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

## 📝 TODOs Futuros

- [ ] Refresh tokens para renovar sin re-login
- [ ] OAuth2 (Google, GitHub)
- [ ] 2FA (Two-Factor Authentication)
- [ ] Rate limiting por usuario
- [ ] Logs de auditoría (quién hizo qué)
- [ ] Password reset via email
- [ ] Sesiones múltiples (revocar tokens específicos)
- [ ] UI de administración de usuarios

## 🧪 Testing

### Test de endpoints
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"Test","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chatbot.com","password":"admin123"}'

# Get current user
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer {token}"

# List users (admin only)
curl http://localhost:8000/auth/users \
  -H "Authorization: Bearer {token}"
```
