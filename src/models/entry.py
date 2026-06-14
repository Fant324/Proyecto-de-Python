from sqlalchemy import Column, Integer, ForeignKey, Date
from src.database.base import Base


class Entry(Base):
    __tablename__ = "entry"

    idEntry = Column(Integer, primary_key=True, autoincrement=True)
    id_prod = Column(Integer, ForeignKey("product.id_prod"), nullable=False)
    cant = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
