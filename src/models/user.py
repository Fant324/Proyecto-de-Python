from sqlalchemy import Column, Integer, String, Enum
from src.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("admin", "vendedor", name="user_roles"), nullable=False, default="vendedor")
