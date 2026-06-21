@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist ".env" (
    echo ERROR: Archivo .env no encontrado
    echo Copia .env.example a .env y configura los datos de PostgreSQL
    pause
    exit /b 1
)

:: Leer variables del .env
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if "%%a"=="DB_HOST" set DB_HOST=%%b
    if "%%a"=="DB_PORT" set DB_PORT=%%b
    if "%%a"=="DB_NAME" set DB_NAME=%%b
    if "%%a"=="DB_USER" set DB_USER=%%b
    if "%%a"=="DB_PASSWORD" set DB_PASSWORD=%%b
)

set PGPASSWORD=%DB_PASSWORD%

psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f sql\clean.sql

set PGPASSWORD=

echo Base de datos limpiada correctamente
pause
