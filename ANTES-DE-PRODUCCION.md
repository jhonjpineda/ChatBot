# ⚠️ CHECKLIST ANTES DE SUBIR A PRODUCCIÓN

## 🔴 CRÍTICO - MIGRAR DE JSON A POSTGRESQL

### Estado Actual
- ✅ Sistema funcionando con archivos JSON
- ✅ Código preparado para PostgreSQL
- ⚠️ **JSON NO es apropiado para producción** (no escala, no soporta concurrencia)

### Por qué PostgreSQL es NECESARIO en Producción
1. **Concurrencia**: JSON se corrompe con múltiples usuarios simultáneos
2. **Escalabilidad**: PostgreSQL maneja millones de registros
3. **Seguridad**: Transacciones ACID, backups automáticos
4. **Performance**: Índices y queries optimizadas
5. **Relaciones**: Integridad referencial entre usuarios, bots, documentos

---

## 📋 PASOS PARA MIGRACIÓN A POSTGRESQL

### Paso 1: Instalar PostgreSQL (15 minutos)

**Opción A - Docker (Recomendado):**
```bash
# 1. Instalar Docker Desktop para Windows
# Descargar de: https://www.docker.com/products/docker-desktop

# 2. Iniciar PostgreSQL
cd D:\2025\ChatBot
docker-compose up -d

# 3. Verificar que esté corriendo
docker ps
# Deberías ver: chatbot-postgres
```

**Opción B - Instalación Manual:**
```bash
# 1. Descargar PostgreSQL 15 o superior
# https://www.postgresql.org/download/windows/

# 2. Durante instalación, configurar:
#    - Password: chatbot_password
#    - Puerto: 5432
#    - Database: chatbot_db

# 3. Crear usuario y base de datos manualmente
# Ver: POSTGRESQL_SETUP.md para instrucciones detalladas
```

### Paso 2: Configurar Variables de Entorno (5 minutos)

```bash
# Crear archivo backend/.env con:
DATABASE_URL=postgresql://chatbot_user:chatbot_password@localhost:5432/chatbot_db
USE_DATABASE=true
JWT_SECRET_KEY=tu-clave-secreta-super-segura-cambiala-en-produccion
OPENAI_API_KEY=tu-api-key-de-openai
```

### Paso 3: Crear Tablas (2 minutos)

```bash
cd backend
python init_tables.py
```

Deberías ver:
```
✅ Tablas de base de datos creadas exitosamente
✅ Usuario admin creado: admin@chatbot.com / admin123
```

### Paso 4: Migrar Datos JSON a PostgreSQL (10 minutos)

```bash
# Script automático de migración
cd backend
python migrate_json_to_postgres.py
```

Este script:
- Lee todos los usuarios de `users.json`
- Lee todos los bots de `bots_config.json`
- Migra todo a PostgreSQL preservando IDs y relaciones
- Crea un backup de los JSON originales

### Paso 5: Verificar Migración (5 minutos)

```bash
# 1. Reiniciar backend
# 2. Ir a http://localhost:8000/docs
# 3. Probar endpoints:
#    - POST /auth/login
#    - GET /auth/users
#    - GET /bots/
# 4. Verificar que los datos estén correctos
```

---

## 🔒 SEGURIDAD EN PRODUCCIÓN

### 1. Variables de Entorno
```bash
# NUNCA usar estos valores en producción:
JWT_SECRET_KEY=dev-secret-key-CHANGE-IN-PRODUCTION  # ❌ CAMBIAR
DATABASE_URL=postgresql://chatbot_user:chatbot_password@localhost:5432/chatbot_db  # ❌ CAMBIAR PASSWORD

# Generar clave segura:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. PostgreSQL en Producción
- ✅ Usar contraseñas fuertes (mínimo 16 caracteres)
- ✅ Habilitar SSL/TLS para conexiones
- ✅ Configurar backups automáticos diarios
- ✅ Limitar conexiones por IP
- ✅ Usar usuario con permisos limitados (no `postgres` superuser)

### 3. CORS y Seguridad API
```python
# backend/app/main.py
# Cambiar ANTES de producción:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # ❌ NO usar "*" en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. HTTPS Obligatorio
- ✅ Usar certificado SSL (Let's Encrypt gratis)
- ✅ Redirigir HTTP → HTTPS
- ✅ Configurar HSTS headers

---

## 📦 DEPLOYMENT - OPCIONES

### Opción 1: Railway.app (Más Fácil)
```bash
# 1. Crear cuenta en railway.app
# 2. Conectar repositorio GitHub
# 3. Railway auto-detecta FastAPI + React
# 4. Agregar PostgreSQL desde Railway
# 5. Configurar variables de entorno
# Total: ~20 minutos
```

### Opción 2: Render.com
```bash
# Similar a Railway
# Tier gratuito disponible
# PostgreSQL incluido
```

### Opción 3: DigitalOcean / AWS / GCP
```bash
# Más control, más complejo
# Requiere configuración manual
# Mejor para escala grande
```

---

## 🧪 TESTING ANTES DE PRODUCCIÓN

### Checklist de Testing
- [ ] **Load Testing**: Probar con 100+ usuarios simultáneos
- [ ] **Backup/Restore**: Verificar que backups funcionen
- [ ] **Failover**: ¿Qué pasa si PostgreSQL se cae?
- [ ] **Monitoreo**: Configurar alertas (Sentry, LogRocket)
- [ ] **Performance**: Respuestas < 200ms para endpoints críticos

### Herramientas Recomendadas
```bash
# Load testing
pip install locust
locust -f tests/load_test.py

# Monitoring
# - Sentry para errores
# - Grafana + Prometheus para métricas
# - Uptime Robot para availability
```

---

## 📊 MONITOREO EN PRODUCCIÓN

### Métricas Críticas a Monitorear
1. **Database**
   - Conexiones activas
   - Query latency
   - Espacio en disco

2. **API**
   - Request rate
   - Error rate
   - Response time P95/P99

3. **RAG/AI**
   - Tiempo de respuesta de embeddings
   - Costo de API de OpenAI
   - Calidad de respuestas (feedback users)

---

## 🚀 OPTIMIZACIONES POST-PRODUCCIÓN

### 1. Database Indexing
```sql
-- Ejecutar después de tener datos reales
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_bot_id ON documents(bot_id);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC);
```

### 2. Caching con Redis
```bash
# Para mejorar performance
# Cachear:
# - Embeddings de documentos
# - Respuestas frecuentes
# - Sesiones de usuarios
```

### 3. CDN para Frontend
```bash
# Usar Cloudflare o Vercel
# Para servir assets estáticos rápido globalmente
```

---

## 📞 SOPORTE Y TROUBLESHOOTING

### Si algo falla en Producción
1. **Revisar logs**: `docker logs chatbot-backend`
2. **Verificar DB**: Conexión, espacio, queries lentas
3. **Rollback**: `git revert` + redeploy
4. **Contactar**: (Tu información de contacto)

### Documentación de Referencia
- `DATABASE_DESIGN.md` - Estructura de tablas
- `POSTGRESQL_SETUP.md` - Setup detallado
- `RAG_PRECISION_GUIDE.md` - Configuración RAG
- `STREAMING_GUIDE.md` - SSE implementation

---

## ✅ CHECKLIST FINAL ANTES DE DEPLOY

Verifica TODOS estos items:

### Backend
- [ ] PostgreSQL configurado y corriendo
- [ ] Migraciones ejecutadas (`init_tables.py`)
- [ ] Datos migrados de JSON
- [ ] Variables de entorno de producción configuradas
- [ ] JWT_SECRET_KEY cambiado (no usar dev key)
- [ ] CORS configurado solo para tu dominio
- [ ] SSL/HTTPS habilitado
- [ ] Backups automáticos configurados

### Frontend
- [ ] API_URL apunta a dominio de producción
- [ ] Build de producción generado (`npm run build`)
- [ ] Assets servidos desde CDN
- [ ] Service Worker configurado (PWA opcional)
- [ ] Analytics configurado (Google Analytics, Mixpanel, etc.)

### DevOps
- [ ] CI/CD configurado (GitHub Actions)
- [ ] Monitoreo activo (Sentry, Grafana)
- [ ] Alertas configuradas (email, Slack)
- [ ] Rollback plan documentado
- [ ] Escalado automático configurado

### Legal & Compliance
- [ ] Términos de servicio
- [ ] Política de privacidad
- [ ] GDPR compliance (si aplicable)
- [ ] Cookies policy

---

## 🎯 ESTIMACIÓN DE TIEMPO TOTAL

| Tarea | Tiempo Estimado |
|-------|----------------|
| Instalar PostgreSQL | 15 min |
| Configurar variables de entorno | 5 min |
| Crear tablas | 2 min |
| Migrar datos JSON → PostgreSQL | 10 min |
| Testing básico | 15 min |
| Configurar deployment (Railway) | 20 min |
| Testing en producción | 30 min |
| **TOTAL** | **~1.5 horas** |

---

## 📝 NOTAS IMPORTANTES

1. **NO BORRAR archivos JSON hasta confirmar que PostgreSQL funciona 100%**
2. **Hacer backup de PostgreSQL ANTES de cualquier cambio mayor**
3. **Probar en ambiente staging ANTES de producción**
4. **Tener plan de rollback listo**

---

## 🆘 ¿NECESITAS AYUDA?

Si encuentras problemas durante la migración o deployment:
1. Revisa los logs detallados en cada documento MD
2. Consulta la documentación oficial de PostgreSQL
3. Verifica que todas las dependencias estén instaladas
4. Compara con el ambiente de desarrollo que funciona

**¡Buena suerte con el deployment! 🚀**
