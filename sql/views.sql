-- ============================================================
-- VISTAS
-- Sistema de Gestión de Inventario
-- ============================================================

CREATE OR REPLACE VIEW v_stock_profit AS
SELECT id_prod, name, cant AS stock, cost, price,
       (price - cost) * cant AS expected_profit
FROM product
WHERE is_active = TRUE;

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
