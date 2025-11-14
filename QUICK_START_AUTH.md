# 🚀 Inicio Rápido - Sistema de Autenticación

Guía rápida para empezar a usar el sistema de autenticación.

## 📦 Instalación

### 1. Instalar dependencias
```bash
cd backend
pip install -r requirements-auth.txt
```

### 2. Iniciar el backend
```bash
uvicorn app.main:app --reload
```

Al iniciar, se crea automáticamente el usuario admin:
```
✅ Usuario admin creado: admin@chatbot.com / admin123
```

## 🔐 Probar el Sistema

### 1. Login como Admin
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@chatbot.com","password":"admin123"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "user": {
    "user_id": "abc-123",
    "email": "admin@chatbot.com",
    "username": "Admin",
    "role": "admin",
    ...
  }
}
```

### 2. Guardar el token
```bash
TOKEN="eyJhbGciOiJIUzI1..."
```

### 3. Ver tu información
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Crear un nuevo usuario
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"usuario@ejemplo.com",
    "username":"Usuario Ejemplo",
    "password":"password123",
    "role":"editor"
  }'
```

### 5. Listar todos los usuarios (solo admin)
```bash
curl http://localhost:8000/auth/users \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 Próximos Pasos

### Para Backend:
1. Proteger endpoints existentes agregando `Depends(get_current_user)`
2. Configurar `JWT_SECRET_KEY` en variables de entorno
3. Cambiar contraseña del admin por defecto

### Para Frontend:
1. Crear páginas de Login y Register
2. Guardar token en localStorage
3. Agregar interceptor de axios para incluir token
4. Proteger rutas con React Router
5. Mostrar información del usuario en navbar
6. Agregar botón de logout

## 📚 Documentación Completa

Ver [AUTH_SYSTEM.md](./AUTH_SYSTEM.md) para documentación detallada.

## 🔒 Seguridad en Producción

1. **Cambiar JWT_SECRET_KEY**:
   ```bash
   # Generar clave segura
   openssl rand -hex 32

   # Agregar a .env
   JWT_SECRET_KEY=clave-generada-aqui
   ```

2. **Cambiar contraseña del admin**:
   - Login como admin
   - Crear nuevo usuario admin con contraseña segura
   - Eliminar el admin por defecto

3. **Configurar CORS**:
   ```python
   # En main.py
   allow_origins=["https://tudominio.com"]  # No usar "*"
   ```

4. **HTTPS en producción**:
   - Solo usar JWT sobre HTTPS
   - Nunca exponer tokens en URLs

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'jose'"
```bash
pip install python-jose[cryptography]
```

### Error: "ModuleNotFoundError: No module named 'passlib'"
```bash
pip install passlib[bcrypt]
```

### Error: "Usuario admin no encontrado"
- Elimina `users.json` y reinicia el backend
- Se recreará automáticamente

### Token inválido
- Verifica que el token no haya expirado (7 días)
- Asegúrate de incluir "Bearer " antes del token
- Verifica que no haya espacios extras

## 💡 Ejemplos de Uso

### JavaScript/TypeScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@chatbot.com',
    password: 'admin123'
  })
});

const { access_token, user } = await loginResponse.json();

// Guardar en localStorage
localStorage.setItem('token', access_token);
localStorage.setItem('user', JSON.stringify(user));

// Requests autenticados
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Python
```python
import requests

# Login
response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'admin@chatbot.com',
    'password': 'admin123'
})

data = response.json()
token = data['access_token']

# Requests autenticados
headers = {'Authorization': f'Bearer {token}'}

response = requests.get('http://localhost:8000/auth/me', headers=headers)
print(response.json())
```
