-- ============================================================
-- FUNCIONES Y TRIGGERS (Reglas de integridad)
-- Sistema de Gestión de Inventario
-- ============================================================

-- Funcion para updated_at automatico
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

-- Validación: precio no puede ser menor que el costo
CREATE OR REPLACE FUNCTION check_price_ge_cost()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price < NEW.cost THEN
        RAISE EXCEPTION 'El precio (%.2f) no puede ser menor que el costo (%.2f)', NEW.price, NEW.cost;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_product_price_check ON product;
CREATE TRIGGER trg_product_price_check
BEFORE INSERT OR UPDATE ON product FOR EACH ROW EXECUTE FUNCTION check_price_ge_cost();
