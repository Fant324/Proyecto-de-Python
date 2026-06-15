# Sistema de Gestión de Inventario

## 1. Diseño y Tecnologías

### Arquitectura
Aplicación de escritorio en **3 capas**: Presentación (PyQt6), Servicios (lógica de negocio) y Acceso a Datos (SQLAlchemy + PostgreSQL).

### Tecnologías
| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| Interfaz gráfica | PyQt6 |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Conexión BD | psycopg2-binary |
| Hashing | bcrypt |
| Migraciones | Alembic |
| Estilos | QSS (hojas de estilo Qt) |

### Estructura del proyecto
```
├── src/
│   ├── main.py              # Punto de entrada
│   ├── seed.py              # Carga datos iniciales (ejecuta sql/schema.sql + sql/seed.sql)
│   ├── database/            # Conexión y sesión SQLAlchemy
│   ├── models/              # Modelos ORM (User, Product, Entry, Out, Sell, ProdSell)
│   ├── services/            # Lógica de negocio (auth, cruds, stock, reportes)
│   └── ui/                  # Interfaces (login, main, title bar, widgets)
│       └── widgets/         # Pantallas: productos, entradas, salidas, ventas, reportes, usuarios
├── sql/
│   ├── schema.sql           # CREATE TABLE de todas las tablas
│   └── seed.sql             # Datos de prueba (admin + 15 productos + movimientos)
├── docs/                    # Documentación
├── alembic/                 # Migraciones
├── requirements.txt
├── run.sh / run.bat         # Scripts de inicio
└── .env.example             # Configuración de BD
```

---

## 2. Manual de Usuario

### 2.1 Requisitos previos
- Python 3.12+
- PostgreSQL con base de datos `stockmanager` creada
- Archivo `.env` configurado (ver `.env.example`)

### 2.2 Instalación rápida

**Linux:**
```bash
./run.sh
```

**Windows:**
```batch
run.bat
```

**Manual:**
```bash
python -m venv venv
source venv/bin/activate      # Linux
venv\Scripts\activate.bat     # Windows
pip install -r requirements.txt
cp .env.example .env          # Editar datos de PostgreSQL
python src/seed.py            # Crea tablas + usuario admin/admin + datos de prueba
python src/main.py
```

**Alternativa con psql (sin seed.py):**
```bash
psql -U postgres -d stockmanager -f sql/schema.sql
psql -U postgres -d stockmanager -f sql/seed.sql
python src/main.py
```

### 2.3 Inicio de sesión
- **Usuario:** `admin`
- **Contraseña:** `admin`
- Rol: administrador (acceso completo)

### 2.4 Pantalla principal
Menú lateral izquierdo con las siguientes opciones (según el rol):

| Botón | Descripción |
|---|---|
| Productos | CRUD de productos del catálogo |
| Entradas | Registrar ingresos de stock |
| Salidas | Registrar egresos de stock |
| Ventas | Registrar ventas (uno o varios productos) |
| Reportes | Reportes por rango de fechas + exportación CSV |
| Usuarios | Gestión de usuarios del sistema (solo admin) |

### 2.5 Pruebas sugeridas

#### a) Productos
1. Ir a **Productos** → ver listado con 15 productos precargados.
2. Click **Nuevo Producto** → crear producto "Teclado USB" (costo 10, precio 25).
3. Seleccionar un producto → **Editar** → cambiar precio.
4. Seleccionar un producto → **Eliminar**.

#### b) Entradas
1. Ir a **Entradas** → **Nueva Entrada**.
2. ID Producto: `2` (Mouse Logitech), Cantidad: `20`, Fecha: hoy.
3. Verificar que el stock del producto aumentó.

#### c) Salidas
1. Ir a **Salidas** → **Nueva Salida**.
2. ID Producto: `3` (Teclado), Cantidad: `2`, Destino: "Devolución", Fecha: hoy.
3. Verificar que el stock disminuyó.

#### d) Ventas
1. Ir a **Ventas** → **Nueva Venta**.
2. Agregar productos:
   - ID: `1` (Laptop), Cant: `1`
   - ID: `2` (Mouse), Cant: `3`
3. Si agregas el mismo producto dos veces, la cantidad se suma automáticamente (ej: agrega ID `2` otra vez con Cant `2` → queda Mouse con Cant `5`).
4. Click **Guardar Venta**.
5. Verificar que la venta aparece en la tabla y el stock se actualizó.
6. Desde **Reportes** → pestaña **Ventas** → click **Actualizar** para verla reflejada.

#### e) Reportes
1. Ir a **Reportes**.
2. Fechas: seleccionar un rango (ej: desde 2026-05-01 hasta hoy).
3. Click **Filtrar**.
4. Navegar por las pestañas en este orden: **Productos**, **Entradas**, **Salidas**, **Ventas**, **Ventas por Producto**, **Resumen**.
   - Las pestañas **Productos**, **Ventas por Producto** y **Resumen** NO muestran filtro de fecha (son datos globales).
   - Las pestañas **Entradas**, **Salidas** y **Ventas** SÍ muestran filtro de fecha.
5. Marcar **Convertir a CUP** → aparece columna extra con valores convertidos en Productos, Ventas y Resumen.
6. Click **Actualizar** para refrescar datos tras cambios en otras pantallas.
7. Click **Exportar CSV** para descargar la pestaña activa.

#### f) Usuarios (solo admin)
1. Ir a **Usuarios** → **Nuevo Usuario**.
2. Crear usuario `vendedor1` con rol `vendedor`.
3. Cerrar sesión e iniciar como `vendedor1` (contraseña configurada).
4. Verificar que los botones Reportes y Usuarios no aparecen.

#### g) Funcionalidades adicionales
- **F11** para alternar pantalla completa.
- Botón **Actualizar** en cada pantalla para refrescar datos.
- Tasa de cambio USD→CUP configurable en Reportes (botones `+`/`-`).
- La aplicación inicia en pantalla completa con barra de título personalizada (minimizar y cerrar).

### 2.6 Roles

| Rol | Acceso |
|---|---|
| admin | Todas las funciones: productos, entradas, salidas, ventas, reportes, usuarios |
| vendedor | Solo productos, entradas, salidas, ventas (sin reportes ni usuarios) |

### 2.7 Notas importantes
- La aplicación usa **PostgreSQL** como base de datos. Asegúrese de tener el servidor corriendo.
- Los errores se muestran en español con mensajes descriptivos.
- La tasa de conversión se guarda automáticamente al cambiar el valor.
- No se puede eliminar el último usuario administrador ni eliminarse a sí mismo.
