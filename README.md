# Sistema de Gestión de Inventario

Aplicación de escritorio para gestión de inventario con roles (admin/vendedor), built con PyQt6 + SQLAlchemy + PostgreSQL.

## Requisitos

- Python 3.10+
- PostgreSQL 14+
- pip

## Instalación

### 1. Clonar y entrar al proyecto

```bash
cd Proyecto-de-Python
```

### 2. Crear y activar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

Crea una base de datos en PostgreSQL:

```bash
createdb stockmanager
```

Copia y edita el archivo de entorno:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de PostgreSQL:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stockmanager
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

### 5. Inicializar la base de datos

```bash
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python src/seed.py
```

Esto crea las tablas y un usuario administrador por defecto.

## Ejecución

### Opción 1: Script automatizado

```bash
./run.sh
```

### Opción 2: Manual

```bash
source venv/bin/activate
PYTHONPATH=. python src/main.py
```

## Usuarios por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin   | admin     | Admin |

Puedes crear más usuarios desde el panel de administración.

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
