
from sqlalchemy import create_engine, text
import json
# Get API details from environment variables, with defaults
API_HOST = "api" #os.getenv("API_HOST", "api")  # Default to 'api' for Docker
API_PORT = "8000" #os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"


POSTGRES_HOST = "postgis" #os.getenv("POSTGRES_HOST")
POSTGRES_PORT = "5432" #os.getenv("POSTGRES_PORT")
POSTGRES_USER = "mapper" #"os.getenv("POSTGRES_USER")"
POSTGRES_PASSWORD = "password" #os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = "overture" #os.getenv("POSTGRES_DB")


engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
print(engine)
# Query execution with explicit connection closure
def query_geojson(query: str):
    clean_query = query.strip().rstrip(';')
    geojson_query = text("""
            SELECT jsonb_build_object(
                'type',     'FeatureCollection',
                'features', jsonb_agg(features.feature)
            )
            FROM (
                SELECT jsonb_build_object(
                    'type',       'Feature',
                    'geometry',   ST_AsGeoJSON(geometry)::jsonb,
                    'properties', to_jsonb(row) - 'geometry'
                ) AS feature
                FROM ({}) row
            ) features;
        """.format(clean_query))
    return geojson_query

def fetch_geojson(query: str):
    with engine.connect() as connection:
        # Read postgis data as geojson, forget geopandas
        geojson_query = query_geojson(query)
        geojson = connection.execute(geojson_query).fetchall()
        return geojson[0][0] if geojson and geojson[0] else None

if __name__ == "__main__":
    geojson = fetch_geojson("SELECT * FROM omf_building LIMIT 10")
    # Write to file
    print(geojson)
    # with open("geojson.json", "w") as f:
    #     json.dump(geojson, f)

