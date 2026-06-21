# Reporte Técnico — Sistema de Gestión de Inventario

## 1. Resumen del Proyecto

Aplicación de escritorio para la gestión de inventario, productos, entradas, salidas y ventas. Desarrollada en Python con PyQt6 para la interfaz gráfica y PostgreSQL como motor de base de datos. Permite control de stock, generación de reportes por rango de fechas, conversión de moneda (USD ↔ CUP), autenticación de usuarios con tres roles (`admin`, `almacen`, `vendedor`) y reglas de integridad a nivel de base de datos mediante triggers.

---

## 2. Arquitectura General

El proyecto sigue una arquitectura en **3 capas**:

```
┌──────────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN                    │
│       (src/ui/ — PyQt6 Widgets)                   │
│   LoginWindow · MainWindow · TitleBar             │
│   ProductWidget · EntryWidget · OutWidget         │
│   SellWidget · ReportWidget · UserWidget          │
├──────────────────────────────────────────────────┤
│            CAPA DE SERVICIOS                      │
│       (src/services/ — Lógica de negocio)         │
│   auth_service · user_service · product_service   │
│   entry_service · out_service · sell_service      │
│   stock_service · report_service                  │
├──────────────────────────────────────────────────┤
│          CAPA DE ACCESO A DATOS                   │
│    (src/models/ + src/database/ — SQLAlchemy)     │
│   User · Product · Entry · Out · Sell             │
│   ProdSell · ProductAudit · Vistas (solo lectura) │
│   session.py · base.py                            │
├──────────────────────────────────────────────────┤
│          CAPA DE BASE DE DATOS                    │
│    (sql/ — PostgreSQL con triggers)               │
│   tables.sql · views.sql · triggers.sql           │
│   clean.sql · seed.sql                            │
└──────────────────────────────────────────────────┘
```

### Flujo de ejecución

1. `src/main.py` crea tablas vía `Base.metadata.create_all()`, luego llama a `seed.seed_database()` para ejecutar `tables.sql`, `views.sql`, `triggers.sql` y datos de prueba si no existe admin.
2. Se carga el tema oscuro y se muestra `LoginWindow`.
3. El usuario se autentica vía `auth_service.authenticate_user()`.
4. Tras login exitoso, se crea `MainWindow` con un menú lateral dinámico según el rol.
5. Cada widget obtiene una sesión, llama al servicio correspondiente, que valida datos, verifica permisos con `require_role()`, aplica reglas de negocio, adquiere bloqueo pesimista si escribe y persiste vía SQLAlchemy.
6. Triggers de PostgreSQL ejecutan reglas de integridad adicionales automáticamente.

---

## 3. Modelo de Datos (Entidad-Relación)

```
┌──────────┐       ┌───────────┐       ┌──────────┐
│   User   │       │  Product  │       │   Sell   │
├──────────┤       ├───────────┤       ├──────────┤
│ id (PK)  │       │ id_prod   │       │ idSell   │
│ username │       │ (PK)      │       │ (PK)     │
│ password │       │ name      │       │ cant     │
│ role     │       │ cant      │       │ revenue  │
│ is_active│       │ cost      │       │ date     │
│ created  │       │ price     │       └────┬─────┘
│ updated  │       │ is_active │            │
└──────────┘       │ created   │            │
                   │ updated   │            │
                   └─────┬─────┘            │
                         │                  │
              ┌──────────┴──────────┐       │
              │                     │       │
        ┌─────┴─────┐        ┌─────┴─────┐  │
        │   Entry   │        │    Out    │  │
        ├───────────┤        ├───────────┤  │
        │ idEntry   │        │ idOut     │  │
        │ id_prod   │◄──────►│ id_prod   │  │
        │ (FK)      │        │ (FK)      │  │
        │ cant      │        │ cant      │  │
        │ date      │        │ dest.     │  │
        │ created   │        │ date      │  │
        │ updated   │        │ created   │  │
        └───────────┘        │ updated   │  │
                             └───────────┘  │
                                    │       │
                                    └───┐   │
                                  ┌─────┴───┴──────┐
                                  │   ProdSell     │
                                  ├────────────────┤
                                  │ id_prod (FK)   │
                                  │ idSell (FK)    │
                                  │ cant           │
                                  └────────────────┘
```
                                                  
```
┌───────────────────┐
│  product_audit    │
├───────────────────┤
│ id (PK)           │
│ product_id        │
│ old_price         │
│ new_price         │
│ changed_at        │
└───────────────────┘
```

### Descripción de tablas

| Tabla | Propósito |
|-------|-----------|
| `users` | Autenticación y roles (admin/almacen/vendedor) |
| `product` | Catálogo de productos con stock, costo y precio |
| `entry` | Registro de entradas (compras/reabastecimiento) |
| `out` | Registro de salidas (traslados, uso interno) |
| `sell` | Cabecera de venta (total unidades e ingreso) |
| `prod_sell` | Detalle de productos por venta (relación N:M) |
| `product_audit` | Auditoría de cambios de precio (old_price, new_price, changed_at) |

### Vistas del sistema

| Vista | Propósito | PK del mapper SQLAlchemy |
|-------|-----------|--------------------------|
| `v_stock_profit` | Ganancia esperada = (precio - costo) × stock (solo activos) | `id_prod` |
| `v_sales_summary` | Total unidades vendidas e ingreso por producto | `id_prod` |
| `v_stock_movements` | Movimientos unificados de entrada y salida | `id_prod` (no único, suficiente para lectura) |

---

## 4. Reglas de Integridad (Triggers)

| Trigger | Evento | Función |
|---------|--------|---------|
| `trg_product_updated_at` | BEFORE UPDATE ON product | Actualiza `updated_at` automáticamente |
| `trg_entry_updated_at` | BEFORE UPDATE ON entry | Actualiza `updated_at` automáticamente |
| `trg_out_updated_at` | BEFORE UPDATE ON out | Actualiza `updated_at` automáticamente |
| `trg_sell_updated_at` | BEFORE UPDATE ON sell | Actualiza `updated_at` automáticamente |
| `trg_users_updated_at` | BEFORE UPDATE ON users | Actualiza `updated_at` automáticamente |
| `trg_audit_price_changes` | AFTER UPDATE OF price ON product | Registra precio anterior y nuevo en `product_audit` |
| `trg_product_price_check` | BEFORE INSERT OR UPDATE ON product | Valida que NEW.price >= NEW.cost (lanza EXCEPTION si no cumple) |

---

## 5. Capa de Servicios (Lógica de Negocio)

### 5.1 `auth_service.py` — Autenticación
- `hash_password()` → genera hash bcrypt con salt aleatorio.
- `check_password()` → verifica contraseña contra hash.
- `authenticate_user()` → busca usuario por username y valida password. Retorna `User` o `None`.
- `verify_role()` → compara rol del usuario con uno requerido.
- `require_role()` → lanza `PermissionError` si el usuario no tiene uno de los roles permitidos.
- `require_admin()` → lanza `PermissionError` si el usuario no es admin.

### 5.2 `user_service.py` — CRUD de usuarios
- Validaciones: username y password no vacíos.
- `delete_user()` verifica permisos de admin e impide eliminar al último administrador.

### 5.3 `product_service.py` — CRUD de productos
- Validaciones: nombre no vacío, costo/precio positivos.
- Soft delete: marca `is_active = False` en lugar de eliminar.

### 5.4 `stock_service.py` — Consulta de stock
- `get_stock()`: consulta el stock actual de un producto (solo lectura, sin bloqueo).

### 5.5 `entry_service.py` — Registro de entradas
- Valida producto_id > 0 y cantidad > 0.
- Obtiene el producto con `SELECT ... FOR UPDATE` y verifica que exista.
- Crea registro `Entry` e incrementa `product.cant` directamente en una transacción.

### 5.6 `out_service.py` — Registro de salidas
- Valida producto, cantidad, destino no vacío y stock suficiente.
- Obtiene el producto con `SELECT ... FOR UPDATE`, verifica stock y descuenta `product.cant` directamente.

### 5.7 `sell_service.py` — Registro de ventas
- Acepta lista de productos con cantidades.
- Obtiene cada producto con `SELECT ... FOR UPDATE` en una sola transacción.
- Valida existencia y stock suficiente para cada producto.
- Calcula ingreso total (`precio × cantidad`).
- Crea `Sell` y asociaciones `ProdSell`, descuenta `product.cant` de cada producto.
- Evita doble bloqueo al operar directamente sobre el producto en lugar de llamar a `stock_service`.

### 5.8 `report_service.py` — Reportes y analítica
- Consultas agregadas con `SUM`, `JOIN` y `GROUP BY`.
- `get_sales_by_product()`: total vendido por producto en un rango de fechas.
- `get_stock_profit()`: ganancia esperada usando la vista `v_stock_profit`.
- `get_total_sales_by_product()`: resumen total de ventas usando `v_sales_summary`.
- `get_stock_movements()`: movimientos unificados usando `v_stock_movements`.
- `get_summary()`: ingreso total, costo total y ganancia total del período.

---

## 6. Roles y Permisos

| Rol | Productos | Entradas | Salidas | Ventas | Reportes | Usuarios |
|-----|-----------|----------|---------|--------|----------|----------|
| admin | CRUD | ✓ | ✓ | ✓ | ✓ | ✓ |
| almacen | CRUD | ✓ | ✓ | ✗ | ✗ | ✗ |
| vendedor | Solo lectura | ✗ | ✗ | ✓ | ✗ | ✗ |

Los tres roles se definen en un ENUM `user_roles` de PostgreSQL y se reflejan en el modelo `User` de SQLAlchemy.

Los permisos se aplican en dos capas:
1. **UI**: el menú lateral solo muestra botones según el rol.
2. **Widgets**: cada widget verifica permisos en su constructor mediante `require_role()`.

---

## 7. Capa de Presentación (Interfaz de Usuario)

### 7.1 `TitleBar` — Barra de título personalizada
- Reemplaza la decoración nativa de ventana (`FramelessWindowHint`).
- Botones: minimizar (`─`), maximizar/restaurar (`☐`/`❐`), cerrar (`✕`).
- Arrastre de ventana mediante eventos de ratón.
- Doble clic para maximizar/restaurar.

### 7.2 `LoginWindow` — Inicio de sesión
- Ventana frameless centrada en la pantalla.
- Campos: usuario, contraseña. Botón "Iniciar Sesión".
- Errores: credenciales incorrectas, campos vacíos.

### 7.3 `MainWindow` — Ventana principal
- Menú lateral (180px) con botones de navegación según rol.
- `QStackedWidget` central que alterna entre widgets sin recrearlos.
- Atajo F11 para pantalla completa.

### 7.4 Widgets de gestión

| Widget | Función | Roles | Diálogo |
|--------|---------|-------|---------|
| `ProductWidget` | CRUD de productos (admin/almacen), solo lectura (vendedor) | Todos | `ProductDialog` |
| `EntryWidget` | Registro de entradas | admin, almacen | `EntryDialog` |
| `OutWidget` | Registro de salidas | admin, almacen | `OutDialog` |
| `SellWidget` | Registro de ventas multi-producto | admin, vendedor | `SellDialog` |
| `ReportWidget` | Reportes por rango de fechas (6 tabs) + exportación CSV + conversión CUP | admin | — |
| `UserWidget` | CRUD de usuarios | admin | `UserDialog` |

### 7.5 `ReportWidget` — Reportes
- 6 pestañas en `QTabWidget`: Entradas, Salidas, Ventas, Ventas por Producto, Productos, Resumen.
- Filtro por rango de fechas con `QDateEdit`.
- Checkbox "Convertir a CUP" + spinbox de tasa de cambio (persistida en `conversion_config.json`).
- Botón "Exportar CSV" que guarda la pestaña activa en formato CSV.

---

## 8. Base de Datos y Conexión

- **Motor:** PostgreSQL vía `psycopg2-binary`.
- **ORM:** SQLAlchemy 2.0 con `DeclarativeBase`.
- **Conexión:** Configurada mediante variables de entorno en `.env`:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stockmanager
DB_USER=postgres
DB_PASSWORD=...
```

- **Migraciones:** Alembic (2 migraciones: esquema inicial + reglas de integridad).
- **String de conexión:** `postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}`

### Scripts SQL

| Archivo | Propósito |
|---------|-----------|
| `sql/tables.sql` | Creación de tablas, ENUMs e índices |
| `sql/views.sql` | Creación de vistas del sistema |
| `sql/triggers.sql` | Funciones y triggers de integridad |
| `sql/seed.sql` | Datos de prueba (admin, 15 productos, movimientos) |
| `sql/clean.sql` | Limpieza completa de datos con reinicio de secuencias |

---

## 9. Seguridad

- Contraseñas hasheadas con **bcrypt** (salt aleatorio).
- Roles de usuario con verificación en UI y widgets.
- Protección de stock con bloqueo pesimista (`SELECT ... FOR UPDATE`) en cada servicio de escritura, evitando doble bloqueo.
- Validación de datos en servidor (servicios) y cliente (diálogos UI).
- Validación precio >= costo a nivel de base de datos (trigger).
- Soft delete en productos y usuarios (`is_active = FALSE`).
- Creación idempotente de esquema: `main.py` ejecuta `seed.seed_database()` que verifica si el admin existe antes de poblar datos.

---

## 10. Despliegue y Ejecución

### Requisitos
- Python 3.10+
- PostgreSQL
- Paquetes en `requirements.txt`

### Instalación

| Sistema | Iniciar app | Limpiar BD |
|---------|------------|------------|
| Linux | `./run.sh` | `./clean.sh` |
| Windows cmd | `run.bat` | `clean.bat` |
| Windows PowerShell | `.\run.ps1` | `.\clean.ps1` |

### Manualmente
```bash
python -m venv venv
source venv/bin/activate                 # Linux
venv\Scripts\activate.bat                # Windows cmd
.\venv\Scripts\Activate.ps1              # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env                     # Editar con datos de PostgreSQL
python src/main.py                       # Crea tablas, vistas, triggers, admin y datos de prueba
```

> `main.py` llama a `seed.seed_database()` que:
> 1. Ejecuta `tables.sql`, `views.sql`, `triggers.sql` (siempre, son idempotentes)
> 2. Si no existe el admin, ejecuta `seed.sql` con datos de prueba
> 3. Si el admin ya existe, omite `seed.sql` para no truncar datos

### Usuario por defecto
| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin   | admin     | admin |

---

## 11. Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| PyQt6 | 6.11.0 | Framework de interfaz gráfica |
| SQLAlchemy | 2.0.50 | ORM para base de datos |
| psycopg2-binary | 2.9.12 | Conexión a PostgreSQL |
| bcrypt | 5.0.0 | Hashing de contraseñas |
| python-dotenv | 1.2.2 | Carga de variables de entorno |
| alembic | 1.18.4 | Migraciones de base de datos |
| pytest | 9.0.3 | Pruebas unitarias |

---

## 12. Pruebas

Framework: **pytest** sobre base de datos PostgreSQL real.

Archivos de prueba en `tests/`:
- `test_models.py` — Pruebas de creación y consulta de modelos.
- `test_services.py` — Pruebas de servicios (auth, productos, entradas, salidas, ventas, reportes).
- `conftest.py` — Fixtures con PostgreSQL: crea tablas, vistas y triggers desde los archivos SQL (scope session). Cada test usa una transacción independiente con rollback automático.

Ejecución:
```bash
# Linux
PYTHONPATH=. python -m pytest tests/ -v

# Windows cmd
set PYTHONPATH=%cd% && python -m pytest tests/ -v

# Windows PowerShell
$env:PYTHONPATH = Get-Location; python -m pytest tests/ -v
```
