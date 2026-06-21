from sqlalchemy import Column, Integer, Date, String, Table, MetaData
from sqlalchemy.orm import registry

view_registry = registry()
view_metadata = MetaData()

view_table = Table(
    "v_stock_movements",
    view_metadata,
    Column("id_prod", Integer),
    Column("cant", Integer),
    Column("date", Date),
    Column("type", String),
    extend_existing=True,
)


@view_registry.mapped
class VStockMovement:
    __table__ = view_table
    __mapper_args__ = {"primary_key": [view_table.c.id_prod]}

    def __repr__(self):
        return f"<VStockMovement(id_prod={self.id_prod}, type='{self.type}')>"
