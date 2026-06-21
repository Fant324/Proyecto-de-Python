#Requires -Version 5.1
<#
.SYNOPSIS
    Limpia todos los datos de la base de datos.
.DESCRIPTION
    Lee las credenciales de .env y ejecuta sql/clean.sql contra PostgreSQL.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$EnvFile = Join-Path $ScriptDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "ERROR: Archivo .env no encontrado" -ForegroundColor Red
    Write-Host "Copia .env.example a .env y configura los datos de PostgreSQL"
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Parsear .env
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.+)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

$env:PGPASSWORD = $env:DB_PASSWORD

& psql -h $env:DB_HOST -p $env:DB_PORT -U $env:DB_USER -d $env:DB_NAME -f (Join-Path $ScriptDir "sql\clean.sql")

Remove-Item env:PGPASSWORD

Write-Host "Base de datos limpiada correctamente" -ForegroundColor Green
Read-Host "Presiona Enter para salir"
