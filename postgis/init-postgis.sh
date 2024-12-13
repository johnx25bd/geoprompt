#!/bin/bash
set -e

# Enable PostGIS extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS postgis;
    CREATE EXTENSION IF NOT EXISTS postgis_topology;
EOSQL

# Restore from dump if it exists
if [ -f "/backup/omf_islington.dump" ]; then
    echo "Found dump file, attempting restore..."
    pg_restore -v -U "$POSTGRES_USER" -d "$POSTGRES_DB" /backup/omf_islington.dump
    
    if [ $? -eq 0 ]; then
        echo "Restore completed successfully"
    else
        echo "Restore failed"
        exit 1
    fi
else
    echo "No dump file found at /backup/omf_islington.dump"
    exit 1
fi