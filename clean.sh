#!/usr/bin/env bash
# ============================================
# Limpia todos los datos de la base de datos
# ============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cargar variables de entorno
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo "ERROR: Archivo .env no encontrado"
    echo "Copia .env.example a .env y configura los datos de PostgreSQL"
    exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f sql/clean.sql

unset PGPASSWORD

echo "Base de datos limpiada correctamente"
