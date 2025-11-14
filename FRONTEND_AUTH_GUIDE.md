# 🔐 Guía de Autenticación Frontend

Sistema completo de autenticación JWT integrado en el frontend React.

## ✅ Implementación Completada

### Archivos Creados

```
frontend/src/
├── contexts/
│   └── AuthContext.tsx          ✨ Contexto de autenticación React
├── services/
│   └── auth.service.ts          ✨ Servicio de autenticación
├── pages/
│   ├── Login.tsx                ✨ Página de login
│   └── Register.tsx             ✨ Página de registro
└── components/
    └── PrivateRoute.tsx         ✨ Componente de protección de rutas
```

### Archivos Modificados

```
frontend/src/
├── types/index.ts               ➕ Tipos de autenticación agregados
├── services/api.ts              ➕ Interceptor JWT agregado
├── components/Layout.tsx        ➕ Menú de usuario y logout
└── App.tsx                      ➕ Rutas de auth y protección
```

---

## 🚀 Características Implementadas

### 1. **Autenticación Completa**
- ✅ Login con email y password
- ✅ Registro de nuevos usuarios
- ✅ Persistencia de sesión en localStorage
- ✅ Cierre de sesión (logout)
- ✅ Auto-login al recargar página

### 2. **Protección de Rutas**
- ✅ Todas las rutas principales protegidas con `PrivateRoute`
- ✅ Redirección automática a `/login` si no está autenticado
- ✅ Redirección a `/` después de login exitoso
- ✅ Manejo de errores 401 (no autenticado)

### 3. **UI Moderna**
- ✅ Páginas de login/register con diseño profesional
- ✅ Menú de usuario en header con dropdown
- ✅ Avatar con inicial del nombre
- ✅ Badge de rol (Admin, Owner, Editor, Viewer)
- ✅ Mensajes de error en formularios
- ✅ Estados de loading

### 4. **Gestión de Estado**
- ✅ Context API de React para estado global
- ✅ Hook personalizado `useAuth()`
- ✅ Sincronización con localStorage
- ✅ Manejo de token JWT automático

---

## 📱 Uso del Sistema

### Login

**URL:** `http://localhost:5176/login`

**Credenciales por defecto:**
```
Email: admin@chatbot.com
Password: admin123
```

**Características:**
- Validación de campos requeridos
- Mensajes de error claros
- Link a página de registro
- Credenciales de prueba visibles

### Registro

**URL:** `http://localhost:5176/register`

**Campos:**
- Nombre completo
- Email
- Contraseña (mínimo 6 caracteres)
- Confirmar contraseña
- Rol (Viewer, Editor, Owner)

**Validaciones:**
- Contraseñas deben coincidir
- Mínimo 6 caracteres
- Email válido requerido

### Logout

**Acceso:** Click en avatar de usuario → "Cerrar Sesión"

**Acciones:**
- Limpia token de localStorage
- Limpia datos de usuario
- Redirige a `/login`

---

## 🔧 Uso Programático

### Hook useAuth()

```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout, register } = useAuth();

  // Acceder a información del usuario
  console.log(user?.email);
  console.log(user?.role);

  // Verificar autenticación
  if (!isAuthenticated) {
    // Usuario no autenticado
  }

  // Login
  await login({ email: 'user@example.com', password: 'password' });

  // Registro
  await register({
    email: 'new@example.com',
    username: 'Nuevo Usuario',
    password: 'password123',
    role: UserRole.VIEWER
  });

  // Logout
  logout();

  return <div>Hola {user?.username}</div>;
}
```

### Servicio de Autenticación

```typescript
import { authService } from '../services/auth.service';

// Verificar si está autenticado
if (authService.isAuthenticated()) {
  // Usuario autenticado
}

// Obtener token
const token = authService.getToken();

// Obtener usuario guardado
const user = authService.getStoredUser();

// Logout
authService.logout();
```

### Proteger Componentes

```typescript
import PrivateRoute from '../components/PrivateRoute';

<PrivateRoute>
  <MiComponenteProtegido />
</PrivateRoute>
```

---

## 🎨 Roles y Permisos

### Viewer (Visualizador)
- Solo lectura
- Puede ver bots y usar chat
- Puede ver analytics
- **Badge:** Gris

### Editor
- Puede editar bots
- Puede subir/eliminar documentos
- Puede modificar configuraciones
- **Badge:** Verde

### Owner (Propietario)
- Admin de su organización
- Puede gestionar usuarios
- Acceso completo a su organización
- **Badge:** Azul

### Admin (Administrador)
- Acceso total al sistema
- Puede gestionar todas las organizaciones
- Super usuario
- **Badge:** Morado

---

## 🔒 Seguridad

### Token JWT
- Almacenado en `localStorage` como `chatbot_token`
- Enviado automáticamente en header `Authorization: Bearer <token>`
- Expiración: 7 días (configurable en backend)

### Interceptores Axios

**Request Interceptor:**
```typescript
// Agrega token automáticamente a todas las peticiones
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('chatbot_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Response Interceptor:**
```typescript
// Maneja errores 401 (no autenticado)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Limpiar sesión y redirigir a login
      localStorage.removeItem('chatbot_token');
      localStorage.removeItem('chatbot_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## 📊 Flujo de Autenticación

```
1. Usuario visita aplicación
   ↓
2. AuthContext verifica si hay token en localStorage
   ↓ Si hay token
3. Intenta cargar usuario desde API (/auth/me)
   ↓ Si es válido
4. Usuario autenticado → acceso a rutas protegidas
   ↓ Si no es válido
5. Limpia token → redirige a /login

Login:
1. Usuario ingresa email y password
   ↓
2. POST /auth/login
   ↓
3. Backend valida y retorna token + user
   ↓
4. Frontend guarda en localStorage
   ↓
5. Actualiza contexto con usuario
   ↓
6. Redirige a dashboard (/)

Logout:
1. Usuario click en "Cerrar Sesión"
   ↓
2. Limpia localStorage
   ↓
3. Limpia contexto de usuario
   ↓
4. Redirige a /login
```

---

## 🧪 Testing

### Probar Login
1. Ir a `http://localhost:5176/login`
2. Usar credenciales: `admin@chatbot.com / admin123`
3. Verificar redirección a dashboard
4. Verificar que aparece avatar y nombre en header

### Probar Registro
1. Ir a `http://localhost:5176/register`
2. Completar formulario con datos nuevos
3. Verificar registro exitoso y redirección
4. Verificar que se puede hacer login con las nuevas credenciales

### Probar Protección de Rutas
1. Abrir navegador en modo incógnito
2. Ir directamente a `http://localhost:5176/bots`
3. Verificar redirección automática a `/login`
4. Hacer login
5. Verificar acceso a `/bots`

### Probar Logout
1. Con sesión iniciada, click en avatar
2. Click en "Cerrar Sesión"
3. Verificar redirección a `/login`
4. Intentar acceder a `http://localhost:5176/bots`
5. Verificar redirección a `/login`

### Probar Persistencia
1. Hacer login
2. Recargar la página (F5)
3. Verificar que sigue autenticado
4. Cerrar pestaña y abrir nueva
5. Ir a `http://localhost:5176`
6. Verificar que sigue autenticado

---

## 🚀 Ejecutar el Proyecto

### Backend
```bash
cd backend
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Acceder
- Frontend: http://localhost:5176
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🎯 Próximos Pasos

### Mejoras Futuras
- [ ] Refresh tokens (renovar sin re-login)
- [ ] Recordar sesión (checkbox "Mantener sesión iniciada")
- [ ] Recuperación de contraseña
- [ ] Verificación de email
- [ ] OAuth2 (Google, GitHub)
- [ ] 2FA (Two-Factor Authentication)
- [ ] Gestión de usuarios en UI (CRUD)
- [ ] Cambio de contraseña desde perfil
- [ ] Límite de intentos de login
- [ ] Logs de actividad del usuario

### Optimizaciones
- [ ] Mover token a httpOnly cookies (más seguro)
- [ ] Implementar refresh token rotation
- [ ] Rate limiting en frontend
- [ ] Validaciones más robustas
- [ ] Tests unitarios y E2E

---

## 📝 Notas Importantes

### localStorage vs Cookies
**Actualmente usando localStorage:**
- ✅ Fácil de implementar
- ✅ Funciona sin configuración
- ❌ Vulnerable a XSS

**Para producción considerar cookies:**
- ✅ httpOnly cookies (más seguro)
- ✅ No accesible desde JavaScript
- ❌ Requiere configuración CORS

### Token Expiration
- Tokens expiran en 7 días
- Al expirar, usuario debe hacer login nuevamente
- Frontend detecta 401 y limpia sesión automáticamente

### Multi-tenancy
- Usuarios con `organization_id` solo ven datos de su organización
- Admin (sin `organization_id`) ve todo
- Backend filtra automáticamente por organización

---

## 🎉 Resumen

**Sistema completamente funcional con:**
- ✅ Login y registro
- ✅ Protección de rutas
- ✅ Manejo de sesión
- ✅ UI moderna y profesional
- ✅ Integración total con backend JWT
- ✅ Interceptores automáticos
- ✅ Manejo de errores
- ✅ Experiencia de usuario fluida

**Listo para usar en desarrollo!** 🚀
