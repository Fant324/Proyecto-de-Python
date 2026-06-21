-- ============================================================
-- LIMPIEZA DE DATOS
-- Sistema de Gestión de Inventario
-- Elimina todos los datos de las tablas y reinicia secuencias
-- ============================================================

BEGIN;

-- Desactivar triggers temporalmente para evitar ejecución de funciones
SET session_replication_role = replica;

-- Eliminar datos y reiniciar secuencias automáticamente (RESTART IDENTITY)
TRUNCATE TABLE prod_sell, product_audit, sell, out, entry, product, users
RESTART IDENTITY CASCADE;

-- Reactivar triggers
SET session_replication_role = origin;

COMMIT;
