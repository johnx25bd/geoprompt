import os
import json
import requests

import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_monaco import st_monaco
import sqlparse

# Setup and config variables
st.set_page_config(layout="wide")

# Get API details from environment variables, with defaults
API_HOST = os.getenv("API_HOST", "api")  # Default to 'api' for Docker
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"


if 'geojson' not in st.session_state:
    st.session_state.geojson = None
if 'query_response' not in st.session_state:
    st.session_state.query_response = None
if 'query' not in st.session_state:
    st.session_state.query = None
if 'show_geojson' not in st.session_state:
    st.session_state.show_geojson = False

# The Page
st.title("Geoprompt")
st.subheader("A natural language interface for geospatial databases")

col1, col2 = st.columns(2)  

# The left column: prompt + query
with col1:
    # One shot
    model = st.radio("Select a model", 
                     ["gpt-4o-2024-08-06",
                      "o1-preview-2024-09-12",
                      "gpt-4o-mini",
                      "o1-mini"])
    
    prompt = st.text_input("Enter a prompt", 
                           "Find all parks within 2 kilometers of Regent's Canal.")

    query_display = st.container()
    geojson_display = st.container()
    
    if st.button("Generate query"):
             # Run query
        @st.cache_data
        def get_query(p, m):
            return requests.post(
                f"{API_URL}/prompt", 
                json={"prompt": p,
                      "model": m})
        
        q_response = get_query(prompt, model).json()["query"]
        st.session_state.query_response = json.loads(q_response)['sql']
        st.session_state.show_geojson = False

    with query_display:
        if st.session_state.query_response:
            st.write(f"Query returned:")
            # Display the query in an editable text area
            st.session_state.query = sqlparse.format(st.session_state.query_response, 
                                              reindent=True, 
                                              keyword_case="upper")



            updated_query = st_monaco(
                value=st.session_state.query,
                height=300,
                language="sql",
                theme="vs",
            )
            if updated_query:
                st.session_state.query = updated_query
# ---- Edited to here, let's test ----

    # add a button to run the query
    if st.button("Run query"):

        # Cache this
        @st.cache_data
        def get_geojson(q):
            return requests.post(
                f"{API_URL}/query", 
                json={"query": q})
        
        prepared_query = st.session_state.query_response
        st.session_state.geojson = get_geojson(st.session_state.query).json()
        st.session_state.show_geojson = True
        # API call
        with geojson_display:
            if st.session_state.show_geojson and st.session_state.geojson:
                st.write(f"GeoJSON returned:")
                st.write(st.session_state.geojson)

# The right column: map + geospatial data
with col2:
    
    # Pause to set up docker compose
    if st.session_state.geojson:
        gdf = gpd.GeoDataFrame.from_features(st.session_state.geojson["features"])

        # TODO: add a map
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

