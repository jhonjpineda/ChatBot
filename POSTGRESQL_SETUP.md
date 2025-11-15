# 🗄️ Guía de Instalación y Configuración de PostgreSQL

## 📥 Instalación de PostgreSQL

### **Windows**

#### Opción 1: Instalador oficial
```powershell
# Descargar desde: https://www.postgresql.org/download/windows/
# O usar Chocolatey:
choco install postgresql
```

#### Opción 2: Docker (Recomendado)
```powershell
docker run --name chatbot-postgres `
  -e POSTGRES_PASSWORD=postgres `
  -e POSTGRES_USER=postgres `
  -p 5432:5432 `
  -d postgres:15
```

### **Linux (Ubuntu/Debian)**

```bash
# Actualizar repositorios
sudo apt update

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Verificar que esté corriendo
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql
```

### **macOS**

```bash
# Con Homebrew
brew install postgresql@15

# Iniciar servicio
brew services start postgresql@15
```

### **Docker (Todas las plataformas)** ✅ Recomendado

```bash
# Iniciar PostgreSQL en Docker
docker run --name chatbot-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -p 5432:5432 \
  -d postgres:15

# Verificar que esté corriendo
docker ps
```

---

## 🔧 Configuración Inicial

### **1. Crear base de datos y usuario**

#### Opción A: Usando psql (Terminal)

```bash
# Conectar a PostgreSQL como superusuario
# Linux/macOS:
sudo -u postgres psql

# Windows (si instalaste con instalador):
psql -U postgres

# Docker:
docker exec -it chatbot-postgres psql -U postgres
```

Luego ejecutar:

```sql
-- Crear usuario
CREATE USER chatbot_user WITH PASSWORD 'chatbot_pass';

-- Crear base de datos
CREATE DATABASE chatbot_db OWNER chatbot_user;

-- Conectar a la base de datos
\c chatbot_db

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO chatbot_user;

-- Crear extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Salir
\q
```

#### Opción B: Usando script SQL

```bash
# Desde el directorio backend/
# Linux/macOS:
sudo -u postgres psql -f init_db.sql

# Windows:
psql -U postgres -f init_db.sql

# Docker:
docker exec -i chatbot-postgres psql -U postgres < init_db.sql
```

---

## ⚙️ Configuración del Proyecto

### **1. Actualizar .env**

Copia `.env.example` a `.env` y actualiza:

```bash
cd backend
cp .env.example .env
```

Edita `.env`:

```bash
# PostgreSQL Database
DATABASE_URL=postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false  # Cambiar a true para ver queries SQL

# JWT Authentication
JWT_SECRET_KEY=tu-clave-secreta-super-segura-cambia-esto
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 días
```

### **2. Instalar dependencias**

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# O
.venv\Scripts\activate  # Windows

# Instalar dependencias actualizadas
pip install -r requirements.txt
```

### **3. Inicializar tablas**

Hay dos formas:

#### Opción A: Automático al iniciar la app

```python
# El archivo main.py ya incluye:
from app.database.connection import init_db

@app.on_event("startup")
async def startup_event():
    init_db()  # Crea todas las tablas
```

Simplemente inicia la app:

```bash
python -m uvicorn app.main:app --reload
```

#### Opción B: Script manual

```bash
# Crear archivo init_tables.py en backend/
python init_tables.py
```

---

## 🧪 Verificar Instalación

### **1. Verificar que PostgreSQL esté corriendo**

```bash
# Linux/macOS:
sudo systemctl status postgresql

# Windows (si instalaste con instalador):
# Buscar "Services" → PostgreSQL debe estar "Running"

# Docker:
docker ps | grep postgres
```

### **2. Conectar con psql**

```bash
# Conectar a la base de datos
psql -U chatbot_user -d chatbot_db -h localhost

# Debería pedir la contraseña: chatbot_pass
# Si conecta, verás:
chatbot_db=>
```

### **3. Verificar tablas**

Dentro de psql:

```sql
-- Listar todas las tablas
\dt

-- Deberías ver:
-- organizations
-- users
-- bots
-- documents
-- conversations
-- analytics_daily
-- user_sessions
```

### **4. Verificar desde Python**

```bash
cd backend
python
```

```python
from app.database.connection import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tablas creadas:", tables)
# Debe mostrar: ['organizations', 'users', 'bots', ...]
```

---

## 🐳 Docker Compose (Recomendado para Desarrollo)

Crea `docker-compose.yml` en la raíz del proyecto:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: chatbot-postgres
    environment:
      POSTGRES_USER: chatbot_user
      POSTGRES_PASSWORD: chatbot_pass
      POSTGRES_DB: chatbot_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chatbot_user -d chatbot_db"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

Iniciar con:

```bash
docker-compose up -d
```

Ventajas:
- ✅ Configuración automática
- ✅ Datos persistentes
- ✅ Fácil de reiniciar
- ✅ No necesitas instalar PostgreSQL localmente

---

## 🔐 Cambiar Contraseñas en Producción

**⚠️ IMPORTANTE:** Las contraseñas por defecto son solo para desarrollo.

En producción:

```bash
# Generar contraseña segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Actualizar en PostgreSQL
psql -U postgres -c "ALTER USER chatbot_user WITH PASSWORD 'nueva-contraseña-segura';"

# Actualizar DATABASE_URL en .env
DATABASE_URL=postgresql://chatbot_user:nueva-contraseña-segura@localhost:5432/chatbot_db
```

---

## 📊 Comandos Útiles de PostgreSQL

### **Conectar a la base de datos**

```bash
psql -U chatbot_user -d chatbot_db -h localhost
```

### **Comandos dentro de psql**

```sql
-- Listar todas las tablas
\dt

-- Describir una tabla
\d users

-- Ver todos los usuarios
SELECT * FROM users;

-- Ver bots
SELECT bot_id, name, strict_mode FROM bots;

-- Ver usuarios pendientes de aprobación
SELECT email, username, created_at
FROM users
WHERE pending_approval = TRUE;

-- Salir
\q
```

### **Backup de la base de datos**

```bash
# Crear backup
pg_dump -U chatbot_user -d chatbot_db > backup.sql

# Restaurar backup
psql -U chatbot_user -d chatbot_db < backup.sql
```

### **Eliminar todo y empezar de cero**

```bash
# Conectar como superusuario
psql -U postgres

# Eliminar y recrear
DROP DATABASE chatbot_db;
CREATE DATABASE chatbot_db OWNER chatbot_user;
\q

# Volver a inicializar
psql -U postgres -d chatbot_db -f backend/init_db.sql
```

---

## 🚨 Troubleshooting

### **Error: "psql: command not found"**

**Solución:**
- Windows: Agregar PostgreSQL a PATH
- Linux: `sudo apt install postgresql-client`
- macOS: `brew install postgresql@15`
- O usar Docker

### **Error: "connection refused"**

**Solución:**

```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql  # Linux
brew services list  # macOS
docker ps  # Docker

# Iniciar si está parado
sudo systemctl start postgresql  # Linux
brew services start postgresql@15  # macOS
docker start chatbot-postgres  # Docker
```

### **Error: "password authentication failed"**

**Solución:**

```bash
# Verificar contraseña en .env
cat backend/.env | grep DATABASE_URL

# Restablecer contraseña del usuario
sudo -u postgres psql -c "ALTER USER chatbot_user WITH PASSWORD 'chatbot_pass';"
```

### **Error: "database does not exist"**

**Solución:**

```bash
# Crear la base de datos
sudo -u postgres createdb -O chatbot_user chatbot_db

# O manualmente
sudo -u postgres psql -c "CREATE DATABASE chatbot_db OWNER chatbot_user;"
```

---

## ✅ Checklist de Instalación

- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos `chatbot_db` creada
- [ ] Usuario `chatbot_user` creado con contraseña
- [ ] Extensiones `uuid-ossp` y `pg_trgm` instaladas
- [ ] `.env` configurado con `DATABASE_URL` correcta
- [ ] Dependencias Python instaladas (`requirements.txt`)
- [ ] Tablas creadas (ejecutar app o script)
- [ ] Conexión verificada con psql
- [ ] Tablas visibles con `\dt`

---

## 🎯 Próximos Pasos

Una vez PostgreSQL esté configurado:

1. ✅ Migrar datos de JSON a PostgreSQL
2. ✅ Implementar sistema de aprobación de usuarios
3. ✅ Actualizar servicios para usar SQLAlchemy
4. ✅ Implementar streaming de respuestas
5. ✅ Crear sistema de reportes avanzados

---

**¿Dudas?** Consulta la documentación oficial de PostgreSQL o abre un issue en el repositorio.
