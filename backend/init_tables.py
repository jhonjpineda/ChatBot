"""
Script para inicializar las tablas de PostgreSQL
Ejecutar una sola vez después de configurar PostgreSQL
"""
from app.database.connection import init_db

if __name__ == "__main__":
    print("🚀 Inicializando base de datos...")
    print("📊 Creando tablas...")

    try:
        init_db()
        print("\n✅ ¡Tablas creadas exitosamente!")
        print("\nTablas creadas:")
        print("  • organizations")
        print("  • users")
        print("  • bots")
        print("  • documents")
        print("  • conversations")
        print("  • analytics_daily")
        print("  • user_sessions")
        print("\n🎉 Base de datos lista para usar!")

    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        print("\nVerifica que:")
        print("  1. PostgreSQL esté corriendo")
        print("  2. La base de datos chatbot_db exista")
        print("  3. El archivo .env tenga la DATABASE_URL correcta")
        print("\nPara más ayuda, consulta POSTGRESQL_SETUP.md")
