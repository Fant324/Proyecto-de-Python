-- ============================================================
-- TABLAS DEL ESQUEMA
-- Sistema de Gestión de Inventario
-- Motor: PostgreSQL
-- ============================================================

-- Tipo ENUM para roles de usuario
DO $$ BEGIN
    CREATE TYPE user_roles AS ENUM ('admin', 'almacen', 'vendedor');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Agregar valor 'almacen' por si el ENUM ya existía sin él
ALTER TYPE user_roles ADD VALUE IF NOT EXISTS 'almacen';

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
CREATE INDEX IF NOT EXISTS idx_audit_product ON product_audit(product_id);
CREATE INDEX IF NOT EXISTS idx_audit_date ON product_audit(changed_at);
