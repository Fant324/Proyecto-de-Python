# Arquitectura del Proyecto

## 1. Introducción
Este proyecto implementa una aplicación de escritorio desarrollada en Python, utilizando **[PyQt6](ca://s?q=PyQt6)** para la interfaz gráfica, **[SQLAlchemy](ca://s?q=SQLAlchemy)** como ORM y **PostgreSQL** como motor de base de datos.  
La arquitectura está diseñada para ser **modular, escalable y mantenible**, siguiendo buenas prácticas de separación por capas.

---

## 2. Estructura del Proyecto

```
Proyecto-de-Python/
│
├── src/
│   ├── app/
│   │   ├── ui/
│   │   ├── models/
│   │   ├── services/
│   │   ├── database/
│   │   └── utils/
│   └── main.py
│
├── docs/
│   └── arquitectura.md
│
├── tests/
│   └── test_app.py
│
├── .gitignore
├── .env.example
├── requirements.txt
└── README.md
```
---

## 3. Descripción de Módulos

### **src/app/ui/**
Contiene todas las interfaces gráficas creadas con **[PyQt6](ca://s?q=PyQt6)**.  
Aquí se definen ventanas, diálogos, formularios y controladores de eventos.

### **src/app/models/**
Incluye los modelos ORM definidos con **[SQLAlchemy](ca://s?q=SQLAlchemy)**.  
Cada archivo representa una tabla de la base de datos.

### **src/app/services/**
Contiene la lógica de negocio.  
Los servicios actúan como intermediarios entre la UI y los modelos.

### **src/app/database/**
Incluye:
- Configuración de conexión  
- Creación del motor  
- Sesiones  
- Migraciones con **[Alembic](ca://s?q=Alembic)**  

### **src/app/utils/**
Funciones auxiliares reutilizables: validaciones, formateos, helpers, etc.

### **tests/**
Pruebas automatizadas utilizando **[pytest](ca://s?q=pytest)**.

---

## 4. Arquitectura por Capas

La aplicación sigue una arquitectura en capas:

### **Capa de UI**
Gestiona la interacción con el usuario.  
No contiene lógica de negocio.

### **Capa de Servicios**
Procesa reglas, validaciones y operaciones complejas.

### **Capa de Modelos**
Define entidades y relaciones ORM.

### **Capa de Base de Datos**
Gestiona persistencia, sesiones y migraciones.

---

## 5. Flujo de Datos

1. El usuario interactúa con la **UI**.  
2. La UI llama a un método de la capa **Services**.  
3. El servicio valida y procesa los datos.  
4. El servicio utiliza los **Models** para interactuar con la base de datos.  
5. La respuesta vuelve hacia la UI para ser mostrada.

---

## 6. Tecnologías Utilizadas

- **[PyQt6](ca://s?q=PyQt6)** — Interfaz gráfica  
- **[SQLAlchemy](ca://s?q=SQLAlchemy)** — ORM  
- **[psycopg2-binary](ca://s?q=psycopg2_binary)** — Driver PostgreSQL  
- **[python-dotenv](ca://s?q=python_dotenv)** — Variables de entorno  
- **[Alembic](ca://s?q=Alembic)** — Migraciones  
- **[pytest](ca://s?q=pytest)** — Pruebas automatizadas  

---

## 7. Decisiones de Diseño

- Se utiliza **SQLAlchemy** para desacoplar la lógica del motor SQL.  
- Se elige **PyQt6** por su robustez y soporte multiplataforma.  
- La arquitectura modular permite escalar el proyecto sin romper componentes existentes.  
- Se usa `.env` para separar configuración sensible del código.  
- Se implementan migraciones con Alembic para mantener la base de datos versionada.

---

## 8. Cómo Extender la Arquitectura

### Añadir un nuevo modelo
Crear un archivo en `src/app/models/` y registrar la tabla.

### Añadir una nueva ventana PyQt6
Crear un archivo en `src/app/ui/` y conectar eventos a servicios.

### Añadir un nuevo servicio
Crear un archivo en `src/app/services/` y exponer métodos a la UI.

### Añadir pruebas
Crear archivos en `tests/` usando pytest.

---

## 9. Conclusión
Esta arquitectura permite mantener un proyecto limpio, organizado y fácil de extender.  
Cada capa cumple un rol específico, lo que facilita el mantenimiento y la escalabilidad del sistema.

