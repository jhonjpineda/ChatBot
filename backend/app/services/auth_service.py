"""
Servicio de autenticación con JWT y bcrypt.
Gestiona usuarios en users.json.
"""
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.models.user import User, UserCreate, UserLogin, UserUpdate, UserResponse, TokenData, UserRole

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_FILE = "users.json"

class AuthService:
    """Servicio para manejo de autenticación y usuarios"""

    def __init__(self):
        self._ensure_users_file()
        self._ensure_admin_user()

    def _ensure_users_file(self):
        """Crea el archivo de usuarios si no existe"""
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w') as f:
                json.dump({"users": []}, f, indent=2)

    def _ensure_admin_user(self):
        """Crea un usuario admin por defecto si no existe ninguno"""
        users = self._load_users()

        # Verificar si ya existe un admin
        has_admin = any(u.role == UserRole.ADMIN for u in users)

        if not has_admin:
            # Crear admin por defecto
            admin = User(
                user_id=str(uuid.uuid4()),
                email="admin@chatbot.com",
                username="Admin",
                hashed_password=self._hash_password("admin123"),
                role=UserRole.ADMIN,
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            users.append(admin)
            self._save_users(users)
            print("✅ Usuario admin creado: admin@chatbot.com / admin123")

    def _load_users(self) -> List[User]:
        """Carga usuarios del archivo JSON"""
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
        return [User(**u) for u in data.get("users", [])]

    def _save_users(self, users: List[User]):
        """Guarda usuarios en el archivo JSON"""
        with open(USERS_FILE, 'w') as f:
            json.dump({
                "users": [u.dict() for u in users]
            }, f, indent=2, default=str)

    def _hash_password(self, password: str) -> str:
        """Hashea una contraseña"""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: User) -> str:
        """Crea un JWT token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role,
            "exp": expire
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decodifica y valida un JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None:
                return None

            return TokenData(user_id=user_id, email=email, role=role)
        except JWTError:
            return None

    def register(self, user_data: UserCreate) -> User:
        """Registra un nuevo usuario"""
        users = self._load_users()

        # Verificar si el email ya existe
        if any(u.email == user_data.email for u in users):
            raise ValueError("El email ya está registrado")

        # Crear nuevo usuario
        new_user = User(
            user_id=str(uuid.uuid4()),
            email=user_data.email,
            username=user_data.username,
            hashed_password=self._hash_password(user_data.password),
            role=user_data.role,
            organization_id=user_data.organization_id,
            allowed_bots=user_data.allowed_bots,
            active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        users.append(new_user)
        self._save_users(users)

        return new_user

    def login(self, credentials: UserLogin) -> Optional[User]:
        """Autentica un usuario"""
        users = self._load_users()

        # Buscar usuario por email
        user = next((u for u in users if u.email == credentials.email), None)

        if not user:
            return None

        # Verificar contraseña
        if not self._verify_password(credentials.password, user.hashed_password):
            return None

        # Verificar que esté activo
        if not user.active:
            return None

        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por ID"""
        users = self._load_users()
        return next((u for u in users if u.user_id == user_id), None)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        users = self._load_users()
        return next((u for u in users if u.email == email), None)

    def list_users(self, organization_id: Optional[str] = None) -> List[User]:
        """Lista todos los usuarios (opcionalmente filtrados por organización)"""
        users = self._load_users()
        if organization_id:
            users = [u for u in users if u.organization_id == organization_id]
        return users

    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Actualiza un usuario"""
        users = self._load_users()
        user_idx = next((i for i, u in enumerate(users) if u.user_id == user_id), None)

        if user_idx is None:
            return None

        user = users[user_idx]

        # Actualizar campos
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.role is not None:
            user.role = user_update.role
        if user_update.active is not None:
            user.active = user_update.active
        if user_update.allowed_bots is not None:
            user.allowed_bots = user_update.allowed_bots

        user.updated_at = datetime.now()

        users[user_idx] = user
        self._save_users(users)

        return user

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario"""
        users = self._load_users()
        original_count = len(users)
        users = [u for u in users if u.user_id != user_id]

        if len(users) < original_count:
            self._save_users(users)
            return True
        return False

    def user_can_access_bot(self, user: User, bot_id: str) -> bool:
        """Verifica si un usuario puede acceder a un bot"""
        # Admin puede acceder a todo
        if user.role == UserRole.ADMIN:
            return True

        # Si allowed_bots es None, puede acceder a todos
        if user.allowed_bots is None:
            return True

        # Si está en la lista de bots permitidos
        return bot_id in user.allowed_bots
