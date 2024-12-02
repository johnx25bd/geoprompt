#!/bin/bash
set -e

# Enable PostGIS extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOSQL

# Restore from dump if it exists
if [ -f "/backup/omf_islington.dump" ]; then
    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /backup/omf_islington.dump || echo "Restore failed but continuing"
fi