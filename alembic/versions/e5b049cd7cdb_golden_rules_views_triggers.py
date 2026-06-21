"""golden_rules_views_triggers

Revision ID: e5b049cd7cdb
Revises: 93327536220a
Create Date: 2026-06-20 20:29:23.676734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5b049cd7cdb'
down_revision: Union[str, Sequence[str], None] = '93327536220a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- FASE 1: CHECK constraints ---
    op.execute("ALTER TABLE product ADD CONSTRAINT chk_product_price_positive CHECK (price >= 0);")
    op.execute("ALTER TABLE product ADD CONSTRAINT chk_product_cost_positive CHECK (cost >= 0);")
    op.execute("ALTER TABLE product ADD CONSTRAINT chk_product_stock_non_negative CHECK (cant >= 0);")
    op.execute("ALTER TABLE entry ADD CONSTRAINT chk_entry_cant_positive CHECK (cant > 0);")
    op.execute("ALTER TABLE out ADD CONSTRAINT chk_out_cant_positive CHECK (cant > 0);")

    # --- FASE 1: Indexes for JOINS and date filters ---
    op.create_index('idx_entry_date', 'entry', ['date'])
    op.create_index('idx_out_date', 'out', ['date'])
    op.create_index('idx_sell_date', 'sell', ['date'])
    op.create_index('idx_entry_product', 'entry', ['id_prod'])
    op.create_index('idx_out_product', 'out', ['id_prod'])
    op.create_index('idx_prodsell_product', 'prod_sell', ['id_prod'])
    op.create_index('idx_prodsell_sell', 'prod_sell', ['idSell'])

    # --- FASE 2: Timestamps y Soft Delete ---
    op.add_column('product', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('product', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('product', sa.Column('is_active', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False))

    op.add_column('entry', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('entry', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))

    op.add_column('out', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('out', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))

    op.add_column('sell', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('sell', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))

    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False))

    # --- FASE 3: Vistas ---
    op.execute("""
        CREATE VIEW v_stock_profit AS
        SELECT id_prod, name, cant AS stock, cost, price,
               (price - cost) * cant AS expected_profit
        FROM product;
    """)
    op.execute("""
        CREATE VIEW v_sales_summary AS
        SELECT p.id_prod, p.name,
               COALESCE(SUM(ps.cant), 0) AS total_units_sold,
               COALESCE(SUM(ps.cant * p.price), 0) AS total_revenue
        FROM product p
        LEFT JOIN prod_sell ps ON p.id_prod = ps.id_prod
        GROUP BY p.id_prod;
    """)
    op.execute("""
        CREATE VIEW v_stock_movements AS
        SELECT id_prod, cant, date, 'ENTRY' AS type FROM entry
        UNION ALL
        SELECT id_prod, cant, date, 'OUT' AS type FROM out;
    """)

    # --- FASE 4: Funcion y trigger para updated_at ---
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("CREATE TRIGGER trg_product_updated_at BEFORE UPDATE ON product FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER trg_entry_updated_at BEFORE UPDATE ON entry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER trg_out_updated_at BEFORE UPDATE ON out FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER trg_sell_updated_at BEFORE UPDATE ON sell FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # --- FASE 4: Tabla de auditoria de precios ---
    op.create_table('product_audit',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('old_price', sa.Float(), nullable=True),
        sa.Column('new_price', sa.Float(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_price_change()
        RETURNS TRIGGER AS $$
        BEGIN
            IF OLD.price IS DISTINCT FROM NEW.price THEN
                INSERT INTO product_audit (product_id, old_price, new_price)
                VALUES (OLD.id_prod, OLD.price, NEW.price);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("CREATE TRIGGER trg_audit_price_changes AFTER UPDATE ON product FOR EACH ROW EXECUTE FUNCTION audit_price_change();")


def downgrade() -> None:
    # --- Reverse: Triggers y funciones ---
    op.execute("DROP TRIGGER IF EXISTS trg_audit_price_changes ON product;")
    op.execute("DROP FUNCTION IF EXISTS audit_price_change;")
    op.execute("DROP TRIGGER IF EXISTS trg_product_updated_at ON product;")
    op.execute("DROP TRIGGER IF EXISTS trg_entry_updated_at ON entry;")
    op.execute("DROP TRIGGER IF EXISTS trg_out_updated_at ON out;")
    op.execute("DROP TRIGGER IF EXISTS trg_sell_updated_at ON sell;")
    op.execute("DROP TRIGGER IF EXISTS trg_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column;")

    # --- Reverse: Tabla de auditoria ---
    op.drop_table('product_audit')

    # --- Reverse: Vistas ---
    op.execute("DROP VIEW IF EXISTS v_stock_movements;")
    op.execute("DROP VIEW IF EXISTS v_sales_summary;")
    op.execute("DROP VIEW IF EXISTS v_stock_profit;")

    # --- Reverse: Columnas de timestamps y soft delete ---
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('sell', 'updated_at')
    op.drop_column('sell', 'created_at')
    op.drop_column('out', 'updated_at')
    op.drop_column('out', 'created_at')
    op.drop_column('entry', 'updated_at')
    op.drop_column('entry', 'created_at')
    op.drop_column('product', 'is_active')
    op.drop_column('product', 'updated_at')
    op.drop_column('product', 'created_at')

    # --- Reverse: Indices ---
    op.drop_index('idx_prodsell_sell')
    op.drop_index('idx_prodsell_product')
    op.drop_index('idx_out_product')
    op.drop_index('idx_entry_product')
    op.drop_index('idx_sell_date')
    op.drop_index('idx_out_date')
    op.drop_index('idx_entry_date')

    # --- Reverse: CHECK constraints ---
    op.execute("ALTER TABLE out DROP CONSTRAINT IF EXISTS chk_out_cant_positive;")
    op.execute("ALTER TABLE entry DROP CONSTRAINT IF EXISTS chk_entry_cant_positive;")
    op.execute("ALTER TABLE product DROP CONSTRAINT IF EXISTS chk_product_stock_non_negative;")
    op.execute("ALTER TABLE product DROP CONSTRAINT IF EXISTS chk_product_cost_positive;")
    op.execute("ALTER TABLE product DROP CONSTRAINT IF EXISTS chk_product_price_positive;")
