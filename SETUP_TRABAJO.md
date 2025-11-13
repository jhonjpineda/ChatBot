# 🚀 Setup para el Trabajo

## Pasos para configurar el proyecto después de hacer pull

### 1. Hacer Pull del Repositorio

```bash
cd /ruta/a/tu/proyecto
git pull origin main
```

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual (si no existe)
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Edita el archivo `backend/.env` y configura:

```bash
APP_NAME=Chatbot RAG
APP_ENV=development
LLM_PROVIDER=ollama  # o "openai"

# Ollama (modelos locales)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

# OpenAI (si lo usarás)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### 4. Instalar y Configurar Ollama (Opcional)

Si vas a usar modelos locales:

```bash
# Instalar Ollama desde https://ollama.ai/download

# Descargar modelo (elige uno)
ollama pull llama3.2:1b        # 1.3GB - Rápido pero básico
ollama pull qwen2.5:0.5b       # 397MB - MUY rápido
ollama pull llama3             # 4.7GB - Más capaz pero más lento

# Verificar instalación
ollama list
```

### 5. Configurar el Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install
```

### 6. Ejecutar el Proyecto

#### Terminal 1 - Backend:
```bash
cd backend
.venv\Scripts\activate  # Windows
python -m uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### 7. Acceder a la Aplicación

- **Frontend Dashboard**: http://localhost:5173 (o el puerto que muestre Vite)
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

---

## ✅ Verificación Rápida

### Probar Backend:
```bash
curl http://localhost:8000/health
```

Debería responder:
```json
{
  "status": "healthy",
  "llm_provider": "ollama",
  "version": "1.0.0"
}
```

### Probar Frontend:
1. Ve a http://localhost:5173
2. Deberías ver el Dashboard
3. Navega a "Bots" → debería mostrar el bot "default"
4. Navega a "Documentos" → puedes subir archivos PDF/DOCX/TXT
5. Navega a "Chat Widget" → prueba el chat con streaming

---

## 🆕 Nuevas Funcionalidades

### Streaming de Respuestas
- Las respuestas ahora aparecen palabra por palabra (como ChatGPT)
- Mejor experiencia de usuario
- Funciona con Ollama y OpenAI

### Gestión de Documentos
- **Subir documentos**: Drag & drop de PDF, DOCX, TXT
- **Mover entre bots**: Botón "Mover" en la tabla de documentos
- **Eliminar**: Botón "Eliminar" en cada documento

### Multi-Tenancy Completo
- Crea múltiples bots independientes
- Cada bot tiene su propia base de conocimiento
- 6 presets de prompts predefinidos

### Analytics
- Métricas por bot y globales
- Tiempo de respuesta promedio
- Preguntas más frecuentes
- Tasa de éxito/error

---

## 🐛 Troubleshooting

### Error: "Ollama model not found"
```bash
ollama pull llama3.2:1b
# Espera a que termine la descarga
# Reinicia el backend
```

### Error: "Module not found"
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Error: "Port already in use"
```bash
# Backend en otro puerto
python -m uvicorn app.main:app --reload --port 8001

# Frontend en otro puerto
npm run dev -- --port 5174
```

### ChromaDB no funciona
```bash
# Eliminar base de datos y recrear
rm -rf backend/chroma_db
# Volver a subir los documentos desde el frontend
```

---

## 📝 Notas Importantes

1. **No hacer commit de**:
   - `backend/chroma_db/` (base de datos vectorial)
   - `backend/analytics_data.json` (datos de analytics)
   - `backend/bots_config.json` (configuración de bots)
   - `backend/.venv/` (entorno virtual)
   - `frontend/node_modules/` (dependencias npm)

2. **Archivos de configuración local**:
   - `backend/.env` (ya está en .gitignore)
   - Los datos se crearán automáticamente al usar la app

3. **Rendimiento**:
   - Primera respuesta puede tardar 10-15 segundos (modelo local)
   - El streaming hace que se sienta más rápido
   - OpenAI es 5-10x más rápido si decides usarlo

---

## 🎯 Próximos Pasos Sugeridos

1. **Prueba el sistema completo**:
   - Crea un bot nuevo
   - Sube documentos
   - Prueba el chat widget

2. **Si OpenAI está aprobado**:
   - Consigue API key en https://platform.openai.com
   - Actualiza `.env`: `LLM_PROVIDER=openai`
   - Agrega tu `OPENAI_API_KEY`

3. **Para producción**:
   - Revisar ARCHITECTURE.md
   - Configurar PostgreSQL
   - Implementar autenticación JWT
   - Configurar Docker

---

**¿Problemas?** Revisa los logs en la terminal donde corre el backend/frontend.
