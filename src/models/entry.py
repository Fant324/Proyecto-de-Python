from sqlalchemy import Column, Integer, ForeignKey, Date
from src.database.base import Base


class Entry(Base):
    __tablename__ = "entry"

    idEntry = Column(Integer, primary_key=True, autoincrement=True)
    idProd = Column(Integer, ForeignKey("product.idProd"), nullable=False)
    cant = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
