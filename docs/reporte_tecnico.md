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

1. `src/main.py` carga el tema oscuro (`styles_dark.qss`) y muestra `LoginWindow`.
2. El usuario se autentica vía `auth_service.authenticate_user()`.
3. Tras login exitoso, se crea `MainWindow` con un menú lateral dinámico según el rol.
4. Cada widget interactúa con su servicio correspondiente, que valida datos, verifica permisos con `require_role()`, aplica reglas de negocio y persiste vía SQLAlchemy.
5. Triggers de PostgreSQL ejecutan reglas de integridad adicionales automáticamente.

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
| `product_audit` | Auditoría de cambios de precio |

### Vistas del sistema

| Vista | Propósito |
|-------|-----------|
| `v_stock_profit` | Ganancia esperada por producto = (precio - costo) × stock |
| `v_sales_summary` | Total unidades vendidas e ingreso por producto |
| `v_stock_movements` | Movimientos unificados de entrada y salida |

---

## 4. Reglas de Integridad (Triggers)

| Trigger | Evento | Función |
|---------|--------|---------|
| `trg_product_updated_at` | BEFORE UPDATE ON product | Actualiza `updated_at` automáticamente |
| `trg_entry_updated_at` | BEFORE UPDATE ON entry | Actualiza `updated_at` automáticamente |
| `trg_out_updated_at` | BEFORE UPDATE ON out | Actualiza `updated_at` automáticamente |
| `trg_sell_updated_at` | BEFORE UPDATE ON sell | Actualiza `updated_at` automáticamente |
| `trg_users_updated_at` | BEFORE UPDATE ON users | Actualiza `updated_at` automáticamente |
| `trg_audit_price_changes` | AFTER UPDATE ON product | Registra cambios de precio en `product_audit` |
| `trg_product_price_check` | BEFORE INSERT OR UPDATE ON product | Valida que precio >= costo |

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

### 5.4 `stock_service.py` — Control de stock (concurrencia)
- Usa `SELECT ... FOR UPDATE` (bloqueo pesimista) para operaciones atómicas.
- `add_stock()` y `remove_stock()` modifican el stock de forma segura.

### 5.5 `entry_service.py` — Registro de entradas
- Valida producto_id > 0 y cantidad > 0.
- Crea registro `Entry` e incrementa stock vía `stock_service.add_stock()`.

### 5.6 `out_service.py` — Registro de salidas
- Valida producto, cantidad, destino no vacío y stock suficiente.
- Crea registro `Out` y decrementa stock vía `stock_service.remove_stock()`.

### 5.7 `sell_service.py` — Registro de ventas
- Acepta lista de productos con cantidades.
- Valida existencia y stock suficiente para cada producto.
- Calcula ingreso total (`precio × cantidad`).
- Crea `Sell` y asociaciones `ProdSell`, decrementa stock de cada producto.

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
- Protección de stock con bloqueo pesimista (`SELECT ... FOR UPDATE`).
- Validación de datos en servidor (servicios) y cliente (diálogos UI).
- Validación precio >= costo a nivel de base de datos (trigger).
- Soft delete en productos y usuarios.

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
python src/seed.py                       # Crea tablas, usuario admin/admin y datos de prueba
python src/main.py
```

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
- `conftest.py` — Fixtures con PostgreSQL y rollback automático por prueba.

Ejecución:
```bash
# Linux
PYTHONPATH=. python -m pytest tests/ -v

# Windows cmd
set PYTHONPATH=%cd% && python -m pytest tests/ -v

# Windows PowerShell
$env:PYTHONPATH = Get-Location; python -m pytest tests/ -v
```
