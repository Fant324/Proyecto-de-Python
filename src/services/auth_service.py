import bcrypt
from sqlalchemy.orm import Session
from src.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return None
    if check_password(password, user.password):
        return user
    return None


def verify_role(user: User, required_role: str) -> bool:
    return user.role == required_role


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise PermissionError("Se requieren permisos de administrador")
