# -*- coding: utf-8 -*-
"""
Script para crear usuario administrador
"""
import sys
import io
import uuid
from app.database.connection import SessionLocal
from app.database.models import User
from app.services.auth_service_db import AuthServiceDB

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if __name__ == "__main__":
    db = SessionLocal()

    try:
        # Verificar si ya existe admin
        existing_admin = db.query(User).filter(User.email == 'admin@chatbot.com').first()
        if existing_admin:
            print('Usuario admin ya existe')
            print(f'Email: {existing_admin.email}')
            print(f'Role: {existing_admin.role}')
            print(f'Active: {existing_admin.active}')
        else:
            # Crear usuario admin
            auth_service = AuthServiceDB(db)
            hashed_password = auth_service.hash_password('admin123')

            admin_user = User(
                user_id=uuid.uuid4(),
                email='admin@chatbot.com',
                username='Administrador',
                password_hash=hashed_password,
                role='admin',
                organization_id=None,
                allowed_bots=None,
                pending_approval=False,
                active=True
            )

            db.add(admin_user)
            db.commit()
            print('Usuario admin creado exitosamente!')
            print('')
            print('Credenciales:')
            print('  Email: admin@chatbot.com')
            print('  Password: admin123')
            print('')
            print('Puedes iniciar sesion con estas credenciales.')

    except Exception as e:
        print(f'Error al crear usuario admin: {e}')
        db.rollback()

    finally:
        db.close()
