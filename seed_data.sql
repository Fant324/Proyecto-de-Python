-- ============================================================
-- DATOS DE PRUEBA PARA SISTEMA DE GESTIÓN DE INVENTARIO
-- ============================================================
-- Ejecutar después de crear las tablas (alembic upgrade head
-- o ejecutar main.py una vez).
--
-- Uso:
--   psql -U postgres -d stockmanager -f seed_data.sql
-- ============================================================

BEGIN;

-- Limpiar datos existentes (orden correcto por FK)
TRUNCATE TABLE prod_sell, sell, out, entry, product, users RESTART IDENTITY CASCADE;

-- ============================================================
-- USUARIO ADMIN
-- ============================================================
INSERT INTO users (username, password, role)
VALUES ('admin', '$2b$12$8BmhifMrjSRhYetgybhgyONrli11ZNTFNM6YfNnOP8qtTwDV1T41.', 'admin');

-- ============================================================
-- PRODUCTOS
-- ============================================================
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

-- Reiniciar secuencia de id_prod
SELECT setval('product_id_prod_seq', 15);

-- ============================================================
-- ENTRADAS (historial de ingresos de stock)
-- ============================================================
INSERT INTO entry (id_prod, cant, date) VALUES
(1,  15, '2026-05-15'),  -- Laptop HP 15
(2,  60, '2026-05-18'),  -- Mouse Logitech M185
(3,  40, '2026-05-20'),  -- Teclado Mecánico Redragon
(4,  10, '2026-05-22'),  -- Monitor LG 24"
(5,  30, '2026-05-25'),  -- SSD Kingston 480GB
(6,  50, '2026-05-28'),  -- Memoria RAM 8GB DDR4
(7,  8,  '2026-06-01'),  -- Impresora Epson L3150
(8,  150,'2026-06-03'),  -- Cable HDMI 2m
(9,  10, '2026-06-05'),  -- Silla Gamer
(10, 20, '2026-06-06'),  -- Webcam Logitech C270
(11, 30, '2026-06-06'),  -- Auriculares HyperX
(14, 80, '2026-06-10'),  -- Pendrive 64GB
(13, 15, '2026-06-11'),  -- Router TPLink AC1200
(15, 20, '2026-06-12'),  -- Base Refrigeradora Notebook
(12, 12, '2026-06-13');  -- Disco Duro Externo 1TB

-- ============================================================
-- SALIDAS (historial de egresos de stock)
-- ============================================================
INSERT INTO out (id_prod, cant, destination, date) VALUES
(2,  10, 'Traslado a sucursal Norte',            '2026-05-19'),
(4,  2,  'Producto dañado - baja',                '2026-05-24'),
(1,  3,  'Préstamo a cliente',                    '2026-05-30'),
(3,  5,  'Devolución a proveedor',               '2026-06-02'),
(8,  10, 'Consumo interno',                       '2026-06-04'),
(5,  5,  'Traslado a sucursal Sur',              '2026-06-07'),
(14, 10, 'Donación',                              '2026-06-09'),
(11, 8,  'Venta por mayor (fuera del sistema)',   '2026-06-12');

-- ============================================================
-- VENTAS
-- ============================================================

-- Venta #1 - 2026-06-08: Laptop HP 15 x2 + Mouse Logitech x5
-- Revenue: 2*650 + 5*25 = 1425, Units: 7
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (1, 7, 1425.00, '2026-06-08');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (1, 1, 2),
  (2, 1, 5);

-- Venta #2 - 2026-06-11: SSD Kingston x3 + Cable HDMI x15
-- Revenue: 3*65 + 15*8 = 315, Units: 18
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (2, 18, 315.00, '2026-06-11');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (5, 2, 3),
  (8, 2, 15);

-- Venta #3 - 2026-06-14: Monitor LG 24" x1 + Auriculares HyperX x2 + Pendrive x5
-- Revenue: 1*180 + 2*75 + 5*15 = 405, Units: 8
INSERT INTO sell ("idSell", cant, revenue, date) VALUES (3, 8, 405.00, '2026-06-14');
INSERT INTO prod_sell (id_prod, "idSell", cant) VALUES
  (4,  3, 1),
  (11, 3, 2),
  (14, 3, 5);

-- Reiniciar secuencia de idSell
SELECT setval('"sell_idSell_seq"', 3);

COMMIT;
