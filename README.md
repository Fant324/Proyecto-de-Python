# Proyecto-de-Python

--------
# Proceso de intalación de requerimientos.

Se debe instalar pip

1. Crear un entorno virtual de la siguiente manera

> En windows:
```bash
python -m venv venv
```
Lo activas de la siguiente manera:

```bash
venv\Scripts\activate
```
Para saber si funciona se debe en terminal algo como:
```bash
(venv) C:\Users\user>
```

Para desactivarlo solo tienes que escribir 'deactivate'


> En linux:
```bash
python3 -m venv venv
```
Lo activas de la siguiente manera:

```bash
source venv/bin/activate
```
Para saber si funciona se debe en terminal algo como:
```bash
(venv) luis@pc:~$
```

En linux si esta activo se ejecuta

```bash
which python
```
Y debe apuntar a la carpeta del proyecto

Para desactivarlo solo tienes que escribir 'deactivate'

2. Ejecutar el comando para que pip instale las dependencias necesarias 

```bash
pip install -r requirements.txt
```
Se puede verificar con 'pip list' a ver si se instalaron bien


# Configuración del .env.example
```codigo
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nombre_de_tu_base
DB_USER=usuario
DB_PASSWORD=contraseña

# Configuración de la aplicación
APP_ENV=development
APP_DEBUG=True

# Configuración opcional (si usas logs)
LOG_LEVEL=INFO
```



