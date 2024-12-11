# Data Processing Guide [WIP]

This guide explains how to fetch, process, and store geospatial data from Overture Maps into PostGIS. This isn't an automated pipeline just yet, but it's a good starting point for anyone looking to get started with recreating the dataset, or adapting the code for other geographic regions.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Required Python packages:
  ```bash
  pip install geopandas sqlalchemy psycopg2-binary
  ```

## Data Pipeline

### 1. Fetch Overture Maps Data

Download data for your bounding box using the Overture Maps API:

```bash
sh data/download.sh
```

(Check out the shell script for what's going on — easy to modify for different bounding boxes, limit the layers downloaded, etc.)

### 2. Load into GeoPandas

Process the downloaded data using the provided Jupyter notebook:

```python
# data.ipynb
import geopandas as gpd
import os

# Loop through files in data, create a dataframe for each
dataframes = []
for file in os.listdir("data"):
    if file.endswith(".json"):
        print(f"Processing {file}")
        df = gpd.read_file(f"data/{file}")
        if df.empty:
            print(f"Skipping {file} because it's empty")
            continue
        df_name = f"df_{file.split('-')[1].split('.')[0]}"
        globals()[df_name] = df
        dataframes.append(df_name)
```

### 3. Store in PostGIS

#### 3.1 Start PostGIS Container

```bash
docker compose up -d postgis
```

#### 3.2 Load Data into PostGIS

```python
from sqlalchemy import create_engine

# Create database connection
engine = create_engine('postgresql://mapper:password@localhost:5433/overture')

# Store dataframes in PostGIS
for df_name in dataframes:
    df = globals()[df_name]
    table_name = f"omf_{df_name.replace('df_', '')}"
    df.to_postgis(table_name, engine, if_exists="replace")
```

### 4. Backup and Restore

#### Creating a Database Dump

To create a backup of your PostGIS database:

```bash
# From host machine
docker exec -t nl-geospatial-interface-postgis-1 pg_dump -U mapper -Fc overture > postgis/data/omf_islington.dump
```

Or using pg_dump directly if PostgreSQL is installed locally:
```bash
pg_dump -h localhost -p 5433 -U mapper -Fc overture > postgis/data/omf_islington.dump
```

#### Restoring from Dump

The database will automatically restore from `postgis/data/omf_islington.dump` when the container starts, thanks to the initialization script in `postgis/init-postgis.sh`.

To manually restore:
```bash
# From host machine
docker exec -i nl-geospatial-interface-postgis-1 pg_restore -U mapper -d overture < postgis/data/omf_islington.dump
```

Or using pg_restore directly:
```bash
pg_restore -h localhost -p 5433 -U mapper -d overture postgis/data/omf_islington.dump
```

## Database Connection Details

- Host: `localhost`
- Port: `5433`
- Database: `overture`
- Username: `mapper`
- Password: `password`

## Project Structure

```
.
├── data/
│   ├── download.sh
│   └── islington-*.json
├── postgis/
│   ├── Dockerfile
│   ├── init-postgis.sh
│   ├── init.sql
│   └── data/
│       └── omf_islington.dump
├── compose.yaml
└── data.ipynb
```

## Notes

- The PostGIS container is configured to use port 5433 to avoid conflicts with any local PostgreSQL installation
- Data is persisted in a Docker volume named `pg_omf_data`
- The dump file is stored in `postgis/data/` which is mounted into the container at `/backup/`
```