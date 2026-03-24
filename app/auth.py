"""
Utilidades de autenticación: hashing de contraseñas y verificación
"""

import hashlib
import os
import logging
from sqlalchemy.orm import Session
from app.models.models import User

logger = logging.getLogger(__name__)


def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Genera hash SHA-256 con salt para una contraseña"""
    if salt is None:
        salt = os.urandom(32).hex()
    pw_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return pw_hash, salt


def hash_password(password: str) -> str:
    """Retorna 'salt:hash' listo para guardar en DB"""
    pw_hash, salt = _hash_password(password)
    return f"{salt}:{pw_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifica una contraseña contra el hash almacenado"""
    try:
        salt, pw_hash = stored_hash.split(":", 1)
        computed, _ = _hash_password(password, salt)
        return computed == pw_hash
    except Exception:
        return False


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Autentica un usuario por email y contraseña. Retorna el User o None."""
    user = db.query(User).filter(User.email == email, User.is_active == 1).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def create_user(db: Session, email: str, name: str, password: str, role: str = "user") -> User:
    """Crea un usuario con contraseña hasheada"""
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Usuario creado: {email} (rol: {role})")
    return user


def ensure_admin_exists(db: Session):
    """Crea el usuario admin por defecto si no existe ningún usuario"""
    from app.config import get_settings
    settings = get_settings()

    if db.query(User).count() == 0:
        admin_email = getattr(settings, "admin_email", "admin@leadreactivation.com")
        admin_password = getattr(settings, "admin_password", "admin1234")
        create_user(db, email=admin_email, name="Administrador", password=admin_password, role="admin")
        logger.info(f"Usuario admin creado por defecto: {admin_email}")
