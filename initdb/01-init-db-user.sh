#!/bin/sh
set -e

# 1. Crear el usuario de la aplicación usando el usuario admin
psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname "$POSTGRES_DB" \
     -v app_user="$APP_USER" \
     -v app_password="$APP_PASSWORD" \
     -v db_name="$POSTGRES_DB" \
     <<-EOSQL
    CREATE USER :"app_user" WITH PASSWORD :'app_password';
    GRANT ALL PRIVILEGES ON DATABASE :"db_name" TO :"app_user";
    GRANT USAGE ON SCHEMA public TO :"app_user";
    GRANT CREATE ON SCHEMA public TO :"app_user";
EOSQL

# 2. Ejecutar el script de creación de tablas como el usuario de la aplicación
psql -v ON_ERROR_STOP=1 \
     --username "$APP_USER" \
     --dbname "$POSTGRES_DB" \
     -v app_user="$APP_USER" \
     -v db_name="$POSTGRES_DB" \
     -f /docker-entrypoint-initdb.d/sql/02-create-tables.sql