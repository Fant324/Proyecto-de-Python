from src.database.session import get_session
from src.models.user import User


def seed_admin():
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == "admin").first()
        if existing:
            print(f"Admin user already exists (id={existing.id})")
            return
        admin = User(username="admin", password="admin", role="admin")
        session.add(admin)
        session.commit()
        print("Admin user created: admin / admin")
    finally:
        session.close()


if __name__ == "__main__":
    seed_admin()
