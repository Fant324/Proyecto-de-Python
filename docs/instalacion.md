# Guia de Instalacion

## Requisitos previos

- **Python 3.10 o superior**
- **PostgreSQL 14 o superior**
- **pip** (incluido con Python)

---

## Indice

1. [Windows - cmd](#windows---cmd)
2. [Windows - PowerShell](#windows---powershell)
3. [Linux - Debian / Ubuntu](#linux---debian--ubuntu)
4. [Linux - Fedora / RHEL](#linux---fedora--rhel)
5. [Linux - Arch Linux](#linux---arch-linux)
6. [Linux - openSUSE](#linux---opensuse)
7. [Configuracion post-instalacion](#configuracion-post-instalacion)

---

## Windows - cmd

### 1. Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalacion **marca la opcion "Add Python to PATH"**
3. Verifica la instalacion:
   ```cmd
   python --version
   pip --version
   ```

### 2. Instalar PostgreSQL

1. Descarga el instalador desde [postgresql.org](https://www.postgresql.org/download/windows/)
2. Durante la instalacion, anota el puerto (por defecto `5432`) y la contrasena del usuario `postgres`
3. Abre **SQL Shell (psql)** y crea la base de datos:
   ```sql
   CREATE DATABASE stockmanager;
   ```

### 3. Clonar y configurar el proyecto

```cmd
cd C:\ruta\al\Proyecto-de-Python
```

### 4. Ejecutar con el script automatico

```cmd
run.bat
```

Esto creara el entorno virtual, instalara las dependencias y te guiara para crear el archivo `.env`.

### 5. Ejecucion paso a paso (alternativa)

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
REM Edita .env con tus datos de PostgreSQL
set PYTHONPATH=%cd%
python src\seed.py
python src\main.py
```

---

## Windows - PowerShell

### 1. Instalar Python

1. Descarga Python desde [python.org](https://www.python.org/downloads/)
2. Durante la instalacion **marca la opcion "Add Python to PATH"**
3. Verifica la instalacion:
   ```powershell
   python --version
   pip --version
   ```

### 2. Instalar PostgreSQL

1. Descarga el instalador desde [postgresql.org](https://www.postgresql.org/download/windows/)
2. Durante la instalacion, anota el puerto (por defecto `5432`) y la contrasena del usuario `postgres`
3. Abre **SQL Shell (psql)** y crea la base de datos:
   ```sql
   CREATE DATABASE stockmanager;
   ```

### 3. Habilitar ejecucion de scripts de PowerShell (si es necesario)

Si es la primera vez que ejecutas scripts.ps1, abre PowerShell como Administrador y ejecuta:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 4. Clonar y configurar el proyecto

```powershell
cd C:\ruta\al\Proyecto-de-Python
```

### 5. Ejecutar con el script automatico

```powershell
.\run.ps1
```

### 6. Ejecucion paso a paso (alternativa)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edita .env con tus datos de PostgreSQL
$env:PYTHONPATH = Get-Location
python src/seed.py
python src/main.py
```

---

## Linux - Debian / Ubuntu

### 1. Instalar Python y dependencias

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib -y
```

### 2. Iniciar PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Crear la base de datos

```bash
sudo -u postgres createdb stockmanager
```

### 4. Configurar contrasena para el usuario postgres

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'tu_contraseña';"
```

### 5. Clonar y ejecutar

```bash
cd /ruta/al/Proyecto-de-Python
./run.sh
```

### 6. Ejecucion paso a paso (alternativa)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus datos de PostgreSQL
PYTHONPATH=. python src/seed.py
PYTHONPATH=. python src/main.py
```

---

## Linux - Fedora / RHEL

### 1. Instalar Python y dependencias

```bash
sudo dnf install python3 python3-pip python3-virtualenv postgresql postgresql-server -y
```

### 2. Inicializar e iniciar PostgreSQL

```bash
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Crear la base de datos

```bash
sudo -u postgres createdb stockmanager
```

### 4. Configurar contrasena para el usuario postgres

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'tu_contraseña';"
```

### 5. Clonar y ejecutar

```bash
cd /ruta/al/Proyecto-de-Python
./run.sh
```

### 6. Ejecucion paso a paso (alternativa)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus datos de PostgreSQL
PYTHONPATH=. python src/seed.py
PYTHONPATH=. python src/main.py
```

---

## Linux - Arch Linux

### 1. Instalar Python y dependencias

```bash
sudo pacman -S python python-pip python-virtualenv postgresql --noconfirm
```

### 2. Inicializar e iniciar PostgreSQL

```bash
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Crear la base de datos

```bash
sudo -u postgres createdb stockmanager
```

### 4. Configurar contrasena para el usuario postgres

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'tu_contraseña';"
```

### 5. Clonar y ejecutar

```bash
cd /ruta/al/Proyecto-de-Python
./run.sh
```

### 6. Ejecucion paso a paso (alternativa)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus datos de PostgreSQL
PYTHONPATH=. python src/seed.py
PYTHONPATH=. python src/main.py
```

---

## Linux - openSUSE

### 1. Instalar Python y dependencias

```bash
sudo zypper install python3 python3-pip python3-virtualenv postgresql postgresql-server
```

### 2. Inicializar e iniciar PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Crear la base de datos

```bash
sudo -u postgres createdb stockmanager
```

### 4. Configurar contrasena para el usuario postgres

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'tu_contraseña';"
```

### 5. Clonar y ejecutar

```bash
cd /ruta/al/Proyecto-de-Python
./run.sh
```

### 6. Ejecucion paso a paso (alternativa)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus datos de PostgreSQL
PYTHONPATH=. python src/seed.py
PYTHONPATH=. python src/main.py
```

---

## Configuracion post-instalacion

### Archivo .env

Edita el archivo `.env` con tus credenciales de PostgreSQL:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stockmanager
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

### Usuario por defecto

Una vez que ejecutes `seed.py`, se crea automaticamente:

| Usuario | Contrasena | Rol    |
|---------|-----------|--------|
| admin   | admin     | Admin  |

### Probar la instalacion

Para verificar que todo funciona correctamente:

```bash
# Linux
PYTHONPATH=. python -m pytest tests/ -v

# Windows cmd
set PYTHONPATH=%cd% && python -m pytest tests/ -v

# Windows PowerShell
$env:PYTHONPATH = Get-Location; python -m pytest tests/ -v
```

### Migraciones con Alembic

```bash
# Linux
PYTHONPATH=. alembic upgrade head

# Windows cmd
set PYTHONPATH=%cd% && alembic upgrade head

# Windows PowerShell
$env:PYTHONPATH = Get-Location; alembic upgrade head
```
