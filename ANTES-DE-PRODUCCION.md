# ⚠️ ANTES DE IR A PRODUCCIÓN - CHECKLIST OBLIGATORIO

## 🚨 CRÍTICO - NO OMITIR

Este documento contiene **todos los pasos obligatorios** que DEBES hacer antes de desplegar el sistema en producción.

---

## 1️⃣ MIGRAR A POSTGRESQL (OBLIGATORIO)

**❌ Estado Actual:** JSON (archivos .json para bots, users, analytics)
**✅ Estado Requerido:** PostgreSQL con SQLAlchemy

### ¿Por qué es obligatorio?

- ❌ JSON no es thread-safe (race conditions)
- ❌ JSON no escala (lento con muchos datos)
- ❌ JSON no tiene transacciones ACID
- ❌ JSON no tiene relaciones con integridad referencial
- ✅ PostgreSQL es production-ready
- ✅ PostgreSQL maneja millones de registros
- ✅ PostgreSQL tiene backups automáticos

### Pasos para migrar:

1. **Instalar PostgreSQL**
   ```bash
   # Opción 1 - Docker (recomendado):
   docker-compose up -d

   # Opción 2 - Nativo:
   # Ver POSTGRESQL_SETUP.md para instrucciones por OS
   ```

2. **Crear base de datos y tablas**
   ```bash
   cd backend
   python init_tables.py
   ```

3. **Migrar datos de JSON a PostgreSQL**
   ```bash
   # Crear script de migración (lo debemos hacer)
   python migrate_json_to_postgres.py
   ```

4. **Actualizar main.py para usar PostgreSQL**
   ```python
   # Cambiar de:
   from app.api import auth  # Versión JSON

   # A:
   from app.api import auth_db  # Versión PostgreSQL

   # Y registrar rutas con auth_db
   app.include_router(auth_db.router, prefix="/auth", tags=["auth"])
   ```

5. **Actualizar servicios para usar SQLAlchemy**
   ```python
   # Usar:
   from app.services.auth_service_db import AuthServiceDB
   from app.database.connection import get_db

   # En vez de:
   from app.services.auth_service import AuthService
   ```

6. **Probar todo el sistema con PostgreSQL**
   - Registro de usuarios
   - Aprobación de usuarios
   - Login
   - CRUD de bots
   - Chat con RAG
   - Analytics

**⏱️ Tiempo estimado:** 2-4 horas
**📁 Archivos ya listos:** Todos los modelos y servicios PostgreSQL YA ESTÁN CREADOS

---

## 2️⃣ VARIABLES DE ENTORNO DE PRODUCCIÓN

**❌ NO usar .env.example en producción**
**✅ Crear .env de producción con secrets reales**

### Variables críticas a cambiar:

```bash
# JWT Secret (CAMBIAR OBLIGATORIAMENTE)
JWT_SECRET_KEY=tu-clave-super-secreta-generada-con-secrets-token-urlsafe-32

# Generar nueva clave:
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PostgreSQL (CAMBIAR passwords)
DATABASE_URL=postgresql://chatbot_user:PASSWORD_SUPER_SEGURO@localhost:5432/chatbot_db

# CORS (limitar a tu dominio)
CORS_ORIGINS=["https://tu-dominio.com"]

# NO usar "*" en producción
```

### Generar secrets seguros:

```bash
# JWT Secret
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# PostgreSQL password
python -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(24))"
```

**⏱️ Tiempo estimado:** 30 minutos

---

## 3️⃣ CONFIGURAR CORS CORRECTAMENTE

**❌ Estado Actual:** `allow_origins=["*"]` (permite cualquier dominio)
**✅ Estado Requerido:** Solo tu dominio

```python
# En backend/app/main.py

# CAMBIAR DE:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ INSEGURO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tu-dominio.com",
        "https://www.tu-dominio.com"
    ],  # ✅ SEGURO
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

**⏱️ Tiempo estimado:** 10 minutos

---

## 4️⃣ HTTPS OBLIGATORIO

**❌ NO usar HTTP en producción**
**✅ Configurar HTTPS con certificado SSL**

### Opciones:

1. **Let's Encrypt (Gratis)** - Recomendado
   ```bash
   # Con Certbot
   certbot --nginx -d tu-dominio.com
   ```

2. **Cloudflare** - Fácil y gratis
   - DNS en Cloudflare
   - SSL/TLS automático

3. **Railway/Render/Vercel** - HTTPS incluido
   - Deploy y ya tienen HTTPS

**⏱️ Tiempo estimado:** 1 hora (primera vez)

---

## 5️⃣ RATE LIMITING (Protección contra Abuse)

**❌ Estado Actual:** Sin rate limiting
**✅ Estado Requerido:** Limitar requests por usuario/IP

```python
# Instalar:
pip install slowapi

# En main.py:
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# En endpoints críticos:
@router.post("/chat/stream")
@limiter.limit("30/minute")  # Max 30 requests por minuto
async def chat_stream_endpoint(...):
    ...
```

**⏱️ Tiempo estimado:** 1 hora

---

## 6️⃣ LOGGING Y MONITOREO

**❌ Estado Actual:** print() statements
**✅ Estado Requerido:** Logging profesional

```python
# Configurar logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usar en vez de print:
logger.info("User logged in: %s", user_id)
logger.error("Chat failed: %s", error)
```

**Monitoreo recomendado:**
- Sentry (errores)
- Grafana + Prometheus (métricas)
- Uptime Robot (disponibilidad)

**⏱️ Tiempo estimado:** 2 horas

---

## 7️⃣ BACKUPS DE BASE DE DATOS

**❌ Sin backups = pérdida total de datos si algo falla**
**✅ Backups automáticos diarios**

```bash
# Script de backup (cron diario)
#!/bin/bash
pg_dump -U chatbot_user chatbot_db > backup_$(date +%Y%m%d).sql
# Subir a S3/Google Cloud Storage
```

**Configurar cron:**
```bash
# Backup diario a las 3 AM
0 3 * * * /path/to/backup.sh
```

**⏱️ Tiempo estimado:** 1 hora

---

## 8️⃣ DOCKERIZAR TODO (Recomendado)

**Ventajas:**
- ✅ Deploy consistente
- ✅ Fácil de escalar
- ✅ Aislamiento de dependencias

```yaml
# docker-compose.yml para producción
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - JWT_SECRET_KEY=${JWT_SECRET}
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=https://api.tu-dominio.com
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    restart: unless-stopped

volumes:
  postgres_data:
```

**⏱️ Tiempo estimado:** 3-4 horas

---

## 9️⃣ TESTS AUTOMATIZADOS (Muy Recomendado)

```bash
# Backend tests
pip install pytest pytest-asyncio

# Crear tests/
pytest backend/tests/

# Frontend tests
npm install --save-dev @testing-library/react vitest
npm run test
```

**⏱️ Tiempo estimado:** 8-12 horas (vale la pena)

---

## 🔟 VARIABLES DE FRONTEND

**❌ Estado Actual:** `http://localhost:8000` hardcodeado
**✅ Estado Requerido:** Variables de entorno

```typescript
// frontend/.env.production
VITE_API_URL=https://api.tu-dominio.com

// Usar en código:
const API_URL = import.meta.env.VITE_API_URL;

// En services/api.ts:
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});
```

**⏱️ Tiempo estimado:** 30 minutos

---

## 📋 CHECKLIST FINAL ANTES DE DEPLOY

Marca cada item cuando esté completado:

### Crítico (NO OMITIR):
- [ ] Migrado a PostgreSQL
- [ ] JWT_SECRET_KEY cambiado
- [ ] Passwords de PostgreSQL cambiados
- [ ] CORS configurado con dominio específico
- [ ] HTTPS configurado
- [ ] Rate limiting implementado

### Importante:
- [ ] Logging configurado
- [ ] Backups automáticos configurados
- [ ] Variables de entorno de producción
- [ ] Frontend usa variables de entorno
- [ ] Sistema de monitoreo (Sentry, etc.)

### Recomendado:
- [ ] Dockerizado
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Documentación de deployment
- [ ] Runbook de incidentes

---

## ⏱️ TIEMPO TOTAL ESTIMADO

**Mínimo obligatorio:** 6-8 horas
**Completo recomendado:** 15-20 horas

---

## 🚀 PLATAFORMAS DE DEPLOY RECOMENDADAS

### Opción 1: Railway (Más fácil)
- ✅ PostgreSQL incluido
- ✅ HTTPS automático
- ✅ Deploy con git push
- 💰 $5-20/mes

### Opción 2: Render (Gratis para empezar)
- ✅ PostgreSQL gratis (limitado)
- ✅ HTTPS automático
- 💰 Gratis tier, luego $7/mes

### Opción 3: DigitalOcean (Más control)
- ✅ Droplets desde $6/mes
- ✅ PostgreSQL managed
- ⚙️ Más configuración manual

### Opción 4: AWS/Google Cloud (Empresarial)
- ✅ Máxima escalabilidad
- 💰 Más caro
- ⚙️ Complejidad alta

---

## 📞 SOPORTE

Si tienes dudas antes de ir a producción:
1. Revisa la documentación en /docs
2. Consulta las guías:
   - DATABASE_DESIGN.md
   - POSTGRESQL_SETUP.md
   - STREAMING_GUIDE.md
   - RAG_PRECISION_GUIDE.md

---

**⚠️ IMPORTANTE:** NO saltarse la migración a PostgreSQL. JSON NO es apto para producción.

**✅ Cuando completes este checklist, tu sistema estará listo para recibir usuarios reales de forma segura y escalable.**
