-- ============================================================
-- LIMPIEZA DE DATOS
-- Sistema de Gestión de Inventario
-- Elimina todos los datos de las tablas y reinicia secuencias
-- ============================================================

BEGIN;

-- Desactivar triggers temporalmente para evitar ejecución de funciones
SET session_replication_role = replica;

-- Eliminar datos (orden respetando FK: hijos primero, padres después)
TRUNCATE TABLE prod_sell CASCADE;
TRUNCATE TABLE product_audit CASCADE;
TRUNCATE TABLE sell CASCADE;
TRUNCATE TABLE out CASCADE;
TRUNCATE TABLE entry CASCADE;
TRUNCATE TABLE product CASCADE;
TRUNCATE TABLE users CASCADE;

-- Reactivar triggers
SET session_replication_role = origin;

-- Reiniciar secuencias
ALTER SEQUENCE IF EXISTS product_audit_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS sell_idSell_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS out_idOut_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS entry_idEntry_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS product_id_prod_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;

COMMIT;
