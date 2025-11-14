# 🔐 Sistema Completo de Permisos y Gestión de Usuarios

Sistema de control de acceso basado en roles (RBAC) completamente implementado en frontend y backend.

---

## ✅ **Implementación Completada**

### **Archivos Creados:**

```
frontend/src/
├── hooks/
│   └── usePermissions.ts           ✨ Hook para verificar permisos
├── services/
│   └── users.service.ts            ✨ Servicio de gestión de usuarios
└── pages/
    └── Users.tsx                   ✨ Página de gestión de usuarios (ADMIN/OWNER)
```

### **Archivos Modificados:**

```
frontend/src/
├── App.tsx                         ➕ Ruta /users agregada
├── components/
│   └── Layout.tsx                  ➕ Link "Usuarios" (solo ADMIN/OWNER)
└── pages/
    ├── Bots.tsx                    ➕ Restricciones de UI por rol
    └── Documents.tsx               ➕ Restricciones de UI por rol
```

---

## 🎯 **Características Implementadas**

### ✅ **1. Hook de Permisos (usePermissions)**

Hook React personalizado que centraliza toda la lógica de permisos:

```typescript
const {
  // Roles
  isAdmin,
  isOwner,
  isEditor,
  isViewer,

  // Permisos de bots
  canCreateBots,
  canEditBots,
  canDeleteBots,
  canEditBot,      // Verifica bot específico + allowed_bots
  canDeleteBot,    // Verifica bot específico + allowed_bots

  // Permisos de documentos
  canUploadDocuments,
  canDeleteDocuments,

  // Permisos de usuarios
  canManageUsers,
  canCreateUsers,
  canEditUsers,
  canDeleteUsers,

  // Verificación de acceso
  canAccessBot,    // Verifica si tiene acceso a un bot

  // Usuario actual
  user,
} = usePermissions();
```

### ✅ **2. Gestión de Usuarios**

Página completa de administración de usuarios (`/users`):

**Características:**
- ✅ Tabla de usuarios con toda la información
- ✅ Stats en tiempo real (Total, Activos, Inactivos, Admins)
- ✅ Modal para crear usuarios
- ✅ Modal para editar usuarios
- ✅ Activar/Desactivar usuarios
- ✅ Eliminar usuarios (solo ADMIN)
- ✅ Filtrado por organización
- ✅ Badges de roles con colores

**Acceso:**
- Solo visible para **ADMIN** y **OWNER**
- Link aparece automáticamente en el sidebar

### ✅ **3. Restricciones de UI**

#### **Página de Bots:**
- ✅ Botón "Crear Bot" solo visible para ADMIN/OWNER
- ✅ Botón "Editar" solo visible si `canEditBot(botId)` es true
- ✅ Botón "Eliminar" solo visible si `canDeleteBot(botId)` es true
- ✅ Considera `allowed_bots` para acceso granular

#### **Página de Documentos:**
- ✅ Área de upload solo visible para EDITOR/OWNER/ADMIN
- ✅ Mensaje informativo para usuarios sin permisos
- ✅ Botón "Eliminar" solo visible para EDITOR/OWNER/ADMIN
- ✅ Botón "Mover" solo visible para EDITOR/OWNER/ADMIN

#### **Layout/Sidebar:**
- ✅ Link "Usuarios" solo visible para ADMIN/OWNER

---

## 📊 **Matriz de Permisos Implementada**

| Acción | ADMIN | OWNER | EDITOR | VIEWER |
|--------|-------|-------|--------|--------|
| **USUARIOS** |
| Ver página usuarios | ✅ | ✅ | ❌ | ❌ |
| Crear usuarios | ✅ | ✅ | ❌ | ❌ |
| Editar usuarios | ✅ | ✅ | ❌ | ❌ |
| Eliminar usuarios | ✅ | ❌ | ❌ | ❌ |
| **BOTS** |
| Ver bots | ✅ | ✅ | ✅* | ✅* |
| Crear bots | ✅ | ✅ | ❌ | ❌ |
| Editar bots | ✅ | ✅ | ✅* | ❌ |
| Eliminar bots | ✅ | ✅ | ❌ | ❌ |
| **DOCUMENTOS** |
| Ver documentos | ✅ | ✅ | ✅* | ✅* |
| Subir documentos | ✅ | ✅ | ✅* | ❌ |
| Eliminar documentos | ✅ | ✅ | ✅* | ❌ |
| Mover documentos | ✅ | ✅ | ✅* | ❌ |
| **CHAT** |
| Usar chat | ✅ | ✅ | ✅* | ✅* |
| **ANALYTICS** |
| Analytics globales | ✅ | ❌ | ❌ | ❌ |
| Analytics de bot | ✅ | ✅ | ✅* | ✅* |

**Nota:** `*` indica que solo tiene acceso a bots en su lista `allowed_bots` (si está definida)

---

## 🚀 **Flujos de Usuario**

### **Flujo 1: ADMIN crea nuevo usuario EDITOR**

1. ADMIN hace login
2. Ve link "Usuarios" en sidebar (OWNER también lo ve)
3. Hace click en "Usuarios"
4. Click en "Crear Usuario"
5. Llena formulario:
   - Nombre: "Juan Editor"
   - Email: "juan@empresa.com"
   - Contraseña: "password123"
   - Rol: **Editor**
   - Organización: "empresa-a"
   - (Allowed bots se pueden configurar después)
6. Click "Crear Usuario"
7. Usuario creado exitosamente
8. Juan puede hacer login y:
   - ✅ Ver bots (todos o solo allowed_bots)
   - ✅ Editar bots
   - ✅ Subir/eliminar documentos
   - ❌ NO puede crear/eliminar bots
   - ❌ NO puede gestionar usuarios

### **Flujo 2: VIEWER intenta subir documento**

1. VIEWER hace login
2. Ve el dashboard y todas las páginas
3. Va a "Documentos"
4. **NO VE** el área de upload
5. Ve mensaje: "Sin permisos para subir documentos"
6. Puede ver la lista de documentos
7. En la tabla, ve "Sin permisos" en lugar de botón "Eliminar"

### **Flujo 3: EDITOR con allowed_bots limitados**

Usuario creado con:
```json
{
  "role": "editor",
  "allowed_bots": ["soporte-tech", "ventas-bot"]
}
```

**Comportamiento:**
- ✅ En `/bots` ve TODOS los bots pero...
- ✅ Solo puede EDITAR "soporte-tech" y "ventas-bot"
- ❌ Otros bots no muestran botón "Editar"
- ✅ En `/documents` puede subir docs solo a esos 2 bots
- ✅ En chat puede usar solo esos 2 bots

### **Flujo 4: OWNER gestiona su organización**

1. OWNER de "empresa-a" hace login
2. Ve link "Usuarios" en sidebar
3. Click en "Usuarios"
4. Ve SOLO usuarios de "empresa-a"
5. Puede crear/editar usuarios de su org
6. ❌ NO puede eliminar usuarios (solo ADMIN)
7. ❌ NO ve usuarios de otras organizaciones

---

## 💻 **Uso del Hook en Componentes**

### **Ejemplo 1: Ocultar botón según permiso**

```tsx
import { usePermissions } from '../hooks/usePermissions';

function MyComponent() {
  const { canCreateBots } = usePermissions();

  return (
    <div>
      {canCreateBots && (
        <button onClick={handleCreate}>
          Crear Bot
        </button>
      )}
    </div>
  );
}
```

### **Ejemplo 2: Verificar acceso a bot específico**

```tsx
import { usePermissions } from '../hooks/usePermissions';

function BotCard({ bot }) {
  const { canEditBot, canDeleteBot } = usePermissions();

  return (
    <div>
      <h3>{bot.name}</h3>

      {canEditBot(bot.bot_id) && (
        <button>Editar</button>
      )}

      {canDeleteBot(bot.bot_id) && (
        <button>Eliminar</button>
      )}
    </div>
  );
}
```

### **Ejemplo 3: Mostrar mensaje según rol**

```tsx
import { usePermissions } from '../hooks/usePermissions';

function UploadArea() {
  const { canUploadDocuments } = usePermissions();

  if (!canUploadDocuments) {
    return (
      <div className="alert">
        <p>Solo usuarios con rol Editor, Owner o Admin pueden subir documentos.</p>
      </div>
    );
  }

  return <DragDropUpload />;
}
```

---

## 🎨 **UI/UX Mejorado**

### **Badges de Roles (con colores)**

```typescript
getRoleBadgeColor(role):
  - 'admin'  → bg-purple-100 text-purple-700
  - 'owner'  → bg-blue-100 text-blue-700
  - 'editor' → bg-green-100 text-green-700
  - 'viewer' → bg-gray-100 text-gray-700
```

### **Estados Activo/Inactivo**

```typescript
user.active:
  - true  → bg-green-100 text-green-700 "Activo"
  - false → bg-red-100 text-red-700 "Inactivo"
```

### **Mensajes Informativos**

Cuando un usuario no tiene permisos:
- ✅ Área de upload muestra mensaje amarillo explicativo
- ✅ Botones reemplazados por texto "Sin permisos"
- ✅ Tooltips informativos en botones deshabilitados

---

## 🔐 **Seguridad**

### **Frontend (Protección de UI)**
- ✅ Botones/áreas ocultas según permisos
- ✅ Rutas protegidas con `PrivateRoute`
- ✅ Mensajes informativos en lugar de errores crípticos

### **Backend (Protección Real)**
- ✅ Endpoints protegidos con decoradores
- ✅ Validación de permisos en cada request
- ✅ Filtrado por `organization_id`
- ✅ Validación de `allowed_bots`
- ✅ Respuestas 403 Forbidden si no tiene permisos

**IMPORTANTE:** El frontend solo OCULTA elementos, pero el backend VALIDA y RECHAZA operaciones no permitidas.

---

## 📝 **Testing del Sistema**

### **Test 1: ADMIN puede todo**

```bash
# Login como admin
Email: admin@chatbot.com
Password: admin123

# Verificar:
✅ Ve link "Usuarios" en sidebar
✅ Puede crear usuarios
✅ Puede eliminar usuarios
✅ Ve todos los usuarios de todas las organizaciones
✅ Puede crear/editar/eliminar bots
✅ Puede subir/eliminar documentos
✅ Ve analytics globales
```

### **Test 2: VIEWER solo lectura**

```bash
# Crear usuario viewer (desde admin)
# Login como viewer

# Verificar:
❌ NO ve link "Usuarios" en sidebar
❌ NO ve botón "Crear Bot"
❌ NO ve botones "Editar/Eliminar" en bots
❌ NO ve área de upload de documentos
❌ Ve mensaje "Sin permisos para subir documentos"
✅ Puede ver bots
✅ Puede ver documentos
✅ Puede usar chat
✅ Puede ver analytics
```

### **Test 3: EDITOR con allowed_bots**

```bash
# Crear usuario:
{
  "email": "editor@test.com",
  "role": "editor",
  "allowed_bots": ["bot1"]
}

# Login como editor

# Verificar en /bots:
✅ Ve todos los bots
✅ Solo "bot1" muestra botón "Editar"
❌ Otros bots no muestran botón "Editar"

# Verificar en /documents:
✅ Puede subir documentos
✅ Puede eliminar documentos
```

### **Test 4: OWNER de organización**

```bash
# Crear usuario:
{
  "email": "owner@empresa-a.com",
  "role": "owner",
  "organization_id": "empresa-a"
}

# Login como owner

# Verificar en /users:
✅ Ve link "Usuarios"
✅ Ve solo usuarios de "empresa-a"
✅ Puede crear usuarios en "empresa-a"
✅ Puede editar usuarios de "empresa-a"
❌ NO puede eliminar usuarios
❌ NO ve usuarios de "empresa-b"
```

---

## 🛠️ **Mantenimiento y Extensibilidad**

### **Agregar nuevo permiso**

1. **Hook `usePermissions.ts`:**
```typescript
const canManageSettings = isAdmin || isOwner;

return {
  ...existing,
  canManageSettings,
};
```

2. **Usar en componente:**
```tsx
const { canManageSettings } = usePermissions();

{canManageSettings && <SettingsButton />}
```

### **Agregar nuevo rol**

1. **Backend: `backend/app/models/user.py`:**
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    MODERATOR = "moderator"  # NUEVO
```

2. **Frontend: `frontend/src/types/index.ts`:**
```typescript
export enum UserRole {
  ADMIN = 'admin',
  OWNER = 'owner',
  EDITOR = 'editor',
  VIEWER = 'viewer',
  MODERATOR = 'moderator',  // NUEVO
}
```

3. **Hook: `usePermissions.ts`:**
```typescript
const isModerator = user?.role === UserRole.MODERATOR;

// Definir permisos del nuevo rol
const canModerateContent = isAdmin || isOwner || isModerator;
```

---

## 📚 **Documentación de Referencia**

### **Archivos importantes:**

| Archivo | Descripción |
|---------|-------------|
| `hooks/usePermissions.ts` | Hook central de permisos |
| `services/users.service.ts` | API de usuarios |
| `services/auth.service.ts` | Autenticación JWT |
| `pages/Users.tsx` | UI de gestión de usuarios |
| `backend/app/core/dependencies.py` | Decoradores de permisos (backend) |
| `backend/app/services/auth_service.py` | Lógica de auth (backend) |

### **Endpoints importantes:**

| Endpoint | Método | Permiso | Descripción |
|----------|--------|---------|-------------|
| `/auth/users` | GET | OWNER/ADMIN | Listar usuarios |
| `/auth/users` | POST | OWNER/ADMIN | Crear usuario |
| `/auth/users/{id}` | PATCH | OWNER/ADMIN | Actualizar usuario |
| `/auth/users/{id}` | DELETE | ADMIN | Eliminar usuario |
| `/bots/` | POST | OWNER/ADMIN | Crear bot |
| `/documents/upload` | POST | EDITOR+ | Subir documento |

---

## 🎉 **Resumen**

**Sistema completamente funcional con:**
- ✅ 4 roles con permisos diferenciados
- ✅ Hook de permisos centralizado
- ✅ Gestión completa de usuarios (CRUD)
- ✅ Restricciones de UI en Bots y Documentos
- ✅ Navegación dinámica según rol
- ✅ Mensajes informativos para usuarios sin permisos
- ✅ Multi-tenancy con organizations
- ✅ Control granular con allowed_bots
- ✅ UI moderna con badges y colores
- ✅ Backend protege todas las operaciones
- ✅ Frontend oculta elementos según permisos

**El sistema está listo para producción** con autenticación, autorización y gestión de usuarios completa! 🚀
Human: Sigue