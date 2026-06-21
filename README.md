# Sistema de Gestión de Inventario

Aplicación de escritorio para gestión de inventario con roles (admin/almacen/vendedor), construida con PyQt6 + SQLAlchemy + PostgreSQL.

## Requisitos

- Python 3.10+
- PostgreSQL 14+
- pip

## Instalación

Consulta la **[guía de instalación completa](docs/instalacion.md)** para instrucciones detalladas según tu sistema operativo:

| Sistema | Iniciar app | Limpiar BD |
|---------|------------|------------|
| Linux   | `./run.sh` | `./clean.sh` |
| Windows (cmd) | `run.bat` | `clean.bat` |
| Windows (PowerShell) | `.\run.ps1` | `.\clean.ps1` |

### Resumen rápido

**Linux:**
```bash
./run.sh
```

**Windows cmd:**
```cmd
run.bat
```

**Windows PowerShell:**
```powershell
.\run.ps1
```

## Usuarios por defecto

| Usuario | Contraseña | Rol  |
|---------|-----------|------|
| admin   | admin     | Admin|

Puedes crear más usuarios (admin, almacen, vendedor) desde el panel de administración.

## Roles y permisos

| Rol | Acceso |
|-----|--------|
| **admin** | Acceso completo: productos, entradas, salidas, ventas, reportes y usuarios |
| **almacen** | Gestión de inventario: productos, entradas y salidas |
| **vendedor** | Ventas y consulta de stock de productos (solo lectura) |

## Recrear la base de datos desde cero

```bash
# 1. Eliminar y crear la base de datos
dropdb stockmanager
createdb stockmanager

# 2. Iniciar (crea esquema + datos de prueba si no existe admin)
PYTHONPATH=. python src/main.py
```

O simplemente usar los scripts automatizados (`run.sh`, `run.bat`, `run.ps1`) que hacen todo automáticamente.
Si el admin ya existe, `seed.sql` se omite para no truncar los datos existentes.

## Limpiar datos sin borrar la base de datos

Para eliminar todos los registros y reiniciar secuencias (sin borrar las tablas):

| Sistema | Comando |
|---------|---------|
| Linux   | `./clean.sh` |
| Windows (cmd) | `clean.bat` |
| Windows (PowerShell) | `.\clean.ps1` |

Luego al iniciar la app se repoblarán los datos automáticamente (las vistas y triggers se crean al arrancar desde `main.py`).

## Estructura del proyecto

```
sql/
├── tables.sql                     # Creación de tablas, enums e índices
├── views.sql                      # Vistas del sistema
├── triggers.sql                   # Funciones y disparadores (integridad)
├── clean.sql                      # Limpieza de datos
└── seed.sql                       # Datos de prueba
src/
├── main.py                        # Punto de entrada
├── seed.py                        # Ejecuta SQL en orden + datos de prueba
├── database/
│   ├── base.py                    # Base declarativa SQLAlchemy
│   └── session.py                 # Conexión a PostgreSQL
├── models/
│   ├── user.py                    # Usuarios con roles
│   ├── product.py                 # Productos
│   ├── entry.py                   # Entradas de stock
│   ├── out.py                     # Salidas de stock
│   ├── sell.py                    # Ventas
│   ├── prod_sell.py               # Productos por venta (N:M)
│   ├── product_audit.py           # Auditoría de cambios de precio
│   ├── v_stock_profit.py          # Vista: ganancia esperada
│   ├── v_sales_summary.py         # Vista: resumen de ventas
│   └── v_stock_movements.py       # Vista: movimientos unificados
├── services/
│   ├── auth_service.py            # Autenticación con bcrypt
│   ├── user_service.py            # CRUD de usuarios
│   ├── product_service.py         # CRUD de productos
│   ├── stock_service.py           # Consulta de stock
│   ├── entry_service.py           # Entradas (lock pesimista en producto)
│   ├── out_service.py             # Salidas (valida stock, lock directo)
│   ├── sell_service.py            # Ventas multiproducto (lock por producto)
│   └── report_service.py          # Reportes por fecha
├── ui/
│   ├── login_window.py            # Ventana de inicio de sesión
│   ├── main_window.py             # Ventana principal con menú
│   ├── title_bar.py               # Barra de título personalizada
│   ├── base_dialog.py             # Diálogo base con padding
│   └── widgets/
│       ├── product_widget.py      # Gestión de productos
│       ├── entry_widget.py        # Entradas
│       ├── out_widget.py          # Salidas
│       ├── sell_widget.py         # Ventas
│       ├── report_widget.py       # Reportes con exportación CSV
│       └── user_widget.py         # Gestión de usuarios (admin)
tests/
├── test_models.py                 # Tests de modelos
└── test_services.py               # Tests de servicios
```

## Migraciones con Alembic

```bash
# Crear nueva migración
PYTHONPATH=. alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
PYTHONPATH=. alembic upgrade head
```

## Tests

```bash
PYTHONPATH=. python -m pytest tests/ -v
```

## Licencia

MIT
