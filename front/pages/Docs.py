import streamlit as st
import pandas as pd

st.title("Using Landline")

st.markdown("""
## About Geospatial Queries

Geospatial queries are unique because they deal with geometric data types and spatial relationships. Unlike regular SQL queries that might ask "show me all restaurants that serve pizza".
            
## Prompts

For this prototype, we've used a simple prompt engineering approach to generate valid PostGIS SQL. Prompts focused on building, water, and place features in northeast London are supported in this demo — such as:
- "Find buildings within 100m of Regent's Canal"
- "Find coffee shops within 500m of Battlebridge Basin"
- "What is the total area of buildings within 1km of the River Lee?"

## Our Data Source

Our data comes from the [Overture Maps Foundation](https://overturemaps.org/), an open source mapping initiative.
            
We've extracted data for three key features, focused on northeast London for this prototype.
""")

# Create a DataFrame for the table schemas
schema_data = {
    'Table': [
        'omf_building', 'omf_building', 'omf_building', 'omf_building',
        'omf_water', 'omf_water', 'omf_water',
        'omf_place', 'omf_place', 'omf_place'
    ],
    'Column': [
        'geometry', 'height', 'num_floors', 'roof_shape',
        'geometry', 'names', 'type',
        'geometry', 'names', 'class'
    ],
    'Data Type': [
        'GEOMETRY', 'FLOAT', 'INTEGER', 'TEXT',
        'GEOMETRY', 'JSONB', 'TEXT',
        'GEOMETRY', 'JSONB', 'TEXT'
    ],
    'Description': [
        'Building footprint', 'Height in meters', 'Number of floors', 'Shape of roof',
        'Water feature geometry', 'Name in different languages', 'Type of water feature',
        'Place geometry', 'Place names', 'Category of place'
    ]
}

schema_df = pd.DataFrame(schema_data)

st.markdown("""
## Database Schema

We maintain three main tables in our PostGIS database:
- **Buildings**: Physical structures with attributes like height and roof type
- **Water Features**: Rivers, canals, and water bodies
- **Places**: Points of interest, parks, and other notable locations
""")

st.dataframe(schema_df, use_container_width=True)

st.markdown("""
## Data Processing Pipeline

1. **Download**: Raw data is downloaded from Overture Maps Foundation
2. **Load**: Data is loaded into PostGIS using Geopandas

The complete data processing workflow is documented in our [data processing guide](https://github.com/johnx25bd/landline/blob/main/data/README.md).

## Example Data

Try asking questions like:
- "Show me all buildings taller than 30 meters"
- "Find water features near parks"
- "List places within 500m of the Thames"
""")