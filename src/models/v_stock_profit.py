from sqlalchemy import Column, Integer, String, Numeric, Table, MetaData
from sqlalchemy.orm import registry

view_registry = registry()
view_metadata = MetaData()


@view_registry.mapped
class VStockProfit:
    __table__ = Table(
        "v_stock_profit",
        view_metadata,
        Column("id_prod", Integer, primary_key=True),
        Column("name", String(100)),
        Column("stock", Integer),
        Column("cost", Numeric(10, 2)),
        Column("price", Numeric(10, 2)),
        Column("expected_profit", Numeric),
        extend_existing=True,
    )

    def __repr__(self):
        return f"<VStockProfit(id_prod={self.id_prod}, name='{self.name}')>"
