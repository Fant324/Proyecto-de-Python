# 📘 Sistema de Gestión de Inventario — Proyecto Académico  
Aplicación de escritorio multiplataforma (Windows/Linux) desarrollada en **Python**, utilizando **PyQt6** para la interfaz gráfica, **SQLAlchemy** como ORM y **PostgreSQL** como base de datos inicial (con futura migración a MySQL).

Su objetivo es gestionar inventario, salidas de productos, ventas y usuarios autorizados mediante login.

---

## 🛠️ Herramientas y Librerías Utilizadas

A continuación se describen las tecnologías principales, su propósito y cómo instalarlas en Windows y Linux.

---

## 🐍 Python 3.10+  
**Qué es:**  
Lenguaje de programación principal del proyecto.

**Para qué se usa:**  
- Lógica de negocio (inventario, ventas, usuarios).  
- Conexión con la base de datos.  
- Construcción de la interfaz de escritorio con PyQt6.

**Instalación:**

### Windows  
1. Descargar desde [https://www.python.org](https://www.python.org)  
2. Instalar marcando **"Add Python to PATH"**  
3. Verificar:  
   ```bash
   python --version
   ```

### Linux (Debian/Ubuntu)  
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## 🎨 PyQt6  
**Qué es:**  
Framework para crear interfaces gráficas modernas en Python.

**Para qué se usa:**  
- Ventanas, formularios, tablas, botones.  
- Interfaz completa de la aplicación.  
- Uso opcional de Qt Designer para diseñar pantallas visualmente.

**Instalación (Windows y Linux):**
```bash
pip install PyQt6
```

---

## 🗄️ PostgreSQL  
**Qué es:**  
Sistema de gestión de bases de datos relacional, robusto y profesional.

**Para qué se usa:**  
- Almacenar productos, usuarios, ventas y salidas.  
- Será la base inicial antes de migrar a MySQL.

**Instalación:**

### Windows  
Descargar instalador oficial:  
[https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

### Linux (Debian/Ubuntu)  
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Verificar servicio:**  
```bash
sudo systemctl status postgresql
```

---

## 🔄 SQLAlchemy  
**Qué es:**  
ORM (Object Relational Mapper) que permite trabajar con la base de datos usando clases en lugar de SQL directo.

**Para qué se usa:**  
- Modelos de Producto, Usuario, Venta, Salida.  
- Migración futura a MySQL sin reescribir todo el backend.  
- Abstracción limpia y profesional.

**Instalación:**  
```bash
pip install SQLAlchemy
```

---

## 🧱 psycopg2-binary  
**Qué es:**  
Driver que permite a Python conectarse a PostgreSQL.

**Instalación:**  
```bash
pip install psycopg2-binary
```

---

## 🔐 python-dotenv  
**Qué es:**  
Permite guardar credenciales (usuario, contraseña, host de la base de datos) en un archivo `.env`.

**Para qué se usa:**  
- Mantener la configuración separada del código.  
- Facilitar la migración a MySQL en el futuro.

**Instalación:**  
```bash
pip install python-dotenv
```

---

## 🧪 pytest (opcional pero recomendado)  
**Qué es:**  
Framework para pruebas automatizadas.

**Para qué se usa:**  
- Validar que el inventario, ventas y login funcionen correctamente.

**Instalación:**  
```bash
pip install pytest
```

---

## 📦 Alembic (opcional para versiones posteriores)  
**Qué es:**  
Sistema de migraciones para SQLAlchemy.

**Para qué se usa:**  
- Evolución de la base de datos sin perder datos.  
- Facilitar la migración PostgreSQL → MySQL.

**Instalación:**  
```bash
pip install alembic
```

---

# 📋 Resumen de Instalación Rápida

```bash
pip install PyQt6 SQLAlchemy psycopg2-binary python-dotenv pytest alembic
```

## Ejecución del proyecto

| Sistema | Comando |
|---------|---------|
| Linux   | `./run.sh` |
| Windows cmd | `run.bat` |
| Windows PowerShell | `.\run.ps1` |

Ver [guía de instalación completa](instalacion.md) para más detalles.

