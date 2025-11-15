# -*- coding: utf-8 -*-
"""
Script para inicializar las tablas de PostgreSQL
Ejecutar una sola vez después de configurar PostgreSQL
"""
import sys
import io
from app.database.connection import init_db

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    print("Inicializando base de datos...")
    print("Creando tablas...")

    try:
        init_db()
        print("\nTablas creadas exitosamente!")
        print("\nTablas creadas:")
        print("  - organizations")
        print("  - users")
        print("  - bots")
        print("  - documents")
        print("  - conversations")
        print("  - analytics_daily")
        print("  - user_sessions")
        print("\nBase de datos lista para usar!")

    except Exception as e:
        print(f"\nError al crear tablas: {e}")
        print("\nVerifica que:")
        print("  1. PostgreSQL este corriendo")
        print("  2. La base de datos chatbot_db exista")
        print("  3. El archivo .env tenga la DATABASE_URL correcta")
        print("\nPara mas ayuda, consulta POSTGRESQL_SETUP.md")
