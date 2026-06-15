@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist "venv\.deps_installed" (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if !errorlevel! equ 0 (
        copy nul > "venv\.deps_installed"
    ) else (
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo Creando .env desde .env.example...
    copy .env.example .env
    echo ^¡EDITA .env CON TUS DATOS DE POSTGRESQL ANTES DE CONTINUAR!
    pause
    exit /b 1
)

set PYTHONPATH=%~dp0
python src\seed.py
python src\main.py

pause
