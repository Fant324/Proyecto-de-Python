@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ============================================
echo  Stock Manager - Sistema de Inventario
echo ============================================
echo.

if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        echo         Asegurate de tener Python 3.10+ instalado.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

if not exist "venv\.deps_installed" (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if !errorlevel! equ 0 (
        copy nul > "venv\.deps_installed"
    ) else (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    echo [INFO] Creando .env desde .env.example...
    copy .env.example .env
    echo.
    echo  ******************************************************
    echo   *  IMPORTANTE: EDITA .env CON TUS DATOS DE        *
    echo   *  POSTGRESQL ANTES DE CONTINUAR                  *
    echo   *                                                  *
    echo   *  DB_HOST=localhost                                *
    echo   *  DB_PORT=5432                                     *
    echo   *  DB_NAME=stockmanager                             *
    echo   *  DB_USER=postgres                                 *
    echo   *  DB_PASSWORD=tu_contraseña                       *
    echo   ******************************************************
    echo.
    pause
    exit /b 1
)

echo [INFO] Sembrando datos iniciales...
set PYTHONPATH=%~dp0
python src\seed.py

echo [INFO] Iniciando aplicacion...
python src\main.py

echo.
pause
