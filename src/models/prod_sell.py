from sqlalchemy import Column, Integer, ForeignKey
from src.database.base import Base


class ProdSell(Base):
    __tablename__ = "prod_sell"

    id_prod = Column(Integer, ForeignKey("product.id_prod"), primary_key=True)
    idSell = Column(Integer, ForeignKey("sell.idSell"), primary_key=True)
    cant = Column(Integer, nullable=False)
