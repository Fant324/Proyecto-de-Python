from src.database.session import get_session, engine
from src.database.base import Base
from src.models.user import User
from src.services.auth_service import hash_password


def seed_admin():
    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"Admin user already exists (id={existing.id})")
            return
        admin = User(username="admin", password=hash_password("admin"), role="admin")
        session.add(admin)
        session.commit()
        print("Admin user created: admin / admin")
    finally:
        session.close()


if __name__ == "__main__":
    seed_admin()
