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
st.set_page_config(
    layout="wide",
    page_title="Landline Demo",
    page_icon="☎"
)

# Get API details from environment variables, with defaults
API_HOST = os.getenv("API_HOST", "api")  # Default to 'api' for Docker
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"

# Define the data coverage bounding box
BOUNDS_SOUTH = 51.521142
BOUNDS_WEST = -0.146821
BOUNDS_NORTH = 51.583499
BOUNDS_EAST = -0.052669

# Initialize session state variables
if 'geojson' not in st.session_state:
    st.session_state.geojson = None
if 'query_response' not in st.session_state:
    st.session_state.query_response = None
if 'query' not in st.session_state:
    st.session_state.query = None
if 'show_geojson' not in st.session_state:
    st.session_state.show_geojson = False
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = True
if 'query_error' not in st.session_state:
    st.session_state.query_error = None
if 'map' not in st.session_state:
    # Center the map on the data coverage area
    center_lat = (BOUNDS_SOUTH + BOUNDS_NORTH) / 2
    center_lon = (BOUNDS_WEST + BOUNDS_EAST) / 2
    initial_zoom = 12

    # Create base map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=initial_zoom, tiles="CartoDB positron")
    
    # Add bounding box for data coverage
    bounds = [[BOUNDS_SOUTH, BOUNDS_WEST], [BOUNDS_NORTH, BOUNDS_EAST]]
    folium.Rectangle(
        bounds=bounds,
        color="gray",
        weight=2,
        fill=False,
        popup="Data coverage area",
        opacity=0.8
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    st.session_state.map = m
    st.session_state.bounds = bounds

col1, col2 = st.columns(2)  

# The left column: prompt + query
with col1:

    # The Page
    st.title("Landline `Demo`")
    st.subheader("A natural language interface for geospatial databases")
    
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = True

    def toggle_instructions():
        st.session_state.show_instructions = not st.session_state.show_instructions
        
    with st.expander("Instructions", expanded=st.session_state.show_instructions):
        st.write("""
        Landline is a demo LLM-powered interface for geospatial databases, powered by OpenAI GPT-4o, PostGIS, Folium and Overture Maps data.

        **Available Data:**
        - Places of Interest (cafes, restaurants, shops, etc.)
        - Buildings
        - Waterways (rivers, canals)""")
        
        subcol1, subcol2, subcol3 = st.columns([1,2,1])
        with subcol2:
            st.image("./assets/layers.png", width=200)
            
        st.write("""
        **Example Prompts:**
        - "Find the 10 nearest coffee shops to Battlebridge Basin"
        - "Show me all restaurants within 100 meters of the Regent's Canal"
        - "Find buildings within 50 meters of any place with 'Kings Cross' in its name"
        - "List waterways that intersect with City Road"

        **Tips:**
        - Specify numbers (e.g., "10 nearest" rather than "nearest")
        - Use place names from northeast London
        - For landmarks, try variations of the name (e.g., "Kings Cross", "King's Cross")
        - Include distance metrics when relevant (meters/kilometers)
        - Mention specific features (buildings, waterways, restaurants, etc.)
        - You can edit the SQL query in the editor, and run the updated query

        **Coverage Area:** Northeast London (Kings Cross up to Stamford Hill)
                 
        **Note:** We don't support geocoding yet, so addresses and postcodes won't work as well as they would seem — should we build a more sophisticated agentic system?

        See the docs for more examples, and the [repo on Github](https://github.com/johnx25bd/landline) for source code.

        Questions or suggestions? Reach out to john@landline.world
        """)
        if st.button("Got it!", type="primary", on_click=toggle_instructions):
            st.rerun()

    # One shot
    model = "gpt-4o"
                         
    prompt = st.text_input("Enter a prompt", 
                           "Find the 10 nearest coffee shops to Battlebridge Basin.")

    # Create containers BEFORE any dynamic content
    button_container = st.container()
    query_display = st.container()
    
    # Put the Generate Query button in its container
    with button_container:
        generate_button = st.button("Generate query")
    
    if generate_button:
        with st.spinner("Generating and executing query..."):
            try:
                # First get the SQL query
                q_response = requests.post(
                    f"{API_URL}/prompt", 
                    json={"prompt": prompt,
                          "model": model}).json()["query"]
                st.session_state.query_response = json.loads(q_response)['sql']
                
                # Then immediately execute it
                result = requests.post(
                    f"{API_URL}/query", 
                    json={"query": st.session_state.query_response}).json()
                
                # Check if we got any features back
                if result and result.get("features") and len(result["features"]) > 0:
                    st.session_state.geojson = result
                    st.session_state.show_geojson = True
                    st.session_state.query_error = None
                else:
                    st.session_state.geojson = None
                    st.session_state.show_geojson = False
                    st.session_state.query_error = "That query didn't return any results — try adjusting your prompt, or try a different location within the coverage area."
            except Exception as e:
                st.session_state.query_error = f"An error occurred: {str(e)}"
                st.session_state.geojson = None
                st.session_state.show_geojson = False

    # Display the Monaco editor in its container
    with query_display:
        if st.session_state.query_response:
            st.write("Query returned:")
            try:
                formatted_sql = sqlparse.format(
                    st.session_state.query_response, 
                    reindent=True, 
                    keyword_case='upper'  # lowercase 'upper' instead of 'UPPER'
                )
                
                updated_query = st_monaco(
                    value=formatted_sql,
                    height=300,
                    language="sql",
                    theme="vs",
                )
                
                if updated_query and updated_query != formatted_sql:
                    st.session_state.query = updated_query
                    if st.button("Run updated query"):
                        with st.spinner("Executing updated query..."):
                            try:
                                result = requests.post(
                                    f"{API_URL}/query", 
                                    json={"query": updated_query}).json()
                                
                                # Check if we got any features back
                                if result and result.get("features") and len(result["features"]) > 0:
                                    st.session_state.geojson = result
                                    st.session_state.show_geojson = True
                                    st.session_state.query_error = None
                                else:
                                    st.session_state.geojson = None
                                    st.session_state.show_geojson = False
                                    st.session_state.query_error = "That query didn't return any results — try adjusting your query."
                            except Exception as e:
                                st.session_state.query_error = f"Error executing query: {str(e)}"
                                st.session_state.geojson = None
                                st.session_state.show_geojson = False
                
                # Show error message after displaying the SQL
                if st.session_state.query_error:
                    st.error(st.session_state.query_error)
                    
            except Exception as e:
                st.error(f"Error formatting SQL: {str(e)}")
                # Still show the unformatted SQL
                st_monaco(
                    value=st.session_state.query_response,
                    height=300,
                    language="sql",
                    theme="vs",
                )



# The right column: map + geospatial data
with col2:
    # Create fresh map
    center_lat = (BOUNDS_SOUTH + BOUNDS_NORTH) / 2
    center_lon = (BOUNDS_WEST + BOUNDS_EAST) / 2
    initial_zoom = 12

    m = folium.Map(location=[center_lat, center_lon], zoom_start=initial_zoom, tiles="CartoDB positron")
    
    # Create feature groups
    bounds_fg = folium.FeatureGroup(name="Coverage Area")
    results_fg = folium.FeatureGroup(name="Query Results")
    
    # Add bounding box for data coverage
    bounds = [[BOUNDS_SOUTH, BOUNDS_WEST], [BOUNDS_NORTH, BOUNDS_EAST]]
    folium.Rectangle(
        bounds=bounds,
        color="gray",
        weight=2,
        fill=False,
        popup="Data coverage area",
        opacity=0.8
    ).add_to(bounds_fg)
    bounds_fg.add_to(m)
    
    # Add GeoJSON if available and not empty
    if st.session_state.geojson and st.session_state.geojson.get("features"):
        gdf = gpd.GeoDataFrame.from_features(st.session_state.geojson["features"])
        
        # Compute the bounding box
        minx, miny, maxx, maxy = gdf.total_bounds

        for _, r in gdf.iterrows():
            sim_geo = gpd.GeoSeries(r["geometry"])
            geo_j = sim_geo.to_json()
            
            # Create popup HTML with all non-geometry columns
            popup_html = "<div style='width: 300px'>"
            for col in r.index:
                if col != 'geometry':
                    value = r[col] if not isinstance(r[col], (dict, list)) else json.dumps(r[col], indent=2)
                    popup_html += f"<b>{col}:</b> {value}<br>"
            popup_html += "</div>"

            # Handle different geometry types
            geom_type = r.geometry.geom_type.lower()
            
            if geom_type == 'point':
                folium.CircleMarker(
                    location=[r.geometry.y, r.geometry.x],
                    radius=8,
                    color="red",
                    fill=True,
                    fillColor="red",
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(results_fg)
            
            elif geom_type == 'linestring':
                folium.GeoJson(
                    data=geo_j,
                    style_function=lambda x: {
                        "color": "blue",
                        "weight": 3,
                        "opacity": 0.8
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(results_fg)
                
                # Add markers at start and end points
                coords = list(r.geometry.coords)
                if coords:
                    folium.CircleMarker(
                        location=[coords[0][1], coords[0][0]],
                        radius=4,
                        color="green",
                        fill=True,
                        popup="Start"
                    ).add_to(results_fg)
                    folium.CircleMarker(
                        location=[coords[-1][1], coords[-1][0]],
                        radius=4,
                        color="red",
                        fill=True,
                        popup="End"
                    ).add_to(results_fg)
            
            else:  # polygon or multipolygon
                folium.GeoJson(
                    data=geo_j,
                    style_function=lambda x: {
                        "fillColor": "orange",
                        "color": "orange",
                        "weight": 2,
                        "fillOpacity": 0.4
                    },
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(results_fg)

                # Add marker at centroid
                centroid = r.geometry.centroid
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=4,
                    color="red",
                    fill=True,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(results_fg)

        # Add results to map
        results_fg.add_to(m)
        
        # Fit map to include both the bounding box and the GeoJSON features
        all_bounds = [[min(miny, BOUNDS_SOUTH), min(minx, BOUNDS_WEST)], 
                     [max(maxy, BOUNDS_NORTH), max(maxx, BOUNDS_EAST)]]
        m.fit_bounds(all_bounds)
    
    # Add layer control
    folium.LayerControl().add_to(m)

    # Display the map
    st_data = st_folium(m, width=725)

    # Display GeoJSON data if requested
    if st.session_state.show_geojson and st.session_state.geojson:
        st.write("GeoJSON returned:")
        st.write(st.session_state.geojson)

