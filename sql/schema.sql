-- ============================================================
-- ESQUEMA DE BASE DE DATOS
-- Sistema de Gestión de Inventario
-- Motor: PostgreSQL
-- ============================================================

-- Tipo ENUM para roles de usuario
DO $$ BEGIN
    CREATE TYPE user_roles AS ENUM ('admin', 'vendedor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Tabla: users (autenticación y roles)
CREATE TABLE IF NOT EXISTS users (
    id         SERIAL       PRIMARY KEY,
    username   VARCHAR(50)  UNIQUE NOT NULL,
    password   VARCHAR(255) NOT NULL,
    role       user_roles   NOT NULL DEFAULT 'vendedor',
    created_at TIMESTAMPTZ  DEFAULT NOW(),
    updated_at TIMESTAMPTZ  DEFAULT NOW(),
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE
);

-- Tabla: product (catálogo de productos)
CREATE TABLE IF NOT EXISTS product (
    id_prod    SERIAL        PRIMARY KEY,
    name       VARCHAR(100)  NOT NULL,
    cant       INTEGER       NOT NULL DEFAULT 0 CHECK (cant >= 0),
    cost       NUMERIC(10,2) NOT NULL CHECK (cost >= 0),
    price      NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    created_at TIMESTAMPTZ   DEFAULT NOW(),
    updated_at TIMESTAMPTZ   DEFAULT NOW(),
    is_active  BOOLEAN       NOT NULL DEFAULT TRUE
);

-- Tabla: entry (entradas de inventario)
CREATE TABLE IF NOT EXISTS entry (
    "idEntry"  SERIAL       PRIMARY KEY,
    id_prod    INTEGER      NOT NULL REFERENCES product(id_prod),
    cant       INTEGER      NOT NULL CHECK (cant > 0),
    date       DATE         NOT NULL,
    created_at TIMESTAMPTZ  DEFAULT NOW(),
    updated_at TIMESTAMPTZ  DEFAULT NOW()
);

-- Tabla: out (salidas de inventario)
CREATE TABLE IF NOT EXISTS out (
    "idOut"      SERIAL        PRIMARY KEY,
    id_prod      INTEGER       NOT NULL REFERENCES product(id_prod),
    cant         INTEGER       NOT NULL CHECK (cant > 0),
    destination  VARCHAR(200)  NOT NULL,
    date         DATE          NOT NULL,
    created_at   TIMESTAMPTZ   DEFAULT NOW(),
    updated_at   TIMESTAMPTZ   DEFAULT NOW()
);

-- Tabla: sell (cabecera de ventas)
CREATE TABLE IF NOT EXISTS sell (
    "idSell"   SERIAL        PRIMARY KEY,
    cant       INTEGER       NOT NULL,
    revenue    NUMERIC(10,2) NOT NULL,
    date       DATE          NOT NULL,
    created_at TIMESTAMPTZ   DEFAULT NOW(),
    updated_at TIMESTAMPTZ   DEFAULT NOW()
);

-- Tabla: prod_sell (detalle producto-venta)
CREATE TABLE IF NOT EXISTS prod_sell (
    id_prod INTEGER NOT NULL REFERENCES product(id_prod),
    "idSell" INTEGER NOT NULL REFERENCES sell("idSell"),
    cant    INTEGER NOT NULL,
    PRIMARY KEY (id_prod, "idSell")
);

-- Tabla: auditoria de cambios de precio
CREATE TABLE IF NOT EXISTS product_audit (
    id         SERIAL       PRIMARY KEY,
    product_id INTEGER      NOT NULL,
    old_price  FLOAT,
    new_price  FLOAT,
    changed_at TIMESTAMPTZ  DEFAULT NOW()
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_entry_date ON entry(date);
CREATE INDEX IF NOT EXISTS idx_out_date ON out(date);
CREATE INDEX IF NOT EXISTS idx_sell_date ON sell(date);
CREATE INDEX IF NOT EXISTS idx_entry_product ON entry(id_prod);
CREATE INDEX IF NOT EXISTS idx_out_product ON out(id_prod);
CREATE INDEX IF NOT EXISTS idx_prodsell_product ON prod_sell(id_prod);
CREATE INDEX IF NOT EXISTS idx_prodsell_sell ON prod_sell("idSell");

-- Vistas
CREATE OR REPLACE VIEW v_stock_profit AS
SELECT id_prod, name, cant AS stock, cost, price,
       (price - cost) * cant AS expected_profit
FROM product;

CREATE OR REPLACE VIEW v_sales_summary AS
SELECT p.id_prod, p.name,
       COALESCE(SUM(ps.cant), 0) AS total_units_sold,
       COALESCE(SUM(ps.cant * p.price), 0) AS total_revenue
FROM product p
LEFT JOIN prod_sell ps ON p.id_prod = ps.id_prod
GROUP BY p.id_prod;

CREATE OR REPLACE VIEW v_stock_movements AS
SELECT id_prod, cant, date, 'ENTRY' AS type FROM entry
UNION ALL
SELECT id_prod, cant, date, 'OUT' AS type FROM out;

-- Funcion y triggers para updated_at automatico
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_product_updated_at ON product;
CREATE TRIGGER trg_product_updated_at
BEFORE UPDATE ON product FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS trg_entry_updated_at ON entry;
CREATE TRIGGER trg_entry_updated_at
BEFORE UPDATE ON entry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS trg_out_updated_at ON out;
CREATE TRIGGER trg_out_updated_at
BEFORE UPDATE ON out FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS trg_sell_updated_at ON sell;
CREATE TRIGGER trg_sell_updated_at
BEFORE UPDATE ON sell FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger de auditoria de cambios de precio
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

DROP TRIGGER IF EXISTS trg_audit_price_changes ON product;
CREATE TRIGGER trg_audit_price_changes
AFTER UPDATE ON product FOR EACH ROW EXECUTE FUNCTION audit_price_change();
