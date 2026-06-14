from sqlalchemy import Column, Integer, Numeric, Date
from src.database.base import Base


class Sell(Base):
    __tablename__ = "sell"

    idSell = Column(Integer, primary_key=True, autoincrement=True)
    cant = Column(Integer, nullable=False)
    revenue = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
