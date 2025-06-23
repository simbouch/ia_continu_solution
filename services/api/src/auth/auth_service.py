#!/usr/bin/env python3
"""
Authentication Service with JWT
Service d'authentification avec tokens JWT pour l'API
"""

from datetime import UTC, datetime, timedelta
import hashlib
import os
import secrets
import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from pydantic import BaseModel

# Configuration JWT
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-super-secret-key-change-in-production"
)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security scheme
security = HTTPBearer()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    username: str
    role: str


class User(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: str


class AuthService:
    """Service d'authentification"""

    def __init__(self, db_path: str = "data/ia_continu_solution.db"):
        self.db_path = db_path
        self.ensure_auth_tables()

    def ensure_auth_tables(self):
        """Créer les tables d'authentification si elles n'existent pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table des utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0
            )
        """)

        # Table des tokens (pour révocation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token_hash TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                is_revoked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Table des sessions de login
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                failure_reason TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        conn.commit()

        # Créer un utilisateur admin par défaut
        self.create_default_admin()

        conn.close()

    def create_default_admin(self):
        """Créer un utilisateur admin par défaut"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Vérifier si l'admin existe déjà
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if cursor.fetchone():
            conn.close()
            return

        # Créer l'admin
        password = "admin123"  # Mot de passe par défaut
        salt = secrets.token_hex(32)
        password_hash = self.hash_password(password, salt)

        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            ("admin", "admin@ia-continu.local", password_hash, salt, "admin", True),
        )

        # Créer un utilisateur de test
        test_salt = secrets.token_hex(32)
        test_password_hash = self.hash_password("test123", test_salt)

        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                "testuser",
                "test@ia-continu.local",
                test_password_hash,
                test_salt,
                "user",
                True,
            ),
        )

        conn.commit()
        conn.close()

        print("✅ Utilisateurs par défaut créés:")
        print("   - admin / admin123 (role: admin)")
        print("   - testuser / test123 (role: user)")

    def hash_password(self, password: str, salt: str) -> str:
        """Hasher un mot de passe avec salt"""
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 100000
        ).hex()

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Vérifier un mot de passe"""
        return self.hash_password(password, salt) == password_hash

    def create_user(self, user_data: UserCreate) -> User:
        """Créer un nouvel utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Vérifier si l'utilisateur existe déjà
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?",
                (user_data.username, user_data.email),
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already exists",
                )

            # Créer l'utilisateur
            salt = secrets.token_hex(32)
            password_hash = self.hash_password(user_data.password, salt)

            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, salt, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    user_data.username,
                    user_data.email,
                    password_hash,
                    salt,
                    user_data.role,
                    True,
                ),
            )

            user_id = cursor.lastrowid
            conn.commit()

            # Récupérer l'utilisateur créé
            cursor.execute(
                """
                SELECT id, username, email, role, is_active, created_at
                FROM users WHERE id = ?
            """,
                (user_id,),
            )

            row = cursor.fetchone()
            return User(
                id=row[0],
                username=row[1],
                email=row[2],
                role=row[3],
                is_active=bool(row[4]),
                created_at=row[5],
            )

        finally:
            conn.close()

    def authenticate_user(self, username: str, password: str) -> User | None:
        """Authentifier un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, username, email, password_hash, salt, role, is_active, created_at
                FROM users WHERE username = ? AND is_active = TRUE
            """,
                (username,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            (
                user_id,
                username,
                email,
                password_hash,
                salt,
                role,
                is_active,
                created_at,
            ) = row

            if not self.verify_password(password, password_hash, salt):
                return None

            # Mettre à jour les statistiques de login
            cursor.execute(
                """
                UPDATE users 
                SET last_login = CURRENT_TIMESTAMP, login_count = login_count + 1
                WHERE id = ?
            """,
                (user_id,),
            )
            conn.commit()

            return User(
                id=user_id,
                username=username,
                email=email,
                role=role,
                is_active=bool(is_active),
                created_at=created_at,
            )

        finally:
            conn.close()

    def create_access_token(self, user: User) -> str:
        """Créer un token JWT"""
        expire = datetime.now(UTC) + timedelta(hours=JWT_EXPIRATION_HOURS)

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access",
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Stocker le token dans la base pour pouvoir le révoquer
        self.store_token(user.id, token, expire)

        return token

    def store_token(self, user_id: int, token: str, expires_at: datetime):
        """Stocker un token dans la base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO tokens (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
        """,
            (user_id, token_hash, expires_at),
        )

        conn.commit()
        conn.close()

    def verify_token(self, token: str) -> User | None:
        """Vérifier et décoder un token JWT"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = int(payload.get("sub"))

            if not user_id:
                return None

            # Vérifier si le token n'est pas révoqué
            if self.is_token_revoked(token):
                return None

            # Récupérer l'utilisateur
            return self.get_user_by_id(user_id)

        except jwt.ExpiredSignatureError:
            return None
        except jwt.DecodeError:
            return None
        except jwt.InvalidSignatureError:
            return None
        except Exception:
            return None

    def is_token_revoked(self, token: str) -> bool:
        """Vérifier si un token est révoqué"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        cursor.execute(
            """
            SELECT is_revoked FROM tokens 
            WHERE token_hash = ? AND expires_at > CURRENT_TIMESTAMP
        """,
            (token_hash,),
        )

        row = cursor.fetchone()
        conn.close()

        return row and row[0]

    def get_user_by_id(self, user_id: int) -> User | None:
        """Récupérer un utilisateur par ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, username, email, role, is_active, created_at
            FROM users WHERE id = ? AND is_active = TRUE
        """,
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            role=row[3],
            is_active=bool(row[4]),
            created_at=row[5],
        )

    def login(self, login_data: UserLogin) -> TokenResponse:
        """Connexion utilisateur"""
        user = self.authenticate_user(login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        access_token = self.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_HOURS * 3600,
            user_id=user.id,
            username=user.username,
            role=user.role,
        )


# Instance globale (sera initialisée dans l'API)
auth_service = None


def get_auth_service():
    """Obtenir l'instance du service d'authentification"""
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Dépendance pour obtenir l'utilisateur actuel"""
    service = get_auth_service()
    user = service.verify_token(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dépendance pour vérifier les droits admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return current_user
