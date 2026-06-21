"""Módulo de servicios de autenticación - hash de contraseñas, verificación de credenciales y roles"""

import logging
import bcrypt
from sqlalchemy.orm import Session
from src.models.user import User

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña usando bcrypt con salt aleatorio"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    """Busca al usuario por nombre de usuario y valida su contraseña; retorna el usuario si es correcta o None si falla"""
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return None
    if check_password(password, user.password):
        return user
    return None


def verify_role(user: User, required_role: str) -> bool:
    """Comprueba si el rol del usuario coincide con el rol requerido"""
    return user.role == required_role


def require_role(user: User, *allowed_roles: str) -> None:
    """Verifica que el usuario tenga uno de los roles permitidos; lanza PermissionError si no"""
    if user.role not in allowed_roles:
        roles_str = ", ".join(allowed_roles)
        raise PermissionError(f"Se requieren permisos de {roles_str}")


def require_admin(user: User) -> None:
    """Verifica que el usuario sea administrador; lanza PermissionError si no lo es"""
    require_role(user, "admin")
