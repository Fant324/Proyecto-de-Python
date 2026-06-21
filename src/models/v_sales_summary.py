from sqlalchemy import Column, Integer, String, Numeric, Table, MetaData
from sqlalchemy.orm import registry

view_registry = registry()
view_metadata = MetaData()


@view_registry.mapped
class VSalesSummary:
    __table__ = Table(
        "v_sales_summary",
        view_metadata,
        Column("id_prod", Integer, primary_key=True),
        Column("name", String(100)),
        Column("total_units_sold", Integer),
        Column("total_revenue", Numeric),
        extend_existing=True,
    )

    def __repr__(self):
        return f"<VSalesSummary(id_prod={self.id_prod}, name='{self.name}')>"
