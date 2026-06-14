from sqlalchemy import Column, Integer, String, ForeignKey, Date
from src.database.base import Base


class Out(Base):
    __tablename__ = "out"

    idOut = Column(Integer, primary_key=True, autoincrement=True)
    idProd = Column(Integer, ForeignKey("product.idProd"), nullable=False)
    cant = Column(Integer, nullable=False)
    destination = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
