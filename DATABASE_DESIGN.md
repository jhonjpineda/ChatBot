# 🗄️ Diseño de Base de Datos PostgreSQL

## 📊 Esquema de Tablas

### **1. Tabla: `users`**

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'owner', 'editor', 'viewer')),
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    active BOOLEAN DEFAULT TRUE,
    pending_approval BOOLEAN DEFAULT TRUE,  -- ✨ NUEVO: Aprobación de admin
    approved_by UUID REFERENCES users(user_id) ON DELETE SET NULL,  -- Quien aprobó
    approved_at TIMESTAMP,
    allowed_bots TEXT[],  -- Array de bot_ids permitidos
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_pending ON users(pending_approval);  -- Para búsquedas rápidas
```

**Campos clave:**
- `pending_approval`: TRUE si espera aprobación, FALSE si está aprobado
- `approved_by`: Referencia al admin que aprobó
- `approved_at`: Timestamp de aprobación

---

### **2. Tabla: `organizations`**

```sql
CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    max_bots INTEGER DEFAULT 10,  -- Límite de bots
    max_users INTEGER DEFAULT 50,  -- Límite de usuarios
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_organizations_slug ON organizations(slug);
```

---

### **3. Tabla: `bots`**

```sql
CREATE TABLE bots (
    bot_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    model_provider VARCHAR(50) DEFAULT 'ollama',  -- 'ollama' o 'openai'
    model_name VARCHAR(100) DEFAULT 'llama3',

    -- Configuración RAG
    retrieval_threshold FLOAT DEFAULT 0.3,  -- ✨ Threshold de similitud
    max_sources INTEGER DEFAULT 5,
    strict_mode BOOLEAN DEFAULT TRUE,  -- ✨ Solo responder con docs
    fallback_response TEXT DEFAULT 'Lo siento, no tengo información sobre eso en mi base de conocimiento.',

    organization_id UUID REFERENCES organizations(organization_id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_bots_organization ON bots(organization_id);
CREATE INDEX idx_bots_active ON bots(active);
```

**Nuevos campos para RAG preciso:**
- `retrieval_threshold`: Mínimo de similitud para considerar un documento
- `strict_mode`: Si TRUE, solo responde con docs; si FALSE, puede usar conocimiento general
- `fallback_response`: Respuesta cuando no hay info en docs

---

### **4. Tabla: `documents`**

```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id VARCHAR(100) REFERENCES bots(bot_id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),  -- 'pdf', 'docx', 'txt'
    file_size INTEGER,  -- En bytes
    file_path TEXT NOT NULL,

    -- Metadata de procesamiento
    chunks_count INTEGER DEFAULT 0,  -- Cuántos chunks se generaron
    processing_status VARCHAR(50) DEFAULT 'completed',  -- 'processing', 'completed', 'failed'
    error_message TEXT,

    uploaded_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_bot ON documents(bot_id);
CREATE INDEX idx_documents_status ON documents(processing_status);
```

---

### **5. Tabla: `conversations`**

```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id VARCHAR(100) REFERENCES bots(bot_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    session_id VARCHAR(255),  -- Para agrupar conversaciones

    -- Pregunta del usuario
    user_message TEXT NOT NULL,

    -- Respuesta del bot
    bot_response TEXT NOT NULL,

    -- Metadata RAG
    sources_used INTEGER DEFAULT 0,  -- Cuántas fuentes se usaron
    similarity_scores FLOAT[],  -- Scores de similitud de cada fuente
    document_ids UUID[],  -- IDs de documentos usados

    -- Performance
    response_time_ms INTEGER,  -- Tiempo de respuesta en ms
    tokens_used INTEGER,

    -- Feedback (opcional)
    user_feedback VARCHAR(20),  -- 'positive', 'negative', null
    feedback_comment TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_bot ON conversations(bot_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
```

**Campos para análisis:**
- `sources_used`: Cuántas fuentes RAG se usaron
- `similarity_scores`: Array de scores para analizar calidad
- `response_time_ms`: Para medir performance
- `user_feedback`: Para mejorar el sistema

---

### **6. Tabla: `analytics_daily`** (Agregaciones diarias)

```sql
CREATE TABLE analytics_daily (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id VARCHAR(100) REFERENCES bots(bot_id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- Métricas diarias
    total_interactions INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT,
    total_tokens_used INTEGER DEFAULT 0,

    -- Feedback
    positive_feedback INTEGER DEFAULT 0,
    negative_feedback INTEGER DEFAULT 0,

    -- Fuentes RAG
    avg_sources_used FLOAT,
    avg_similarity_score FLOAT,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(bot_id, date)
);

CREATE INDEX idx_analytics_bot_date ON analytics_daily(bot_id, date DESC);
```

---

### **7. Tabla: `user_sessions`** (Control de sesiones JWT)

```sql
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,  -- JWT ID
    refresh_token VARCHAR(500),
    ip_address VARCHAR(50),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_jti);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

---

## 🔗 Relaciones entre Tablas

```
organizations (1) ──── (N) users
organizations (1) ──── (N) bots
users (1) ──── (N) bots (created_by)
users (1) ──── (N) conversations
users (1) ──── (N) user_sessions
users (1) ──── (N) users (approved_by) [self-reference]
bots (1) ──── (N) documents
bots (1) ──── (N) conversations
bots (1) ──── (N) analytics_daily
documents (N) ──── (N) conversations (through document_ids array)
```

---

## 📈 Ventajas de este Diseño

### **1. Sistema de Aprobación Completo**
```sql
-- Usuarios pendientes de aprobación
SELECT * FROM users
WHERE pending_approval = TRUE
ORDER BY created_at DESC;

-- Aprobar usuario
UPDATE users
SET pending_approval = FALSE,
    approved_by = 'admin-uuid',
    approved_at = NOW()
WHERE user_id = 'user-uuid';
```

### **2. RAG Preciso y Configurable**
```sql
-- Bots en modo estricto (solo docs)
SELECT * FROM bots
WHERE strict_mode = TRUE;

-- Conversaciones con baja similitud (para revisar)
SELECT * FROM conversations
WHERE bot_id = 'my-bot'
  AND (SELECT AVG(s) FROM unnest(similarity_scores) s) < 0.5;
```

### **3. Analytics Avanzados**
```sql
-- Reporte semanal de un bot
SELECT
    date,
    total_interactions,
    avg_response_time_ms,
    avg_similarity_score,
    ROUND(100.0 * positive_feedback / NULLIF(positive_feedback + negative_feedback, 0), 2) as satisfaction_rate
FROM analytics_daily
WHERE bot_id = 'my-bot'
  AND date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC;
```

### **4. Auditoría Completa**
```sql
-- Quién aprobó a cada usuario
SELECT
    u.username,
    u.email,
    u.created_at as registered_at,
    u.approved_at,
    approver.username as approved_by
FROM users u
LEFT JOIN users approver ON u.approved_by = approver.user_id
WHERE u.pending_approval = FALSE;
```

### **5. Performance Optimizado**
- Índices en todas las búsquedas frecuentes
- `analytics_daily` pre-calculado (evita queries pesadas)
- Arrays de PostgreSQL para relaciones N-N simples
- UUIDs para mejor distribución y seguridad

---

## 🚀 Queries Útiles

### **Dashboard de Admin - Usuarios Pendientes**
```sql
SELECT
    user_id,
    username,
    email,
    role,
    created_at,
    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_waiting
FROM users
WHERE pending_approval = TRUE
ORDER BY created_at ASC;
```

### **Calidad de Respuestas RAG**
```sql
-- Conversaciones con fuentes insuficientes
SELECT
    c.conversation_id,
    c.user_message,
    c.sources_used,
    b.name as bot_name
FROM conversations c
JOIN bots b ON c.bot_id = b.bot_id
WHERE c.sources_used < 2
  AND c.created_at > NOW() - INTERVAL '24 hours';
```

### **Top Bots por Uso**
```sql
SELECT
    b.name,
    COUNT(c.conversation_id) as total_conversations,
    AVG(c.response_time_ms) as avg_response_time,
    COUNT(DISTINCT c.user_id) as unique_users
FROM bots b
LEFT JOIN conversations c ON b.bot_id = c.bot_id
WHERE c.created_at > NOW() - INTERVAL '30 days'
GROUP BY b.bot_id, b.name
ORDER BY total_conversations DESC
LIMIT 10;
```

### **Documentos más Útiles**
```sql
-- Documentos que más aparecen en respuestas
SELECT
    d.filename,
    d.bot_id,
    COUNT(*) as times_used
FROM documents d
JOIN conversations c ON d.document_id = ANY(c.document_ids)
WHERE c.created_at > NOW() - INTERVAL '7 days'
GROUP BY d.document_id, d.filename, d.bot_id
ORDER BY times_used DESC
LIMIT 20;
```

---

## 🔧 Configuración de PostgreSQL

### **1. Extensiones necesarias**
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- Para búsquedas de texto similares
```

### **2. Variables de entorno**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

---

## 📝 Migración de Datos

### **Plan de migración desde JSON:**

1. **Crear tablas** (ejecutar SQL DDL)
2. **Migrar usuarios** (`users_data.json` → `users`)
3. **Migrar bots** (`bots_config.json` → `bots`)
4. **Migrar analytics** (`analytics_data.json` → `analytics_daily`)
5. **Mantener ChromaDB** (embeddings siguen en Chroma)
6. **Actualizar servicios** (cambiar de JSON a PostgreSQL)

---

## ✅ Ventajas Finales

| Aspecto | JSON (Actual) | PostgreSQL (Nuevo) |
|---------|---------------|-------------------|
| Concurrencia | ❌ Race conditions | ✅ ACID transactions |
| Búsquedas | ❌ Lento (scan completo) | ✅ Índices optimizados |
| Relaciones | ❌ Manual | ✅ Foreign keys |
| Reportes | ❌ Limitado | ✅ SQL avanzado |
| Escalabilidad | ❌ Limitada | ✅ Millones de registros |
| Backups | ❌ Manual | ✅ Automático |
| Aprobaciones | ❌ No implementado | ✅ Built-in |
| Analytics | ❌ Cálculo en runtime | ✅ Pre-agregado |

---

**Próximo paso:** Implementar modelos SQLAlchemy y configurar la conexión a PostgreSQL.
