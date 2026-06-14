from sqlalchemy.orm import Session
from src.models.user import User


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    return session.query(User).filter(
        User.username == username,
        User.password == password,
    ).first()


def verify_role(user: User, required_role: str) -> bool:
    return user.role == required_role


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise PermissionError("Se requieren permisos de administrador")
