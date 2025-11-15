-- Script de inicialización de PostgreSQL
-- Ejecutar como superusuario de PostgreSQL

-- Crear usuario de la base de datos
CREATE USER chatbot_user WITH PASSWORD 'chatbot_pass';

-- Crear base de datos
CREATE DATABASE chatbot_db OWNER chatbot_user;

-- Conectar a la base de datos
\c chatbot_db

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO chatbot_user;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- Para gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- Para búsquedas de texto similares

-- Mensaje de confirmación
SELECT 'Base de datos chatbot_db creada exitosamente!' AS status;
