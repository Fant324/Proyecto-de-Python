#Requires -Version 5.1
<#
.SYNOPSIS
    Script de inicio para el Sistema de Gestión de Inventario (Windows PowerShell).
.DESCRIPTION
    Crea el entorno virtual, instala dependencias, configura .env y ejecuta la aplicación.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Crear entorno virtual si no existe
if (-not (Test-Path "venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
    python -m venv venv
}

# Activar entorno virtual
$ActivateScript = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"
. $ActivateScript

# Instalar dependencias
$DepsFile = Join-Path $ScriptDir "venv\.deps_installed"
if (-not (Test-Path $DepsFile)) {
    Write-Host "Instalando dependencias..." -ForegroundColor Cyan
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        New-Item -ItemType File -Path $DepsFile -Force | Out-Null
    } else {
        Write-Host "Error al instalar dependencias." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

# Archivo .env
$EnvFile = Join-Path $ScriptDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "Creando .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "`n¡EDITA .env CON TUS DATOS DE POSTGRESQL ANTES DE CONTINUAR!" -ForegroundColor Red
    Read-Host "`nPresiona Enter después de editar .env, o Ctrl+C para salir"
}

# Semilla: usuario admin por defecto
$env:PYTHONPATH = $ScriptDir
python src/seed.py

# Iniciar aplicación
Write-Host "`nIniciando aplicación..." -ForegroundColor Green
python src/main.py

Read-Host "`nPresiona Enter para salir"
