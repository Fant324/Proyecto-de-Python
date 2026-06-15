-- ============================================================
-- SCRIPT COMPLETO: CREACIÓN DE BASE DE DATOS + DATOS DE PRUEBA
-- Sistema de Gestión de Inventario
-- Motor: PostgreSQL
--
-- NOTA: Los scripts ejecutables están en la carpeta sql/ de la raíz.
--   sql/schema.sql  → CREATE TABLE
--   sql/seed.sql    → Datos de prueba
--   python src/seed.py  → Ejecuta ambos automáticamente
-- ============================================================

-- ============================================================
-- CREACIÓN DE TABLAS
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
    id_prod SERIAL      PRIMARY KEY,
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

-- Tabla: prod_sell (detalle producto-venta, relación N:M)
CREATE TABLE IF NOT EXISTS prod_sell (
    id_prod INTEGER NOT NULL REFERENCES product(id_prod),
    "idSell" INTEGER NOT NULL REFERENCES sell("idSell"),
    cant    INTEGER NOT NULL,
    PRIMARY KEY (id_prod, "idSell")
);

-- ============================================================
-- DATOS DE PRUEBA
-- ============================================================

BEGIN;

-- Limpiar datos existentes (orden correcto por FK)
TRUNCATE TABLE prod_sell, sell, out, entry, product, users RESTART IDENTITY CASCADE;

-- Usuario administrador por defecto (contraseña: admin)
INSERT INTO users (username, password, role)
VALUES ('admin', '$2b$12$8BmhifMrjSRhYetgybhgyONrli11ZNTFNM6YfNnOP8qtTwDV1T41.', 'admin');

-- Productos
INSERT INTO product (id_prod, name, cant, cost, price) VALUES
(1,  'Laptop HP 15',                12,  450.00, 650.00),
(2,  'Mouse Logitech M185',         50,  12.50,  25.00),
(3,  'Teclado Mecánico Redragon',   30,  35.00,  65.00),
(4,  'Monitor LG 24"',             8,   120.00, 180.00),
(5,  'SSD Kingston 480GB',          25,  40.00,  65.00),
(6,  'Memoria RAM 8GB DDR4',        40,  28.00,  45.00),
(7,  'Impresora Epson L3150',       5,   180.00, 260.00),
(8,  'Cable HDMI 2m',               100, 3.00,   8.00),
(9,  'Silla Gamer',                 7,   150.00, 220.00),
(10, 'Webcam Logitech C270',        15,  35.00,  55.00),
(11, 'Auriculares HyperX',          20,  45.00,  75.00),
(12, 'Disco Duro Externo 1TB',      10,  55.00,  85.00),
(13, 'Router TPLink AC1200',        12,  40.00,  65.00),
(14, 'Pendrive 64GB',               60,  8.00,   15.00),
(15, 'Base Refrigeradora Notebook', 18,  20.00,  35.00);

SELECT setval('product_id_prod_seq', 15);

-- Entradas (historial de ingresos de stock)
INSERT INTO entry (id_prod, cant, date) VALUES
(1,  15, '2026-05-15'),
(2,  60, '2026-05-18'),
(3,  40, '2026-05-20'),
(4,  10, '2026-05-22'),
(5,  30, '2026-05-25'),
(6,  50, '2026-05-28'),
(7,  8,  '2026-06-01'),
(8,  150,'2026-06-03'),
(9,  10, '2026-06-05'),
(10, 20, '2026-06-06'),
(11, 30, '2026-06-06'),
(14, 80, '2026-06-10'),
(13, 15, '2026-06-11'),
(15, 20, '2026-06-12'),
(12, 12, '2026-06-13');

-- Salidas (historial de egresos de stock)
INSERT INTO out (id_prod, cant, destination, date) VALUES
(2,  10, 'Traslado a sucursal Norte',          '2026-05-19'),
(4,  2,  'Producto dañado - baja',              '2026-05-24'),
(1,  3,  'Préstamo a cliente',                  '2026-05-30'),
(3,  5,  'Devolución a proveedor',             '2026-06-02'),
(8,  10, 'Consumo interno',                     '2026-06-04'),
(5,  5,  'Traslado a sucursal Sur',            '2026-06-07'),
(14, 10, 'Donación',                            '2026-06-09'),
(11, 8,  'Venta por mayor (fuera del sistema)', '2026-06-12');

-- Venta #1: Laptop HP 15 x2 + Mouse Logitech x5
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (1, 7, 1425.00, '2026-06-08');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (1, 1, 2),
  (2, 1, 5);

-- Venta #2: SSD Kingston x3 + Cable HDMI x15
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (2, 18, 315.00, '2026-06-11');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (5, 2, 3),
  (8, 2, 15);

-- Venta #3: Monitor LG 24" x1 + Auriculares HyperX x2 + Pendrive x5
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (3, 8, 405.00, '2026-06-14');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (4,  3, 1),
  (11, 3, 2),
  (14, 3, 5);

SELECT setval('"sell_idSell_seq"', 3);

COMMIT;
