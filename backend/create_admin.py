"""
Script para crear el primer usuario ADMIN en la base de datos PostgreSQL.
Ejecutar: python create_admin.py
"""
import sys
import uuid
from sqlalchemy.orm import Session

# Agregar el path del proyecto
sys.path.insert(0, '/home/user/ChatBot/backend')

from app.database.connection import SessionLocal, init_db
from app.services.auth_service_db import AuthServiceDB
from app.schemas.user import UserCreate, UserRole

def create_admin_user():
    """Crea el primer usuario administrador"""

    # Datos del admin
    print("\n" + "="*60)
    print("🔧 CREACIÓN DE USUARIO ADMINISTRADOR")
    print("="*60 + "\n")

    email = input("Email del admin (ej: admin@example.com): ").strip()
    username = input("Nombre de usuario (ej: Admin): ").strip()
    password = input("Contraseña: ").strip()

    if not email or not username or not password:
        print("❌ Error: Todos los campos son obligatorios")
        return

    # Confirmar
    print(f"\n📋 Datos a crear:")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Role: ADMIN")
    print(f"   Organization: Nueva (auto-generada)")

    confirm = input("\n¿Confirmar creación? (s/n): ").strip().lower()

    if confirm != 's':
        print("❌ Cancelado")
        return

    # Inicializar DB
    print("\n⏳ Inicializando base de datos...")
    init_db()

    # Crear usuario
    db: Session = SessionLocal()
    try:
        auth_service = AuthServiceDB(db)

        # Crear organización automáticamente
        organization_id = uuid.uuid4()

        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            role=UserRole.ADMIN,
            organization_id=organization_id,
            allowed_bots=[]
        )

        print("⏳ Creando usuario administrador...")
        user = auth_service.register(user_data, auto_approve=True)

        print("\n" + "="*60)
        print("✅ USUARIO ADMINISTRADOR CREADO EXITOSAMENTE")
        print("="*60)
        print(f"\n📧 Email: {user.email}")
        print(f"👤 Username: {user.username}")
        print(f"🔑 User ID: {user.user_id}")
        print(f"🏢 Organization ID: {user.organization_id}")
        print(f"👔 Role: {user.role}")
        print(f"✅ Active: {user.active}")
        print(f"✅ Approved: {not user.pending_approval}")
        print("\n🎉 Ahora puedes hacer login con estas credenciales!\n")

    except ValueError as e:
        print(f"\n❌ Error al crear usuario: {e}")
        print("   (Puede que el email ya exista en la base de datos)\n")

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}\n")
        import traceback
        traceback.print_exc()
