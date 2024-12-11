import os
import json
import time
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
st.title("Landline")
st.subheader("A natural language interface for geospatial databases")
st.write("""
An LLM-powered interface for geospatial databases, powered by OpenAI and PostGIS and Overture Maps data.
See the docs for instructions on what prompts are supported with this dataset, and the [repo on Github](https://github.com/johnx25bd/landline) for source code.
""")

col1, col2 = st.columns(2)  

# The left column: prompt + query
with col1:
    # One shot
    with st.expander("Select a model"):
        model = st.radio("Cheating with OpenAI:", 
                         ["gpt-4o-2024-08-06",
                          "o1-preview-2024-09-12",
                          "gpt-4o-mini",
                          "o1-mini"])
    
    prompt = st.text_input("Enter a prompt", 
                           "Find the 10 nearest coffee shops to Battlebridge Basin.")

    # Create containers BEFORE any dynamic content
    button_container = st.container()
    query_display = st.container()
    
    # Put the Generate Query button in its container
    with button_container:
        generate_button = st.button("Generate query")
    
    if generate_button:  # Use the button result instead of creating a new button
        @st.cache_data
        def get_query(p, m):
            return requests.post(
                f"{API_URL}/prompt", 
                json={"prompt": p,
                      "model": m})
        
        q_response = get_query(prompt, model).json()["query"]
        st.session_state.query_response = json.loads(q_response)['sql']
        st.session_state.show_geojson = False

    # Display the Monaco editor in its container
    with query_display:
        if st.session_state.query_response:
            st.write(f"Query returned:")
            st.session_state.query = sqlparse.format(
                st.session_state.query_response, 
                reindent=True, 
                keyword_case="upper"
            )
            
            updated_query = st_monaco(
                value=st.session_state.query,
                height=300,
                language="sql",
                theme="vs",
            )
            
            if updated_query:
                st.session_state.query = updated_query

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



# The right column: map + geospatial data
with col2:

    geojson_display = st.container()
    with geojson_display:
        if st.session_state.show_geojson and st.session_state.geojson:
            st.write(f"GeoJSON returned:")
            st.write(st.session_state.geojson)
    
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
            sim_geo = gpd.GeoSeries(r["geometry"])
            geo_j = sim_geo.to_json()

            # Create popup HTML with all non-geometry columns
            popup_html = "<div style='width: 300px'>"
            for col in r.index:
                if col != 'geometry':
                    # Format JSON columns for better readability
                    if isinstance(r[col], (dict, list)):
                        value = json.dumps(r[col], indent=2)
                    else:
                        value = r[col]
                    popup_html += f"<b>{col}:</b> {value}<br>"
            popup_html += "</div>"



            # Get geometry type
            geom_type = r.geometry.geom_type.lower()

            if geom_type == 'point':
                # For points, just add a CircleMarker
                folium.CircleMarker(
                    location=[r.geometry.y, r.geometry.x],
                    radius=8,
                    color="red",
                    fill=True,
                    fillColor="red",
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
            
            elif geom_type == 'linestring':
                # For lines, add the GeoJson with line styling
                folium.GeoJson(
                    data=geo_j,
                    style_function=lambda x: {
                        "color": "blue",
                        "weight": 3,
                        "opacity": 0.8
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
                
                # Add markers at start and end points
                coords = list(r.geometry.coords)
                if coords:
                    # Start point
                    folium.CircleMarker(
                        location=[coords[0][1], coords[0][0]],
                        radius=4,
                        color="green",
                        fill=True,
                        popup="Start"
                    ).add_to(m)
                    # End point
                    folium.CircleMarker(
                        location=[coords[-1][1], coords[-1][0]],
                        radius=4,
                        color="red",
                        fill=True,
                        popup="End"
                    ).add_to(m)
            
            else:  # polygon or multipolygon
                # Add the polygon
                folium.GeoJson(
                    data=geo_j,
                    style_function=lambda x: {
                        "fillColor": "orange",
                        "color": "orange",
                        "weight": 2,
                        "fillOpacity": 0.4
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)

                # Add a marker at the centroid
                centroid = r.geometry.centroid
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=4,
                    color="red",
                    fill=True,
                    fillColor="red",
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)


        # Fit the map to the bounding box
        m.fit_bounds([[miny, minx], [maxy, maxx]])

        time.sleep(0.1)
        st_data = st_folium(m, width=725)
        gdf

