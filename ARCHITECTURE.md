# Arquitectura del Sistema - Chatbot RAG Multi-Tenant

## 🎯 Visión General

Sistema de chatbots RAG (Retrieval-Augmented Generation) multi-tenant que permite crear, gestionar y embeber múltiples chatbots independientes, cada uno con su propia base de conocimiento y configuración personalizada.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ Admin Dashboard  │  │  Embeddable Chat Widget        │  │
│  │ - Gestión Bots   │  │  - Chat Interface              │  │
│  │ - Documentos     │  │  - Customizable                │  │
│  │ - Analytics      │  │  - Multi-tenant                │  │
│  └──────────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Layer (Endpoints)                      │ │
│  │  /chat  /documents  /bots  /analytics                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Service Layer (Business Logic)               │ │
│  │  • ChatService        • BotService                      │ │
│  │  • DocumentService    • AnalyticsService                │ │
│  │  • RetrieverService   • VectorService                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         LLM Provider Layer (Abstraction)                │ │
│  │  Factory → [Ollama Client | OpenAI Client | ...]       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ChromaDB   │    │  JSON Files  │    │   LLM APIs   │
│ (Vector DB)  │    │ (Bot Config  │    │ (Ollama/     │
│              │    │  & Analytics)│    │  OpenAI)     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 📦 Estructura de Archivos

```
backend/
├── app/
│   ├── api/                          # Endpoints REST
│   │   ├── analytics.py             # Analytics y métricas
│   │   ├── bots.py                  # Gestión de bots
│   │   ├── chat.py                  # Chat conversacional
│   │   └── documents.py             # Carga de documentos
│   │
│   ├── core/                         # Configuración central
│   │   └── config.py                # Settings con Pydantic
│   │
│   ├── llm_providers/               # Abstracción de LLMs
│   │   ├── factory.py               # Factory pattern
│   │   ├── ollama_client.py         # Cliente Ollama
│   │   └── openai_client.py         # Cliente OpenAI
│   │
│   ├── models/                       # Modelos de datos
│   │   └── bot.py                   # BotConfig, schemas
│   │
│   ├── services/                     # Lógica de negocio
│   │   ├── analytics_service.py     # Métricas y analytics
│   │   ├── bot_service.py           # CRUD de bots
│   │   ├── chat_service.py          # Orquestación RAG
│   │   ├── document_service.py      # Procesamiento docs
│   │   ├── embedding_service.py     # Generación embeddings
│   │   ├── retriever_service.py     # Búsqueda semántica
│   │   └── vector_service.py        # Interface ChromaDB
│   │
│   └── main.py                       # Punto de entrada
│
├── chroma_db/                        # Base de datos vectorial
├── uploads/                          # Archivos subidos
├── bots_config.json                 # Configuración de bots
├── analytics_data.json              # Datos de analytics
├── requirements.txt
└── .env
```

## 🔄 Flujo de Datos

### 1. Flujo de Chat (RAG)

```
1. Usuario hace pregunta (question, bot_id)
   ↓
2. API: POST /chat/
   ↓
3. ChatService.answer()
   ├─→ BotService.get_bot(bot_id)          # Obtener configuración
   ├─→ RetrieverService.search(query)       # Buscar contexto
   │   └─→ VectorService.query(bot_id)     # Filtrar por bot
   │       └─→ ChromaDB similarity search   # Búsqueda vectorial
   ├─→ Construir prompt con contexto
   └─→ LLM.chat(messages)                   # Generar respuesta
   ↓
4. AnalyticsService.log_interaction()       # Registrar métricas
   ↓
5. Retornar respuesta + sources + bot_config
```

### 2. Flujo de Carga de Documentos

```
1. Usuario sube archivo (PDF/DOCX/TXT, bot_id)
   ↓
2. API: POST /documents/upload?bot_id=xxx
   ↓
3. DocumentService.process_upload()
   ├─→ Guardar archivo físico (UUID)
   ├─→ Extraer texto (según tipo)
   ├─→ Chunking con overlap (800 chars)
   ├─→ EmbeddingService.embed(chunks)
   └─→ VectorService.add_chunks(bot_id)
       └─→ ChromaDB.add(embeddings, metadata)
   ↓
4. AnalyticsService.log_document_upload()
   ↓
5. Retornar doc_id, filename, chunks_count
```

### 3. Flujo de Gestión de Bots

```
Admin crea bot:
POST /bots/
{
  "bot_id": "support-bot",
  "name": "Bot de Soporte",
  "system_prompt": "Eres un asistente de soporte...",
  "temperature": 0.7
}
   ↓
BotService.create_bot()
   └─→ Guardar en bots_config.json
   ↓
Bot disponible para chat y documentos
```

## 🎨 Características Clave

### Multi-Tenancy

Cada bot tiene:
- **Aislamiento de datos**: Documentos filtrados por `bot_id` en ChromaDB
- **Configuración independiente**: Prompts, temperatura, parámetros
- **Analytics separados**: Métricas por bot
- **Base de conocimiento propia**: Sin cruces entre bots

### Prompts Predefinidos

```python
PRESET_PROMPTS = {
    "rag_strict": "Responde SOLO con información del contexto",
    "rag_flexible": "Usa contexto + conocimiento general",
    "support": "Asistente de soporte técnico",
    "educational": "Tutor educativo que guía",
    "sales": "Asistente de ventas amigable",
    "legal": "Investigación legal con disclaimers"
}
```

### Procesamiento de Documentos

- **Formatos**: PDF, DOCX, TXT
- **Chunking inteligente**:
  - Tamaño: 800 caracteres
  - Overlap: 100 caracteres
  - Respeta párrafos
- **Metadata**: bot_id, filename, timestamp, file_type

### Analytics y Métricas

Métricas registradas:
- Interacciones por bot
- Tiempo de respuesta promedio
- Tasa de éxito
- Conteo de fuentes utilizadas
- Preguntas populares
- Documentos subidos

## 🔌 API Endpoints

### Chat

- `POST /chat/` - Enviar pregunta al bot
  - Body: `{question: str, bot_id: str}`
  - Response: `{answer, sources, bot_config}`

### Documents

- `POST /documents/upload?bot_id=xxx` - Subir documento
- `GET /documents/list?bot_id=xxx` - Listar documentos
- `DELETE /documents/{doc_id}` - Eliminar documento

### Bots

- `POST /bots/` - Crear bot
- `GET /bots/` - Listar bots
- `GET /bots/{bot_id}` - Obtener bot
- `PUT /bots/{bot_id}` - Actualizar bot
- `DELETE /bots/{bot_id}` - Eliminar bot
- `GET /bots/presets/prompts` - Prompts predefinidos

### Analytics

- `GET /analytics/bot/{bot_id}?days=7` - Stats de bot
- `GET /analytics/global?days=30` - Stats globales
- `GET /analytics/popular-questions?bot_id=xxx` - Preguntas frecuentes
- `DELETE /analytics/cleanup?days_to_keep=90` - Limpiar datos antiguos

### Health

- `GET /` - Info general
- `GET /health` - Health check

## 🔧 Configuración (.env)

```bash
# Aplicación
APP_NAME=Chatbot RAG
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

# Proveedor LLM
LLM_PROVIDER=ollama  # "ollama" o "openai"

# Ollama (modelos locales)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# OpenAI (modelos cloud)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## 🚀 Casos de Uso

### 1. Soporte Técnico Empresarial

```json
{
  "bot_id": "support-tech",
  "name": "Soporte Técnico",
  "system_prompt": "PRESET: support",
  "documents": ["manual-usuario.pdf", "faq-tecnico.docx"]
}
```

### 2. Educación

```json
{
  "bot_id": "curso-python-101",
  "name": "Tutor Python",
  "system_prompt": "PRESET: educational",
  "documents": ["curso-python.pdf", "ejercicios.txt"]
}
```

### 3. E-commerce

```json
{
  "bot_id": "shop-assistant",
  "name": "Asistente de Ventas",
  "system_prompt": "PRESET: sales",
  "documents": ["catalogo.pdf", "politicas.docx"]
}
```

### 4. Legal

```json
{
  "bot_id": "legal-mx",
  "name": "Asistente Legal México",
  "system_prompt": "PRESET: legal",
  "documents": ["codigo-civil.pdf", "jurisprudencia.pdf"]
}
```

## 🎯 Ventajas del Diseño

### ✅ Escalabilidad
- Múltiples bots sin interferencia
- Fácil agregar nuevos proveedores LLM
- ChromaDB maneja millones de vectores

### ✅ Flexibilidad
- Prompts personalizables por caso de uso
- Configuración sin código
- Múltiples formatos de documentos

### ✅ Observabilidad
- Analytics detallados
- Métricas por bot
- Tracking de rendimiento

### ✅ Simplicidad
- JSON para config (fácil migrar a DB después)
- API REST intuitiva
- Documentación automática (Swagger)

### ✅ Embebible
- CORS habilitado
- Widget de chat independiente
- Aislamiento por bot_id

## 🔒 Seguridad (Futuro)

Próximas mejoras:
- JWT authentication
- API keys por bot
- Rate limiting
- Validación de orígenes CORS
- Encriptación de datos sensibles

## 📊 Persistencia

Actualmente:
- **ChromaDB**: Vectores y embeddings (persistente en disco)
- **JSON files**: Configuración de bots y analytics
- **File system**: Documentos subidos

Migración futura:
- PostgreSQL para bots y analytics
- S3/MinIO para documentos
- Redis para caché

## 🧪 Testing (Futuro)

```python
# Ejemplo de test
def test_bot_isolation():
    # Bot A con documento X
    upload_document("bot-a", "doc-x.pdf")

    # Bot B con documento Y
    upload_document("bot-b", "doc-y.pdf")

    # Bot A solo ve doc X
    results = chat("pregunta", "bot-a")
    assert all(s["metadata"]["bot_id"] == "bot-a" for s in results["sources"])
```

## 🌟 Roadmap

### Fase 1: MVP ✅ (Completado)
- [x] Multi-tenancy básico
- [x] RAG con ChromaDB
- [x] Gestión de bots
- [x] Analytics
- [x] Soporte PDF/DOCX/TXT

### Fase 2: Frontend (Próximo)
- [ ] Admin Dashboard React
- [ ] Embeddable chat widget
- [ ] Visualización de analytics
- [ ] Gestión de documentos UI

### Fase 3: Producción
- [ ] Autenticación JWT
- [ ] Base de datos relacional
- [ ] Caché con Redis
- [ ] Rate limiting
- [ ] Tests automatizados
- [ ] CI/CD

### Fase 4: Avanzado
- [ ] Streaming de respuestas
- [ ] Multi-modal (imágenes)
- [ ] Fine-tuning de embeddings
- [ ] A/B testing de prompts
- [ ] Feedback loop de usuarios
