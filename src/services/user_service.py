"""Módulo de servicios de usuarios - CRUD de usuarios con validaciones y control de roles"""

import logging
from sqlalchemy.orm import Session
from src.models.user import User
from src.services.auth_service import hash_password, require_admin

logger = logging.getLogger(__name__)


def create_user(session: Session, username: str, password: str, role: str = "vendedor") -> User:
    """Crea un usuario validando que username y contraseña no estén vacíos; hashea la contraseña antes de persistir"""
    if not username:
        raise ValueError("Usuario: el nombre de usuario no puede estar vacío")
    if not password:
        raise ValueError("Contraseña: no puede estar vacía")
    user = User(username=username, password=hash_password(password), role=role)
    session.add(user)
    session.commit()
    return user


def get_user(session: Session, user_id: int) -> User | None:
    """Busca un usuario por su ID; retorna None si no existe"""
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    """Busca un usuario por su nombre de usuario; retorna None si no existe"""
    return session.query(User).filter(User.username == username).first()


def get_all_users(session: Session) -> list[User]:
    """Obtiene todos los usuarios ordenados por ID"""
    return session.query(User).order_by(User.id).all()


def update_user(session: Session, user_id: int, **kwargs) -> User | None:
    """Actualiza atributos de un usuario; si se incluye 'password' lo hashea antes de guardar; retorna None si no existe"""
    user = get_user(session, user_id)
    if not user:
        return None
    if "password" in kwargs:
        kwargs["password"] = hash_password(kwargs["password"])
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    session.commit()
    return user


def delete_user(session: Session, user_id: int, current_user: User) -> bool:
    """Elimina un usuario previa verificación de permisos de admin; impide eliminar al último administrador o a sí mismo"""
    require_admin(current_user)
    if user_id == current_user.id:
        raise ValueError("No puedes eliminarte a ti mismo")
    user = get_user(session, user_id)
    if not user:
        return False
    if user.role == "admin":
        admin_count = session.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise ValueError("No se puede eliminar al único administrador")
    session.delete(user)
    session.commit()
    return True
