# 🔧 Solución de Problemas

## Error: "does not provide an export named..."

Si ves errores como:
```
Uncaught SyntaxError: The requested module '/src/types/index.ts' does not provide an export named 'AuthResponse'
```

### Solución:

1. **Limpiar caché de Vite:**
```bash
cd frontend
rm -rf node_modules/.vite dist .vite
```

2. **Reinstalar dependencias (opcional):**
```bash
npm install
```

3. **Reiniciar el servidor de desarrollo:**
```bash
npm run dev
```

4. **Limpiar caché del navegador:**
- Chrome/Edge: Ctrl + Shift + R (Windows/Linux) o Cmd + Shift + R (Mac)
- Firefox: Ctrl + F5 (Windows/Linux) o Cmd + Shift + R (Mac)

---

## Error: Backend no responde

Si el frontend no puede conectarse al backend:

1. **Verificar que el backend esté corriendo:**
```bash
cd backend
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
python -m uvicorn app.main:app --reload
```

2. **Verificar la URL del backend en el frontend:**
El archivo `frontend/.env` (si existe) o `frontend/src/services/api.ts` debe tener:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

3. **Verificar CORS:**
El backend debe permitir el origen del frontend. Verifica en `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5176"],  # Puerto del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Error: 401 Unauthorized después de login

Si después de hacer login obtienes errores 401:

1. **Verificar que el token se guardó correctamente:**
Abre las DevTools del navegador (F12) → Application/Storage → Local Storage → `http://localhost:5176`

Debes ver:
- `chatbot_token`: JWT token
- `chatbot_user`: JSON con datos del usuario

2. **Verificar que el backend acepta el token:**
Ve a http://localhost:8000/docs y prueba el endpoint `/auth/me` con el token.

3. **Limpiar sesión y volver a hacer login:**
```javascript
// En la consola del navegador:
localStorage.clear();
location.reload();
```

---

## Error: npm install falla

Si `npm install` falla:

1. **Limpiar caché de npm:**
```bash
npm cache clean --force
```

2. **Eliminar node_modules:**
```bash
rm -rf node_modules package-lock.json
npm install
```

3. **Usar una versión compatible de Node.js:**
Este proyecto requiere Node.js 16 o superior.
```bash
node --version  # Debe ser >= 16.x
```

---

## Puerto 5176 ya en uso

Si el puerto del frontend está ocupado:

1. **Cambiar el puerto en vite.config.ts:**
```typescript
export default defineConfig({
  server: {
    port: 5177,  // Cambiar a otro puerto
  },
  // ...
})
```

2. **O terminar el proceso que usa el puerto:**
```bash
# Linux/Mac:
lsof -i :5176
kill -9 <PID>

# Windows:
netstat -ano | findstr :5176
taskkill /PID <PID> /F
```

---

## Problemas con Tailwind CSS (estilos no se aplican)

Si los estilos de Tailwind no funcionan:

1. **Verificar que tailwind.config.js existe** y tiene:
```javascript
content: [
  "./index.html",
  "./src/**/*.{js,ts,jsx,tsx}",
],
```

2. **Verificar que main.css importa Tailwind:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

3. **Reiniciar el servidor de desarrollo:**
```bash
npm run dev
```

---

## Logs útiles para debugging

### Ver logs del backend:
El backend imprime logs en la terminal donde ejecutas `uvicorn`.

### Ver logs del frontend:
1. Abre DevTools (F12)
2. Ve a la pestaña "Console"
3. Verás errores de JavaScript/TypeScript

### Ver requests HTTP:
1. Abre DevTools (F12)
2. Ve a la pestaña "Network"
3. Filtra por "XHR" o "Fetch"
4. Verás todas las peticiones al backend

---

## Resetear el proyecto completamente

Si nada funciona, resetea todo:

```bash
# Backend
cd backend
rm -rf .venv chroma_db uploads bots_config.json analytics_data.json users.json
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
rm -rf node_modules .vite dist package-lock.json
npm install

# Iniciar backend
cd ../backend
python -m uvicorn app.main:app --reload

# En otra terminal, iniciar frontend
cd frontend
npm run dev
```

---

## Contacto

Si el problema persiste, abre un issue en GitHub con:
- Descripción del error
- Logs del backend y frontend
- Versión de Node.js y Python
- Sistema operativo
