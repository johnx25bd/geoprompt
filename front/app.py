import os
import requests
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import pydeck as pdk
import folium
from streamlit_folium import st_folium

# Setup and config variables
st.set_page_config(layout="wide")

# Get API details from environment variables, with defaults
API_HOST = "0.0.0.0" #os.getenv("API_HOST", "api")  # Default to 'api' for Docker
API_PORT = "8000" #os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"


# The Page
st.title("Simple Map")

col1, col2 = st.columns(2)  

# The left column: prompt + query
with col1:
    # One shot
    model = st.radio("Select a model", 
                     ["gpt", 
                      "xxx"],
                      horizontal=True)
    
    # prompt = st.text_input("Query")
    prompt = st.selectbox("Select a prompt", 
                                ["building", 
                                "water", 
                                "places"
                                ])

     # Run query
    prompt_2_query_response = requests.post(
        f"{API_URL}/prompt", 
        json={"prompt": prompt,
              "model": "gpt"})
    
    query = prompt_2_query_response.json()["query"]
    st.write(f"Query returned for {prompt}: `{query}`")
    # add a button to run the query
    if st.button("Run query"):
        # API call
        st.write(f"{prompt} query: `{query}`")

# The right column: map + geospatial data
with col2:
    geojson = requests.post(
        f"{API_URL}/query", 
        json={"query": query})
        # Pause to set up docker compose
    st.write(geojson.json())

    # TODO: add a map
    # # Compute the bounding box
    # minx, miny, maxx, maxy = gdf.total_bounds
    # # Compute the center of the bounding box
    # center_lat = (miny + maxy) / 2
    # center_lon = (minx + maxx) / 2

    # m = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles="CartoDB positron")

    # for _, r in gdf.iterrows():
    #     # Without simplifying the representation of each borough,
    #     # the map might not be displayed
    #     sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
    #     geo_j = sim_geo.to_json()
    #     geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})

    #     geo_j.add_to(m)
    # # Fit the map to the bounding box
    # m.fit_bounds([[miny, minx], [maxy, maxx]])
    # st_data = st_folium(m, width=725)

