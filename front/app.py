import os
import requests
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import pydeck as pdk
import folium
from streamlit_folium import st_folium
from sqlalchemy import create_engine

POSTGRES_USER = "mapper" #"os.getenv("POSTGRES_USER")"
POSTGRES_PASSWORD = "password" #os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = "localhost" #os.getenv("POSTGRES_HOST")
POSTGRES_PORT = "5433" #os.getenv("POSTGRES_PORT")
POSTGRES_DB = "overture" #os.getenv("POSTGRES_DB")

st.set_page_config(layout="wide")

# # Get API details from environment variables, with defaults
# API_HOST = os.getenv("API_HOST", "api")  # Default to 'api' for Docker
# API_PORT = os.getenv("API_PORT", "8000")
# API_URL = f"http://{API_HOST}:{API_PORT}"


engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
# Function to create a database connection
@st.cache_resource
def get_engine():
    return engine

engine = get_engine()
# Query execution with explicit connection closure
def fetch_data(query):
    with engine.connect() as connection:
        return gpd.read_postgis(query, con=connection, geom_col="geometry")

st.title("Simple Map")

col1, col2 = st.columns(2)  

with col1:
    # One shot
    st.write("Write a query")
    prompt = st.text_input("Query")
    selected_query = st.selectbox("Select a query", 
                                ["SELECT id, num_floors, geometry FROM omf_building LIMIT 10", 
                                "SELECT id, class, geometry FROM omf_water LIMIT 10", 
                                "SELECT names::json->>'primary' as name, geometry FROM omf_place LIMIT 10"
                                ])

with col2:
    # Run query
    st.write(prompt)
    gdf = fetch_data(selected_query)

    # Compute the bounding box
    minx, miny, maxx, maxy = gdf.total_bounds
    # Compute the center of the bounding box
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles="CartoDB positron")



    for _, r in gdf.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})

        geo_j.add_to(m)
    # Fit the map to the bounding box
    m.fit_bounds([[miny, minx], [maxy, maxx]])
    st_data = st_folium(m, width=725)

engine.dispose()