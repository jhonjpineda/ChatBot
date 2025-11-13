# 🤖 Chatbot RAG Multi-Tenant

**Sistema profesional de chatbots** con RAG (Retrieval-Augmented Generation) que permite crear, gestionar y embeber múltiples chatbots independientes, cada uno con su propia base de conocimiento y configuración personalizada.

## 🌟 Características Principales

- **Multi-Tenancy**: Múltiples bots aislados, cada uno con su propia base de conocimiento
- **RAG Inteligente**: Recuperación semántica de información con ChromaDB
- **Multi-Formato**: Soporte para PDF, DOCX y TXT
- **Prompts Personalizables**: 6 presets predefinidos + configuración custom
- **Analytics**: Sistema completo de métricas y estadísticas
- **Embebible**: Widget de chat fácil de integrar en cualquier sitio web
- **Dual LLM**: Soporte para Ollama (local) y OpenAI (cloud)

---

## 🚀 Instalación Rápida

### Requisitos Previos

- Python 3.10 o superior
- Ollama instalado y corriendo (opcional, si usas modelos locales)
- 4GB RAM mínimo (8GB recomendado)

### 1. Clonar el repositorio

```bash
git clone https://github.com/jhonjpineda/ChatBot.git
cd ChatBot
```

### 2. Configurar el Backend

```bash
cd backend

# Crear entorno virtual
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

Copia el archivo `.env.example` a `.env` y configura:

```bash
# Aplicación
APP_NAME=Chatbot RAG
APP_ENV=development
APP_PORT=8000

# Proveedor LLM (elige uno)
LLM_PROVIDER=ollama  # o "openai"

# Ollama (modelos locales)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI (modelos cloud)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Ejecutar el Backend

```bash
# Asegúrate de estar en /backend con el venv activado
python -m uvicorn app.main:app --reload --port 8000
```

El backend estará disponible en: **http://localhost:8000**
Documentación API en: **http://localhost:8000/docs**

### 5. Configurar el Frontend

```bash
cd ../frontend

# Instalar dependencias
npm install

# Ejecutar desarrollo
npm run dev
```

El frontend estará disponible en: **http://localhost:5176**

---

## 📦 Estructura del Proyecto

```
ChatBot/
├── backend/
│   ├── app/
│   │   ├── api/                  # Endpoints REST
│   │   │   ├── analytics.py     # Analytics y métricas
│   │   │   ├── bots.py          # Gestión de bots
│   │   │   ├── chat.py          # Chat conversacional
│   │   │   └── documents.py     # Gestión de documentos
│   │   ├── core/
│   │   │   └── config.py        # Configuración centralizada
│   │   ├── llm_providers/       # Abstracción de LLMs
│   │   │   ├── factory.py
│   │   │   ├── ollama_client.py
│   │   │   └── openai_client.py
│   │   ├── models/              # Modelos de datos
│   │   │   └── bot.py
│   │   ├── services/            # Lógica de negocio
│   │   │   ├── analytics_service.py
│   │   │   ├── bot_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── retriever_service.py
│   │   │   └── vector_service.py
│   │   └── main.py              # Punto de entrada
│   ├── chroma_db/               # Base de datos vectorial
│   ├── uploads/                 # Documentos subidos
│   ├── bots_config.json         # Configuraciones de bots
│   ├── analytics_data.json      # Datos de analytics
│   ├── requirements.txt
│   └── .env
├── frontend/                    # Admin Dashboard React
│   ├── src/
│   │   ├── components/          # Componentes reutilizables
│   │   │   ├── Layout.tsx       # Layout principal
│   │   │   └── ChatWidget.tsx   # Widget embebible
│   │   ├── pages/               # Páginas
│   │   │   ├── Dashboard.tsx    # Dashboard home
│   │   │   ├── Bots.tsx         # Gestión de bots
│   │   │   ├── Documents.tsx    # Gestión de documentos
│   │   │   ├── Analytics.tsx    # Visualización analytics
│   │   │   └── ChatDemo.tsx     # Demo del widget
│   │   ├── services/            # API clients
│   │   │   ├── api.ts           # Axios config
│   │   │   ├── bots.service.ts
│   │   │   ├── documents.service.ts
│   │   │   ├── chat.service.ts
│   │   │   └── analytics.service.ts
│   │   ├── types/               # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx              # App principal
│   │   └── main.tsx             # Entry point
│   ├── package.json
│   └── tailwind.config.js
├── ARCHITECTURE.md              # Documentación de arquitectura
├── FRONTEND_PLAN.md             # Plan del frontend React
├── CHANGELOG.md                 # Changelog de mejoras
├── GUIA_USO.md                  # Guía paso a paso completa
└── README.md                    # Este archivo
```

---

## 🎯 Casos de Uso

### 1. Soporte Técnico

Crea un bot que responda preguntas sobre manuales de productos:

```bash
# Crear bot de soporte
POST /bots/
{
  "bot_id": "support-tech",
  "name": "Asistente de Soporte",
  "system_prompt": "Eres un asistente de soporte técnico profesional...",
  "temperature": 0.7
}

# Subir manuales
POST /documents/upload?bot_id=support-tech
Files: manual.pdf, faq.docx

# Chatear
POST /chat/
{
  "question": "¿Cómo reinicio el dispositivo?",
  "bot_id": "support-tech"
}
```

### 2. E-learning

Bot educativo para un curso específico:

```bash
# Crear bot educativo
POST /bots/
{
  "bot_id": "curso-python",
  "name": "Tutor Python",
  "system_prompt": "Eres un tutor educativo que guía...",
  "temperature": 0.8
}

# Subir materiales del curso
POST /documents/upload?bot_id=curso-python
Files: leccion1.pdf, ejercicios.txt
```

### 3. E-commerce

Asistente de ventas para tu tienda online:

```bash
# Crear bot de ventas
POST /bots/
{
  "bot_id": "shop-assistant",
  "name": "Asistente de Ventas",
  "system_prompt": "Eres un asistente de ventas amigable...",
  "temperature": 0.9
}

# Subir catálogo y políticas
POST /documents/upload?bot_id=shop-assistant
Files: catalogo.pdf, politicas-devolucion.docx
```

---

## 📡 API Endpoints

### Chat

- `POST /chat/` - Enviar pregunta al bot

### Gestión de Bots

- `POST /bots/` - Crear nuevo bot
- `GET /bots/` - Listar todos los bots
- `GET /bots/{bot_id}` - Obtener bot específico
- `PUT /bots/{bot_id}` - Actualizar bot
- `DELETE /bots/{bot_id}` - Eliminar bot
- `GET /bots/presets/prompts` - Obtener prompts predefinidos

### Documentos

- `POST /documents/upload?bot_id=xxx` - Subir documento
- `GET /documents/list?bot_id=xxx` - Listar documentos
- `DELETE /documents/{doc_id}` - Eliminar documento

### Analytics

- `GET /analytics/bot/{bot_id}?days=7` - Estadísticas de bot
- `GET /analytics/global?days=30` - Estadísticas globales
- `GET /analytics/popular-questions` - Preguntas frecuentes

### Health Check

- `GET /` - Información general
- `GET /health` - Estado del sistema

Ver documentación completa en: **http://localhost:8000/docs**

---

## 🎨 Prompts Predefinidos

El sistema incluye 6 prompts optimizados para diferentes casos de uso:

1. **rag_strict**: Responde SOLO con información del contexto
2. **rag_flexible**: Combina contexto + conocimiento general
3. **support**: Asistente de soporte técnico profesional
4. **educational**: Tutor educativo que guía el aprendizaje
5. **sales**: Asistente de ventas amigable
6. **legal**: Investigación legal con disclaimers apropiados

---

## 📊 Analytics y Métricas

El sistema registra automáticamente:

- Total de interacciones por bot
- Tiempo de respuesta promedio
- Tasa de éxito/error
- Número de fuentes utilizadas
- Preguntas más frecuentes
- Documentos subidos

Accede a las métricas vía API o (próximamente) en el Admin Dashboard.

---

## 🔧 Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **ChromaDB** - Base de datos vectorial
- **Sentence Transformers** - Generación de embeddings
- **PyPDF** - Procesamiento de PDFs
- **python-docx** - Procesamiento de DOCX
- **Pydantic** - Validación de datos
- **Ollama/OpenAI** - Modelos de lenguaje

### Frontend
- **React 18** + **TypeScript** - Framework UI moderno
- **Tailwind CSS v3** - Estilos utility-first
- **React Query (TanStack)** - Gestión de estado del servidor
- **React Router v6** - Navegación SPA
- **Vite** - Build tool ultrarrápido
- **Axios** - Cliente HTTP

---

## 🚀 Roadmap

### ✅ Fase 1: Backend MVP (Completado)
- [x] Multi-tenancy con aislamiento por bot
- [x] RAG con ChromaDB
- [x] Gestión completa de bots
- [x] Sistema de analytics
- [x] Soporte PDF/DOCX/TXT
- [x] Prompts configurables

### ✅ Fase 2: Frontend (Completado)
- [x] Admin Dashboard React
- [x] Gestión completa de Bots (CRUD)
- [x] Sistema de carga de documentos (drag & drop)
- [x] Visualización de analytics
- [x] Chat Widget embebible (solo React por ahora)
- [x] Generador de código de embed

### 📋 Fase 3: Producción
- [ ] Autenticación JWT
- [ ] Base de datos PostgreSQL
- [ ] Rate limiting
- [ ] Tests automatizados
- [ ] Docker + Docker Compose
- [ ] CI/CD pipeline

### 🌟 Fase 4: Avanzado
- [ ] Streaming de respuestas
- [ ] Soporte multi-idioma
- [ ] A/B testing de prompts
- [ ] Fine-tuning de embeddings
- [ ] Feedback loop de usuarios

---

## 📚 Documentación Adicional

- **[GUIA_USO.md](GUIA_USO.md)** - 📖 **Guía paso a paso completa** (EMPIEZA AQUÍ)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitectura detallada del sistema
- **[FRONTEND_PLAN.md](FRONTEND_PLAN.md)** - Plan completo del frontend React
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios y mejoras

## 🎥 Inicio Rápido

**Para empezar a usar el sistema ahora mismo:**

1. Lee la **[GUIA_USO.md](GUIA_USO.md)** - Contiene instrucciones paso a paso
2. Asegúrate de tener el backend y frontend corriendo
3. Crea tu primer bot desde el admin dashboard
4. Sube documentos PDF/DOCX/TXT
5. ¡Empieza a chatear!

---

## 🧪 Testing

```bash
# Crear bot de prueba
curl -X POST "http://localhost:8000/bots/" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "test-bot",
    "name": "Bot de Prueba",
    "description": "Bot para testing"
  }'

# Subir documento de prueba
curl -X POST "http://localhost:8000/documents/upload?bot_id=test-bot" \
  -F "file=@test.pdf"

# Hacer pregunta
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué información tienes?",
    "bot_id": "test-bot"
  }'
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👨‍💻 Autor

**Jhon Jairo Pineda Muñoz**
Ingeniero en Sistemas y Computación
GitHub: [@jhonjpineda](https://github.com/jhonjpineda)

---

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Excelente framework web
- [ChromaDB](https://www.trychroma.com/) - Base de datos vectorial
- [Ollama](https://ollama.ai/) - Modelos LLM locales
- [OpenAI](https://openai.com/) - GPT APIs

---

## 📞 Soporte

¿Tienes preguntas o necesitas ayuda?

- Abre un [Issue](https://github.com/jhonjpineda/ChatBot/issues)
- Contacta al autor

---

**⭐ Si te gusta este proyecto, dale una estrella en GitHub!**
