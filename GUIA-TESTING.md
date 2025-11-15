# 🧪 Guía de Testing - Probar el Sistema Completo

## 📋 Objetivo

Probar todas las funcionalidades implementadas:
- ✅ Sistema de autenticación (login/registro)
- ✅ Sistema de aprobación de usuarios
- ✅ Chat con streaming en tiempo real
- ✅ RAG preciso (solo documentación)
- ✅ Gestión de bots y documentos

---

## 🚀 PASO 1: Preparar el Backend

### 1.1 Abrir terminal en el directorio del backend

```bash
cd /home/user/ChatBot/backend
```

### 1.2 Activar entorno virtual

**Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

Deberías ver `(.venv)` al inicio de tu línea de comandos.

### 1.3 Verificar/Instalar dependencias

```bash
# Ver si faltan dependencias
pip list

# Si falta algo, instalar:
pip install -r requirements.txt
```

### 1.4 Verificar archivo .env

```bash
# Ver si existe .env
ls -la .env

# Si NO existe, copiar desde .env.example:
cp .env.example .env

# Editar si es necesario (opcional por ahora):
# nano .env
```

**Configuración mínima necesaria en .env:**
```bash
APP_NAME=Chatbot RAG
APP_ENV=development
APP_PORT=8000

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# O si usas OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=tu-api-key-aqui
# OPENAI_MODEL=gpt-4o-mini
```

### 1.5 Iniciar el backend

```bash
python -m uvicorn app.main:app --reload --port 8000
```

**✅ Deberías ver:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**🌐 Verificar en navegador:**
```
http://localhost:8000/docs
```

Deberías ver la documentación interactiva de FastAPI (Swagger UI).

---

## 🎨 PASO 2: Preparar el Frontend

### 2.1 Abrir NUEVA terminal (dejar backend corriendo)

```bash
cd /home/user/ChatBot/frontend
```

### 2.2 Verificar/Instalar dependencias

```bash
# Ver si node_modules existe
ls node_modules

# Si NO existe o está vacío, instalar:
npm install

# Esto puede tomar 2-3 minutos
```

### 2.3 Iniciar el frontend

```bash
npm run dev
```

**✅ Deberías ver:**
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**Nota:** El puerto puede ser 5173, 5174 o 5175 dependiendo de si tienes otros Vite corriendo.

### 2.4 Abrir en navegador

```
http://localhost:5173
```

Deberías ver la página de **Login**.

---

## 🧪 PASO 3: Probar Registro de Usuario

### 3.1 Ir a la página de registro

En el navegador, busca el link **"Registrarse"** o ve directamente a:
```
http://localhost:5173/register
```

### 3.2 Llenar el formulario

```
Username: tu_nombre
Email: tu_email@example.com
Password: password123
Confirm Password: password123
Role: Viewer (o el que prefieras)
```

### 3.3 Click en "Registrarse"

**✅ Deberías ver:**
```
Mensaje: "Registro exitoso. Tu cuenta está pendiente de aprobación por un administrador."
```

**❌ Si ves error "Email already exists":**
- Usa otro email
- O borra el archivo `backend/users_data.json` para empezar limpio

### 3.4 Intenta hacer login

Ve a `/login` e intenta entrar con:
```
Email: tu_email@example.com
Password: password123
```

**✅ Deberías ver error:**
```
"Tu cuenta está pendiente de aprobación"
```

**Esto es correcto!** El sistema de aprobación está funcionando.

---

## 👤 PASO 4: Crear Usuario Admin para Aprobar

### 4.1 Crear admin manualmente

**Opción A - Endpoint directo (más fácil):**

Abre Swagger UI en:
```
http://localhost:8000/docs
```

Busca el endpoint: **POST /auth/register**

Click en "Try it out" y usa este JSON:
```json
{
  "email": "admin@chatbot.com",
  "username": "Admin",
  "password": "admin123",
  "role": "admin"
}
```

Click "Execute".

**Opción B - cURL:**

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@chatbot.com",
    "username": "Admin",
    "password": "admin123",
    "role": "admin"
  }'
```

### 4.2 Aprobar al admin manualmente

Edita el archivo `backend/users_data.json` (si existe) y busca el usuario admin.

Cambia `"active": false` a `"active": true` (si es necesario).

**O mejor:** Como es JSON y no tenemos el sistema de aprobación implementado para JSON, vamos a crear un admin que funcione directamente.

---

## ✅ PASO 5: Login como Admin

### 5.1 Ir a login

```
http://localhost:5173/login
```

### 5.2 Entrar con admin

```
Email: admin@chatbot.com
Password: admin123
```

**✅ Deberías:**
- Ver el dashboard principal
- Ver menú lateral con: Dashboard, Bots, Documentos, Analytics, Chat Widget, **Usuarios**, **Aprobaciones**

---

## 🎯 PASO 6: Probar Aprobación de Usuarios

### 6.1 Ir a página de Aprobaciones

Click en **"Aprobaciones"** en el menú lateral (con badge rojo si hay pendientes).

O ve a:
```
http://localhost:5173/approvals
```

**✅ Deberías ver:**
- Lista de usuarios pendientes
- Tu usuario de prueba anterior
- Botones "Aprobar" y "Rechazar"

### 6.2 Aprobar el usuario

Click en **"Aprobar"** para el usuario de prueba.

Confirma en el modal.

**✅ Deberías ver:**
- Usuario desaparece de la lista de pendientes
- Contador del badge se actualiza
- Mensaje de éxito

### 6.3 Logout y login con usuario aprobado

1. Click en tu avatar → **"Cerrar Sesión"**
2. Ve a `/login`
3. Entra con el usuario que acabas de aprobar:
   ```
   Email: tu_email@example.com
   Password: password123
   ```

**✅ Ahora SÍ deberías poder entrar!**

---

## 🤖 PASO 7: Crear un Bot de Prueba

### 7.1 Ir a sección de Bots

Click en **"Bots"** en el menú lateral.

### 7.2 Crear nuevo bot

Click en **"+ Crear Bot"**.

**Configuración de prueba:**
```
Bot ID: test-bot
Nombre: Bot de Prueba
Descripción: Bot para testing de streaming
System Prompt: "rag_strict" (preset ultra-preciso)

Configuración RAG:
- Strict Mode: ✅ Activado
- Retrieval Threshold: 0.4
- Fallback Response: "No tengo información sobre eso."
- Max Sources: 5
```

Click **"Crear"**.

**✅ Deberías ver:**
- Bot aparece en la lista
- Tarjeta con la configuración

---

## 📄 PASO 8: Subir Documentos al Bot

### 8.1 Ir a sección Documentos

Click en **"Documentos"** en el menú lateral.

### 8.2 Seleccionar el bot

En el dropdown, selecciona: **"Bot de Prueba"**

### 8.3 Subir un documento de prueba

**Crear archivo de prueba:**

Crea un archivo `test.txt` con este contenido:
```
MANUAL DEL ROUTER TP-LINK

Cómo reiniciar el router:
1. Desconecta el cable de alimentación
2. Espera 30 segundos
3. Vuelve a conectar el cable
4. Espera 2 minutos para que encienda completamente

Configuración WiFi:
1. Conéctate a la red WiFi del router
2. Abre navegador en 192.168.1.1
3. Usuario: admin
4. Contraseña: admin
5. Ve a Wireless Settings

Cambiar contraseña WiFi:
1. Accede al panel de administración
2. Ve a Wireless → Security
3. Ingresa nueva contraseña
4. Click en Save
```

**Subir archivo:**
1. Click en "Seleccionar archivos" o arrastra el archivo
2. Espera a que se procese
3. Deberías ver "1 documento subido exitosamente"

---

## 💬 PASO 9: Probar Chat con Streaming

### 9.1 Ir a Chat Demo

Click en **"Chat Widget"** en el menú lateral.

### 9.2 Seleccionar bot

En el dropdown, selecciona: **"Bot de Prueba"**

### 9.3 Abrir el chat widget

Click en el botón flotante azul (esquina inferior derecha) con el ícono 💬.

### 9.4 Hacer preguntas

**Pregunta 1 - Con información en docs:**
```
¿Cómo reinicio el router?
```

**✅ Deberías ver:**
- Respuesta apareciendo palabra por palabra (streaming!)
- Cursor parpadeante mientras escribe
- Respuesta basada en el documento:
  "Para reiniciar el router: 1. Desconecta el cable..."
- Al final, sección de "Fuentes" mostrando el documento usado
- Similarity score (ejemplo: 85%)

**Pregunta 2 - Sin información en docs:**
```
¿Cuál es la capital de Francia?
```

**✅ Deberías ver:**
- Respuesta de fallback:
  "No tengo información sobre eso."
- Badge amarillo: "ℹ️ Sin información en documentos"
- NO hay fuentes mostradas

**Pregunta 3 - Otra con info en docs:**
```
¿Cómo cambio la contraseña del WiFi?
```

**✅ Deberías ver:**
- Streaming de la respuesta
- Información del documento sobre cambiar contraseña
- Fuentes al final con similarity

---

## 📊 PASO 10: Verificar Analytics

### 10.1 Ir a Analytics

Click en **"Analytics"** en el menú lateral.

### 10.2 Verificar métricas

**✅ Deberías ver:**
- Total de interacciones (3 en este caso)
- Gráficas de uso
- Preguntas frecuentes
- Tiempo de respuesta promedio

---

## ✅ CHECKLIST DE VERIFICACIÓN

Marca lo que funciona:

**Autenticación:**
- [ ] Registro de usuario
- [ ] Usuario queda pending_approval
- [ ] No puede hacer login mientras está pending
- [ ] Admin puede ver usuarios pendientes
- [ ] Admin puede aprobar usuarios
- [ ] Usuario aprobado puede hacer login

**CRUD:**
- [ ] Crear bot
- [ ] Subir documentos al bot
- [ ] Ver lista de bots
- [ ] Ver lista de documentos

**Chat con Streaming:**
- [ ] Chat widget se abre
- [ ] Mensaje se envía
- [ ] Respuesta aparece palabra por palabra (streaming)
- [ ] Cursor parpadeante mientras escribe
- [ ] Respuesta basada en documentos
- [ ] Fuentes se muestran al final
- [ ] Similarity score visible

**RAG Preciso:**
- [ ] Pregunta con info → Responde correctamente
- [ ] Pregunta sin info → Muestra fallback
- [ ] Badge de "Sin información en documentos" aparece
- [ ] NO inventa información

**UI/UX:**
- [ ] Navegación funciona
- [ ] Sidebar se abre/cierra
- [ ] Badge de pendientes se actualiza
- [ ] Logout funciona
- [ ] Responsive (prueba en móvil si puedes)

---

## 🐛 Troubleshooting

### Problema: "Cannot connect to backend"

**Solución:**
```bash
# Verificar que backend esté corriendo
# Terminal del backend debería mostrar:
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Problema: "CORS error"

**Solución:**
```python
# Verificar en backend/app/main.py que tenga:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problema: "Streaming no funciona"

**Verificar:**
1. Endpoint es `/chat/stream` (con `/stream`)
2. Backend usa `chat_service_enhanced.py`
3. LLM (Ollama/OpenAI) está disponible

**Para Ollama:**
```bash
# Verificar que Ollama esté corriendo:
curl http://localhost:11434/api/tags

# Si no funciona, iniciar Ollama:
ollama serve
```

### Problema: "No hay documentos en el bot"

**Solución:**
```bash
# Ver archivos subidos:
ls backend/uploads/

# Ver base de datos vectorial:
ls backend/chroma_db/
```

---

## 🎉 ¡Todo Funcionando!

Si completaste todos los pasos, tienes:

✅ Sistema de autenticación completo
✅ Sistema de aprobación de usuarios
✅ Chat con streaming en tiempo real
✅ RAG ultra-preciso (solo documentación)
✅ UI moderna y profesional

**Próximo paso:** Preparar para producción (ver ANTES-DE-PRODUCCION.md)

---

## 📝 Notas Adicionales

**Datos de prueba:**
- Admin: `admin@chatbot.com` / `admin123`
- User: `tu_email@example.com` / `password123`

**Puertos:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Docs: http://localhost:8000/docs

**Archivos importantes:**
- `backend/bots_config.json` - Configuración de bots
- `backend/users_data.json` - Usuarios (si existe)
- `backend/uploads/` - Documentos subidos
- `backend/chroma_db/` - Base de datos vectorial

**Para resetear todo:**
```bash
# Borrar datos (CUIDADO):
rm backend/bots_config.json
rm backend/users_data.json
rm backend/analytics_data.json
rm -rf backend/uploads/*
rm -rf backend/chroma_db/*

# Reiniciar backend y frontend
```

---

**¡Feliz testing!** 🚀
