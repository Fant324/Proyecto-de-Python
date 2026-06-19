# Reporte Técnico — Sistema de Gestión de Inventario

## 1. Resumen del Proyecto

Aplicación de escritorio para la gestión de inventario, productos, entradas, salidas y ventas. Desarrollada en Python con PyQt6 para la interfaz gráfica y PostgreSQL como motor de base de datos. Permite control de stock, generación de reportes por rango de fechas, conversión de moneda (USD ↔ CUP) y autenticación de usuarios con dos roles: `admin` y `vendedor`.

---

## 2. Arquitectura General

El proyecto sigue una arquitectura en **3 capas**:

```
┌──────────────────────────────────────────────┐
│              CAPA DE PRESENTACIÓN             │
│          (src/ui/ — PyQt6 Widgets)            │
│   LoginWindow · MainWindow · TitleBar         │
│   ProductWidget · EntryWidget · OutWidget     │
│   SellWidget · ReportWidget · UserWidget      │
├──────────────────────────────────────────────┤
│               CAPA DE SERVICIOS               │
│          (src/services/ — Lógica de negocio)  │
│   auth_service · user_service · product_service│
│   entry_service · out_service · sell_service   │
│   stock_service · report_service               │
├──────────────────────────────────────────────┤
│             CAPA DE ACCESO A DATOS             │
│   (src/models/ + src/database/ — SQLAlchemy)  │
│   User · Product · Entry · Out · Sell         │
│   ProdSell · session.py · base.py             │
└──────────────────────────────────────────────┘
```

### Flujo de ejecución

1. `src/main.py` crea las tablas en BD, carga el tema oscuro (`styles_dark.qss`), y muestra `LoginWindow`.
2. El usuario se autentica vía `auth_service.authenticate_user()`.
3. Tras login exitoso, se crea `MainWindow` con un menú lateral y un `QStackedWidget` que alterna entre los widgets de cada módulo.
4. Cada widget interactúa con su servicio correspondiente, que valida datos, aplica reglas de negocio y persiste vía SQLAlchemy.

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
└──────────┘       │ cost      │       │ date     │
                   │ price     │       └────┬─────┘
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
        └───────────┘        │ date      │  │
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

### Descripción de tablas

| Tabla | Propósito |
|-------|-----------|
| `users` | Autenticación y roles (admin/vendedor) |
| `product` | Catálogo de productos con stock, costo y precio |
| `entry` | Registro de entradas (compras/reabastecimiento) |
| `out` | Registro de salidas (traslados, uso interno) |
| `sell` | Cabecera de venta (total unidades e ingreso) |
| `prod_sell` | Detalle de productos por venta (relación N:M) |

---

## 4. Capa de Servicios (Lógica de Negocio)

### 4.1 `auth_service.py` — Autenticación
- `hash_password()` → genera hash bcrypt con salt aleatorio.
- `check_password()` → verifica contraseña contra hash.
- `authenticate_user()` → busca usuario por username y valida password. Retorna `User` o `None`.
- `require_admin()` → lanza `PermissionError` si el usuario no es admin.

### 4.2 `user_service.py` — CRUD de usuarios
- Validaciones: username y password no vacíos.
- `delete_user()` impide eliminar al último administrador.

### 4.3 `product_service.py` — CRUD de productos
- Validaciones: nombre no vacío, costo/precio positivos.

### 4.4 `stock_service.py` — Control de stock (concurrencia)
- Usa `SELECT ... FOR UPDATE` (bloqueo pesimista) para operaciones atómicas.
- `add_stock()` y `remove_stock()` modifican el stock de forma segura.

### 4.5 `entry_service.py` — Registro de entradas
- Valida producto_id > 0 y cantidad > 0.
- Crea registro `Entry` e incrementa stock vía `stock_service.add_stock()`.

### 4.6 `out_service.py` — Registro de salidas
- Valida producto, cantidad, destino no vacío y stock suficiente.
- Crea registro `Out` y decrementa stock vía `stock_service.remove_stock()`.

### 4.7 `sell_service.py` — Registro de ventas
- Acepta lista de productos con cantidades.
- Valida existencia y stock suficiente para cada producto.
- Calcula ingreso total (`precio × cantidad`).
- Crea `Sell` y asociaciones `ProdSell`, decrementa stock de cada producto.

### 4.8 `report_service.py` — Reportes y analítica
- Consultas agregadas con `SUM`, `JOIN` y `GROUP BY`.
- `get_sales_by_product()`: total vendido por producto en un rango de fechas.
- `get_stock_profit()`: ganancia esperada = `(precio - costo) × stock` por producto.
- `get_summary()`: ingreso total, costo total y ganancia total del período.

---

## 5. Capa de Presentación (Interfaz de Usuario)

### 5.1 `TitleBar` — Barra de título personalizada
- Reemplaza la decoración nativa de ventana (`FramelessWindowHint`).
- Botones: minimizar (`─`), maximizar/restaurar (`☐`/`❐`), cerrar (`✕`).
- Arrastre de ventana mediante eventos de ratón.
- Doble clic para maximizar/restaurar.

### 5.2 `LoginWindow` — Inicio de sesión
- Ventana frameless centrada en la pantalla.
- Campos: usuario, contraseña. Botón "Iniciar Sesión".
- Errores: credenciales incorrectas, campos vacíos.

### 5.3 `MainWindow` — Ventana principal
- Menú lateral (180px) con botones de navegación.
- Botones visibles según rol: `admin` ve Reportes y Usuarios; `vendedor` no.
- `QStackedWidget` central que alterna entre widgets sin recrearlos.
- Atajo F11 para pantalla completa.

### 5.4 Widgets de gestión

| Widget | Función | Diálogo |
|--------|---------|---------|
| `ProductWidget` | CRUD de productos con tabla y botones Editar/Eliminar | `ProductDialog` (nombre, costo, precio, stock) |
| `EntryWidget` | Registro de entradas de inventario | `EntryDialog` (ID producto, cantidad, fecha) |
| `OutWidget` | Registro de salidas de inventario | `OutDialog` (ID producto, cantidad, destino, fecha) |
| `SellWidget` | Registro de ventas multi-producto | `SellDialog` (selector de productos, cantidades, fecha) |
| `ReportWidget` | Reportes por rango de fechas (6 tabs) + exportación CSV + conversión CUP | — |
| `UserWidget` | CRUD de usuarios (solo admin) | `UserDialog` (usuario, contraseña, rol) |

### 5.5 `ReportWidget` — Reportes
- 6 pestañas en `QTabWidget`: Entradas, Salidas, Ventas, Ventas por Producto, Productos, Resumen.
- Filtro por rango de fechas con `QDateEdit`.
- Checkbox "Convertir a CUP" + spinbox de tasa de cambio (persistida en `conversion_config.json`).
- Botón "Exportar CSV" que guarda la pestaña activa en formato CSV.
- Columnas con `QHeaderView.Stretch` para ocupar todo el ancho.

---

## 6. Temas y Estilos (QSS)

### 6.1 `styles_dark.qss` (tema activo)
Paleta azul/verde oscuro cargada desde `src/main.py`:

| Elemento | Color |
|----------|-------|
| Fondo ventana | `#121820` |
| Paneles/tablas | `#1a2530` |
| Encabezados/TitleBar | `#0d3b4f` |
| Botón primario | `#1f6d49` (verde) |
| Botón secundario | `#2a6d8f` (azul) |
| Texto principal | `#e0e5ec` |
| Bordes | `#2c3e4e` |
| Selección | `#2a5f6b` |

### 6.2 `styles.qss` (tema alternativo)
Tema oscuro genérico con tonos grises (`#1e1e1e`, `#2d2d2d`, `#3a3a3a`).

---

## 7. Base de Datos y Conexión

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

- **Migraciones:** Alembic (1 migración inicial que crea todas las tablas).
- **String de conexión:** `postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}`

---

## 8. Manejo de Errores

Todos los errores están en español y son trazables:

- **Errores de validación** (`ValueError`): mensajes claros desde la capa de servicios (ej: "Stock insuficiente: disponible X, requerido Y").
- **Errores de permisos** (`PermissionError`): "Se requieren permisos de administrador".
- **Errores inesperados**: capturados con `except Exception`, mostrados al usuario con contexto ("Error inesperado: ...") y registrados con `logger.exception()` para trazabilidad completa.

---

## 9. Seguridad

- Contraseñas hasheadas con **bcrypt** (salt aleatorio).
- Roles de usuario: `admin` (acceso completo) y `vendedor` (sin reportes ni gestión de usuarios).
- Protección de stock con bloqueo pesimista (`SELECT ... FOR UPDATE`) para evitar condiciones de carrera.
- Validación de datos en servidor (servicios) y cliente (diálogos UI).

---

## 10. Despliegue y Ejecución

### Requisitos
- Python 3.10+
- PostgreSQL
- Paquetes en `requirements.txt`

### Instalación (Linux)
```bash
./run.sh
```

### Instalación (Windows cmd)
```batch
run.bat
```

### Instalación (Windows PowerShell)
```powershell
.\run.ps1
```

### Manualmente
```bash
python -m venv venv
source venv/bin/activate              # Linux
venv\Scripts\activate.bat             # Windows cmd
.\venv\Scripts\Activate.ps1           # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env                  # Editar con datos de PostgreSQL
python src/seed.py                    # Crea usuario admin/admin
python src/main.py
```

### Usuario por defecto
- **Usuario:** `admin`
- **Contraseña:** `admin`
- **Rol:** admin

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

## 12. Estructura del Proyecto

```
├── doc/                           # Documentación
│   └── reporte_tecnico.md
├── docs/                          # Documentación previa
├── src/                           # Código fuente
│   ├── main.py                    # Punto de entrada
│   ├── seed.py                    # Carga de datos iniciales
│   ├── conversion_config.json     # Tasa de cambio persistida
│   ├── database/
│   │   ├── base.py                # Base declarativa de SQLAlchemy
│   │   └── session.py             # Fábrica de sesiones
│   ├── models/                    # Modelos ORM
│   │   ├── user.py, product.py
│   │   ├── entry.py, out.py, sell.py, prod_sell.py
│   ├── services/                  # Lógica de negocio
│   │   ├── auth_service.py, user_service.py
│   │   ├── product_service.py, stock_service.py
│   │   ├── entry_service.py, out_service.py
│   │   ├── sell_service.py, report_service.py
│   └── ui/                        # Interfaz de usuario
│       ├── login_window.py
│       ├── main_window.py
│       ├── title_bar.py
│       ├── styles.qss, styles_dark.qss
│       └── widgets/
│           ├── product_widget.py, entry_widget.py
│           ├── out_widget.py, sell_widget.py
│           ├── report_widget.py, user_widget.py
├── tests/                         # Pruebas unitarias
├── run.sh                         # Script de inicio (Linux)
├── run.bat                        # Script de inicio (Windows cmd)
├── run.ps1                        # Script de inicio (Windows PowerShell)
├── requirements.txt
└── .env.example                   # Plantilla de configuración
```

---

## 13. Pruebas

Framework: **pytest**.

Archivos de prueba en `tests/`:
- `test_models.py` — Pruebas de creación y consulta de modelos.
- `test_services.py` — Pruebas de servicios (auth, productos, entradas, salidas, ventas, reportes).
- `conftest.py` — Fixtures de base de datos en memoria (SQLite) para pruebas.

Ejecución:
```bash
# Linux
PYTHONPATH=. python -m pytest tests/ -v

# Windows cmd
set PYTHONPATH=%cd% && python -m pytest tests/ -v

# Windows PowerShell
$env:PYTHONPATH = Get-Location; python -m pytest tests/ -v
```
