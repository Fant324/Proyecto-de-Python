from sqlalchemy.orm import Session
from src.models.user import User


def create_user(session: Session, username: str, password: str, role: str = "vendedor") -> User:
    user = User(username=username, password=password, role=role)
    session.add(user)
    session.commit()
    return user


def get_user(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.query(User).filter(User.username == username).first()


def get_all_users(session: Session) -> list[User]:
    return session.query(User).order_by(User.id).all()


def update_user(session: Session, user_id: int, **kwargs) -> User | None:
    user = get_user(session, user_id)
    if not user:
        return None
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    session.commit()
    return user


def delete_user(session: Session, user_id: int, current_user: User) -> bool:
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
