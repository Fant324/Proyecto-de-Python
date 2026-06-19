# Sistema de Gestión de Inventario

Aplicación de escritorio para gestión de inventario con roles (admin/vendedor), built con PyQt6 + SQLAlchemy + PostgreSQL.

## Requisitos

- Python 3.10+
- PostgreSQL 14+
- pip

## Instalación

Consulta la **[guía de instalación completa](docs/instalacion.md)** para instrucciones detalladas según tu sistema operativo:

| Sistema | Script automatizado |
|---------|-------------------|
| Linux   | `./run.sh`        |
| Windows (cmd) | `run.bat`    |
| Windows (PowerShell) | `.\run.ps1` |

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

Puedes crear más usuarios desde el panel de administración.

## Recrear la base de datos desde cero

```bash
# 1. Eliminar y crear la base de datos
dropdb stockmanager
createdb stockmanager

# 2. Iniciar la app (crea las tablas automáticamente)
PYTHONPATH=. python src/main.py
# Presiona Ctrl+C una vez que veas "Base de datos lista"

# 3. Sembrar usuario admin y datos de prueba
PYTHONPATH=. python src/seed.py
psql -U postgres -d stockmanager -f seed_data.sql

# 4. Ejecutar normalmente
PYTHONPATH=. python src/main.py
```

O simplemente usar `run.sh` (Linux), `run.bat` (Windows cmd) o `run.ps1` (Windows PowerShell) que hacen todo automáticamente.

## Estructura del proyecto

```
src/
├── main.py                        # Punto de entrada
├── seed.py                        # Creación de usuario admin inicial
├── database/
│   ├── base.py                    # Base declarativa SQLAlchemy
│   └── session.py                 # Conexión a PostgreSQL
├── models/
│   ├── user.py                    # Usuarios con roles
│   ├── product.py                 # Productos
│   ├── entry.py                   # Entradas de stock
│   ├── out.py                     # Salidas de stock
│   ├── sell.py                    # Ventas
│   └── prod_sell.py               # Productos por venta (N:M)
├── services/
│   ├── auth_service.py            # Autenticación con bcrypt
│   ├── user_service.py            # CRUD de usuarios
│   ├── product_service.py         # CRUD de productos
│   ├── stock_service.py           # Control de stock
│   ├── entry_service.py           # Registro de entradas
│   ├── out_service.py             # Registro de salidas
│   ├── sell_service.py            # Ventas multiproducto
│   └── report_service.py          # Reportes por fecha
├── ui/
│   ├── login_window.py            # Ventana de inicio de sesión
│   ├── main_window.py             # Ventana principal con menú
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

## Roles y permisos

- **Admin**: acceso completo a todas las funciones, incluyendo gestión de usuarios
- **Vendedor**: puede gestionar productos, entradas, salidas, ventas y reportes

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
