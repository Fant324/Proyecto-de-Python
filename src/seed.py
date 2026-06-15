"""Script de inicialización - crea las tablas y carga datos de prueba desde archivos SQL"""

import logging
from pathlib import Path
from sqlalchemy import text
from src.database.session import engine, get_session
from src.models.user import User

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BASE_DIR / "sql"


def _execute_sql_file(filename: str) -> None:
    """Ejecuta un archivo SQL directamente contra la base de datos"""
    filepath = SQL_DIR / filename
    if not filepath.exists():
        logger.warning(f"Archivo SQL no encontrado: {filepath}")
        return
    sql = filepath.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))


def seed_database():
    """Crea las tablas con schema.sql y carga datos de prueba con seed.sql si no hay admin"""
    # Crear tablas
    _execute_sql_file("schema.sql")
    logger.info("Esquema de base de datos creado/verificado")

    # Verificar si ya existe el admin
    session = get_session()
    try:
        admin = session.query(User).filter(User.username == "admin").first()
        if admin:
            logger.info(f"El usuario admin ya existe (id={admin.id}), se omite seed")
            return
    finally:
        session.close()

    # Cargar datos de prueba
    _execute_sql_file("seed.sql")
    logger.info("Datos de prueba cargados: usuario admin/admin + 15 productos + movimientos")


if __name__ == "__main__":
    seed_database()
