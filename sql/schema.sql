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
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50)  UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role     user_roles   NOT NULL DEFAULT 'vendedor'
);

-- Tabla: product (catálogo de productos)
CREATE TABLE IF NOT EXISTS product (
    id_prod SERIAL       PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    cant    INTEGER      NOT NULL DEFAULT 0,
    cost    NUMERIC(10,2) NOT NULL,
    price   NUMERIC(10,2) NOT NULL
);

-- Tabla: entry (entradas de inventario)
CREATE TABLE IF NOT EXISTS entry (
    "idEntry" SERIAL PRIMARY KEY,
    id_prod   INTEGER NOT NULL REFERENCES product(id_prod),
    cant      INTEGER NOT NULL,
    date      DATE    NOT NULL
);

-- Tabla: out (salidas de inventario)
CREATE TABLE IF NOT EXISTS out (
    "idOut"      SERIAL       PRIMARY KEY,
    id_prod      INTEGER      NOT NULL REFERENCES product(id_prod),
    cant         INTEGER      NOT NULL,
    destination  VARCHAR(200) NOT NULL,
    date         DATE         NOT NULL
);

-- Tabla: sell (cabecera de ventas)
CREATE TABLE IF NOT EXISTS sell (
    "idSell" SERIAL       PRIMARY KEY,
    cant     INTEGER      NOT NULL,
    revenue  NUMERIC(10,2) NOT NULL,
    date     DATE         NOT NULL
);

-- Tabla: prod_sell (detalle producto-venta)
CREATE TABLE IF NOT EXISTS prod_sell (
    id_prod INTEGER NOT NULL REFERENCES product(id_prod),
    "idSell" INTEGER NOT NULL REFERENCES sell("idSell"),
    cant    INTEGER NOT NULL,
    PRIMARY KEY (id_prod, "idSell")
);
