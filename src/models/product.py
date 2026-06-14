from sqlalchemy import Column, Integer, String, Numeric
from src.database.base import Base


class Product(Base):
    __tablename__ = "product"

    idProd = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cant = Column(Integer, nullable=False, default=0)
    cost = Column(Numeric(10, 2), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
