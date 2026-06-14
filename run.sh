#!/usr/bin/env bash
set -e

# Activar entorno virtual
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -f "venv/.deps_installed" ]; then
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Archivo .env
if [ ! -f ".env" ]; then
    echo "Creando .env desde .env.example..."
    cp .env.example .env
    echo "¡EDITA .env CON TUS DATOS DE POSTGRESQL ANTES DE CONTINUAR!"
    exit 1
fi

# Semilla: usuario admin por defecto
PYTHONPATH="$SCRIPT_DIR" python src/seed.py

# Iniciar aplicación
PYTHONPATH="$SCRIPT_DIR" python src/main.py
