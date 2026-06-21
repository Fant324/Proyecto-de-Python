from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func
from src.database.base import Base


class ProductAudit(Base):
    __tablename__ = "product_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    old_price = Column(Float)
    new_price = Column(Float)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
