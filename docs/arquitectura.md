# Arquitectura del Proyecto

## 1. Introducción
Aplicación de escritorio desarrollada en Python, utilizando **PyQt6** para la interfaz gráfica, **SQLAlchemy** como ORM y **PostgreSQL** como motor de base de datos.
La arquitectura está diseñada para ser **modular, escalable y mantenible**, siguiendo buenas prácticas de separación por capas.

---

## 2. Estructura del Proyecto

```
Proyecto-de-Python/
├── sql/
│   ├── tables.sql                  # Creación de tablas, enums e índices
│   ├── views.sql                   # Vistas del sistema
│   ├── triggers.sql                # Funciones y disparadores (integridad)
│   ├── clean.sql                   # Limpieza de datos
│   └── seed.sql                    # Datos de prueba
├── src/
│   ├── main.py                     # Punto de entrada
│   ├── seed.py                     # Ejecuta SQL en orden + datos de prueba
│   ├── database/                   # Conexión y sesión SQLAlchemy
│   ├── models/                     # Modelos ORM (+ vistas como modelos)
│   ├── services/                   # Lógica de negocio
│   └── ui/                         # Interfaces (login, main, title bar, widgets)
├── docs/                           # Documentación
├── tests/                          # Pruebas unitarias (pytest)
├── alembic/                        # Migraciones
├── clean.sh / clean.bat / clean.ps1 # Scripts de limpieza de BD
├── run.sh / run.bat / run.ps1      # Scripts de inicio
├── requirements.txt
└── .env.example                    # Configuración de base de datos
```

---

## 3. Descripción de Módulos

### **src/ui/**
Contiene todas las interfaces gráficas creadas con **PyQt6**.
- `login_window.py` — inicio de sesión
- `main_window.py` — ventana principal con menú lateral y stacked widget
- `title_bar.py` — barra de título personalizada (frameless)
- `base_dialog.py` — diálogo base reutilizable
- `widgets/` — pantallas individuales (productos, entradas, salidas, ventas, reportes, usuarios)

### **src/models/**
Modelos ORM definidos con **SQLAlchemy** e **imports de tablas existentes** para vistas.
- Modelos de tablas: `User`, `Product`, `Entry`, `Out`, `Sell`, `ProdSell`, `ProductAudit`
- Modelos de vistas: `VStockProfit`, `VSalesSummary`, `VStockMovement`

### **src/services/**
Contiene la lógica de negocio. Los servicios actúan como intermediarios entre la UI y los modelos.
- `auth_service` — autenticación y verificación de roles
- `user_service` — CRUD de usuarios
- `product_service` — CRUD de productos
- `stock_service` — control de stock con bloqueo pesimista
- `entry_service` — registro de entradas
- `out_service` — registro de salidas
- `sell_service` — ventas multiproducto
- `report_service` — reportes y analítica

### **src/database/**
- Configuración de conexión a PostgreSQL
- Motor y fábrica de sesiones SQLAlchemy
- Base declarativa

### **sql/**
Scripts SQL organizados por responsabilidad:
- `tables.sql` — definición de tablas, tipos ENUM e índices
- `views.sql` — vistas materializadas para consultas frecuentes
- `triggers.sql` — funciones y disparadores (updated_at automático, auditoría de precios, validación precio>=costo)
- `clean.sql` — truncado seguro de todas las tablas con reinicio de secuencias
- `seed.sql` — datos de prueba (admin, 15 productos, movimientos y ventas)

### **tests/**
Pruebas automatizadas con **pytest** sobre una base PostgreSQL real.

### **alembic/**
Migraciones versionadas de la base de datos.

---

## 4. Arquitectura por Capas

### Capa de UI
Gestiona la interacción con el usuario. No contiene lógica de negocio.
El menú lateral se adapta según el rol del usuario:
- **admin**: todas las opciones
- **almacen**: productos, entradas, salidas
- **vendedor**: productos (solo lectura), ventas

### Capa de Servicios
Procesa reglas, validaciones y operaciones complejas. Cada servicio llama a `require_role()` para control de acceso.

### Capa de Modelos
Define entidades, relaciones ORM y modelos de vista (solo lectura).

### Capa de Base de Datos
Gestiona persistencia, sesiones, migraciones y ejecución de scripts SQL.

---

## 5. Flujo de Datos

1. El usuario interactúa con la **UI**.
2. La UI llama a un método de la capa **Services**.
3. El servicio valida permisos con `require_role()` y procesa los datos.
4. El servicio utiliza los **Models** para interactuar con la base de datos.
5. **Triggers** de PostgreSQL ejecutan reglas de integridad adicionales (updated_at automático, auditoría de precios, validación precio>=costo).
6. La respuesta vuelve hacia la UI para ser mostrada.

---

## 6. Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| Interfaz gráfica | PyQt6 |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Conexión BD | psycopg2-binary |
| Hashing | bcrypt |
| Migraciones | Alembic |
| Pruebas | pytest |
| Estilos | QSS |

---

## 7. Decisiones de Diseño

- **SQLAlchemy** para desacoplar la lógica del motor SQL.
- **PyQt6** por su robustez y soporte multiplataforma.
- **Arquitectura modular** que permite escalar sin romper componentes existentes.
- **`.env`** para separar configuración sensible del código.
- **Migraciones con Alembic** para mantener la base de datos versionada.
- **Triggers en PostgreSQL** para reglas de integridad a nivel BD (updated_at automático, validación precio>=costo, auditoría de cambios de precio).
- **Roles** definidos como ENUM de PostgreSQL y reflejados en SQLAlchemy.
- **Menú dinámico** que muestra/oculta opciones según el rol del usuario autenticado.

---

## 8. Cómo Extender la Arquitectura

### Añadir un nuevo modelo
1. Crear archivo en `src/models/`.
2. Agregar la tabla o vista en el SQL correspondiente (`tables.sql` o `views.sql`).
3. Registrar en `src/models/__init__.py`.
4. Crear migración Alembic.

### Añadir una nueva ventana
1. Crear widget en `src/ui/widgets/`.
2. Agregar botón en el menú de `main_window.py` con su verificación de rol.

### Añadir un nuevo servicio
1. Crear archivo en `src/services/`.
2. Implementar lógica de negocio con validación de roles vía `require_role()`.

### Añadir pruebas
1. Crear archivos en `tests/` usando pytest.

---

## 9. Conclusión
Esta arquitectura permite mantener un proyecto limpio, organizado y fácil de extender. Cada capa cumple un rol específico, lo que facilita el mantenimiento y la escalabilidad del sistema.
