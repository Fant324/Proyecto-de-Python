"""Script de inicialización - crea el usuario administrador por defecto en la base de datos"""

import logging
from src.database.session import get_session, engine
from src.database.base import Base
from src.models.user import User
from src.services.auth_service import hash_password

logger = logging.getLogger(__name__)


def seed_admin():
    """Crea el usuario admin por defecto si no existe; inicializa las tablas de la base de datos"""
    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        existing = session.query(User).filter(User.username == "admin").first()
        if existing:
            logger.info(f"El usuario admin ya existe (id={existing.id})")
            return
        admin = User(username="admin", password=hash_password("admin"), role="admin")
        session.add(admin)
        session.commit()
        logger.info("Usuario admin creado: admin / admin")
    finally:
        session.close()


if __name__ == "__main__":
    seed_admin()
