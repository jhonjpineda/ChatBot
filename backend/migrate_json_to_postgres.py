"""
Script para migrar datos de JSON a PostgreSQL

Este script lee los archivos JSON existentes y migra toda la data
a PostgreSQL preservando IDs y relaciones.

Uso:
    python migrate_json_to_postgres.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Importar modelos de SQLAlchemy
from app.database.connection import get_db, engine
from app.database.models import User, Bot, Document, ChatHistory, Approval, Organization
from app.database.base import Base
import bcrypt


def backup_json_files():
    """Crear backup de archivos JSON antes de migrar"""
    print("📦 Creando backup de archivos JSON...")

    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    files_to_backup = [
        "users.json",
        "bots_config.json",
        "analytics_data.json"
    ]

    for filename in files_to_backup:
        if os.path.exists(filename):
            backup_path = backup_dir / f"{filename}.backup_{timestamp}"
            with open(filename, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"   ✅ Backup creado: {backup_path}")

    print("✅ Backups completados\n")


def migrate_users(db):
    """Migrar usuarios de users.json a PostgreSQL"""
    print("👥 Migrando usuarios...")

    if not os.path.exists("users.json"):
        print("   ⚠️  users.json no encontrado, creando usuario admin por defecto")
        create_default_admin(db)
        return

    with open("users.json", 'r', encoding='utf-8') as f:
        users_data = json.load(f)

    migrated = 0
    for user_data in users_data:
        try:
            # Verificar si el usuario ya existe
            existing = db.query(User).filter(User.email == user_data['email']).first()
            if existing:
                print(f"   ⚠️  Usuario ya existe: {user_data['email']}")
                continue

            # Crear nuevo usuario
            user = User(
                user_id=user_data['user_id'],
                email=user_data['email'],
                username=user_data['username'],
                hashed_password=user_data['hashed_password'],
                role=user_data['role'],
                organization_id=user_data.get('organization_id'),
                active=user_data.get('active', True),
                created_at=datetime.fromisoformat(user_data['created_at']),
                updated_at=datetime.fromisoformat(user_data['updated_at'])
            )

            # Manejar allowed_bots (puede ser None, lista vacía, o lista con elementos)
            if 'allowed_bots' in user_data:
                user.allowed_bots = user_data['allowed_bots']

            db.add(user)
            migrated += 1
            print(f"   ✅ Migrado: {user_data['email']}")

        except Exception as e:
            print(f"   ❌ Error migrando {user_data.get('email', 'unknown')}: {e}")

    db.commit()
    print(f"✅ {migrated} usuarios migrados\n")


def create_default_admin(db):
    """Crear usuario admin por defecto"""
    # Verificar si ya existe
    existing = db.query(User).filter(User.email == "admin@chatbot.com").first()
    if existing:
        print("   ✅ Usuario admin ya existe")
        return

    # Crear password hash
    password = "admin123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    admin = User(
        email="admin@chatbot.com",
        username="Admin",
        hashed_password=hashed.decode('utf-8'),
        role="admin",
        active=True
    )

    db.add(admin)
    db.commit()
    print("   ✅ Usuario admin creado: admin@chatbot.com / admin123")


def migrate_bots(db):
    """Migrar bots de bots_config.json a PostgreSQL"""
    print("🤖 Migrando bots...")

    if not os.path.exists("bots_config.json"):
        print("   ⚠️  bots_config.json no encontrado, saltando migración de bots")
        return

    with open("bots_config.json", 'r', encoding='utf-8') as f:
        bots_data = json.load(f)

    migrated = 0
    for bot_data in bots_data:
        try:
            # Verificar si el bot ya existe
            existing = db.query(Bot).filter(Bot.bot_id == bot_data['bot_id']).first()
            if existing:
                print(f"   ⚠️  Bot ya existe: {bot_data['bot_id']}")
                continue

            # Crear nuevo bot
            bot = Bot(
                bot_id=bot_data['bot_id'],
                name=bot_data['name'],
                description=bot_data.get('description'),
                system_prompt=bot_data['system_prompt'],
                temperature=bot_data.get('temperature', 0.7),
                max_tokens=bot_data.get('max_tokens', 500),
                retrieval_k=bot_data.get('retrieval_k', 5),
                active=bot_data.get('active', True),
                metadata=bot_data.get('metadata', {}),
                created_by=None  # No tenemos esta info en JSON
            )

            db.add(bot)
            migrated += 1
            print(f"   ✅ Migrado: {bot_data['name']}")

        except Exception as e:
            print(f"   ❌ Error migrando {bot_data.get('name', 'unknown')}: {e}")

    db.commit()
    print(f"✅ {migrated} bots migrados\n")


def migrate_analytics(db):
    """Migrar datos de analytics a chat_history"""
    print("📊 Migrando analytics...")

    if not os.path.exists("analytics_data.json"):
        print("   ⚠️  analytics_data.json no encontrado, saltando migración de analytics")
        return

    with open("analytics_data.json", 'r', encoding='utf-8') as f:
        analytics_data = json.load(f)

    migrated = 0
    for interaction in analytics_data:
        try:
            # Crear registro en chat_history
            chat = ChatHistory(
                bot_id=interaction['bot_id'],
                question=interaction['question'],
                answer=interaction['answer'],
                sources_count=interaction.get('sources_count', 0),
                response_time_ms=interaction.get('response_time_ms', 0),
                question_length=len(interaction['question']),
                answer_length=len(interaction['answer']),
                metadata=interaction.get('metadata', {})
            )

            # Usar timestamp si existe
            if 'timestamp' in interaction:
                chat.created_at = datetime.fromisoformat(interaction['timestamp'])

            db.add(chat)
            migrated += 1

        except Exception as e:
            print(f"   ❌ Error migrando interacción: {e}")

    db.commit()
    print(f"✅ {migrated} interacciones migradas\n")


def verify_migration(db):
    """Verificar que la migración fue exitosa"""
    print("🔍 Verificando migración...")

    users_count = db.query(User).count()
    bots_count = db.query(Bot).count()
    chats_count = db.query(ChatHistory).count()

    print(f"   📊 Usuarios en DB: {users_count}")
    print(f"   📊 Bots en DB: {bots_count}")
    print(f"   📊 Interacciones en DB: {chats_count}")

    if users_count == 0:
        print("   ⚠️  ADVERTENCIA: No hay usuarios en la base de datos")

    if bots_count == 0:
        print("   ⚠️  ADVERTENCIA: No hay bots en la base de datos")

    print("\n✅ Verificación completada")


def main():
    """Función principal de migración"""
    print("=" * 60)
    print("🚀 MIGRACIÓN DE JSON A POSTGRESQL")
    print("=" * 60)
    print()

    # Verificar que las tablas existan
    print("Verificando tablas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas verificadas\n")
    except Exception as e:
        print(f"❌ Error verificando tablas: {e}")
        print("Por favor ejecuta primero: python init_tables.py")
        return

    # Crear backup
    backup_json_files()

    # Obtener sesión de DB
    db = next(get_db())

    try:
        # Migrar en orden
        migrate_users(db)
        migrate_bots(db)
        migrate_analytics(db)

        # Verificar
        verify_migration(db)

        print()
        print("=" * 60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print()
        print("Próximos pasos:")
        print("1. Verificar los datos en PostgreSQL")
        print("2. Probar el login y funcionalidades")
        print("3. Configurar USE_DATABASE=true en .env")
        print("4. Reiniciar el backend")
        print()
        print("Los archivos JSON originales están respaldados en la carpeta 'backups/'")
        print()

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("Los datos en PostgreSQL pueden estar incompletos.")
        print("Revisa los logs arriba para más detalles.")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
