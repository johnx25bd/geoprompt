# PostGIS Data Preparation

This directory contains PostgreSQL dump files created from Overture Maps Foundation data. Below is the process used to prepare this data.

## Data Source

The data is sourced from the [Overture Maps Foundation](https://overturemaps.org/), which provides open map data in multiple formats. The original data was collected from the [`/data`](../../data/) directory containing Overture's raw data files, fetched via their CLI, focused on northeast London.

## Preparation Process

1. **Data Collection**
   - Raw data files were downloaded from Overture Maps Foundation
   - GeoJSON Files were stored in the `/data` directory

2. **Database Setup**
   - PostgreSQL database was created with PostGIS extension enabled
   ```sql
   CREATE DATABASE overture;
   \c overture
   CREATE EXTENSION postgis;
   ```

3. **Data Import**
   - Raw data was processed and imported into PostgreSQL tables
   - Spatial indexes were created for geometry columns
   - Required transformations and data cleaning were performed

4. **Dump Creation**
   ```bash
   pg_dump -Fc overture > overture.dump
   ```

## Using the Dump File

To restore the database:
```bash
pg_restore -d overture overture.dump
```

This process ensures that the data is correctly imported into the PostgreSQL database, ready for use in applications that require geospatial capabilities.


## Schema Information

[Add details about the database schema, table structures, and any important indexes or views]

## Data Updates

This dump was created on [DATE]. For the latest data, please refer to the Overture Maps Foundation releases.

## License

This data is derived from Overture Maps Foundation and is subject to their licensing terms. Please see [Overture Maps Foundation License](https://overturemaps.org/license/) for more information.