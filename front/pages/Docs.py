import streamlit as st
import pandas as pd

st.set_page_config(
    layout="wide",
    page_title="Landline Docs",
    page_icon="☎"
)

st.title("Documentation")

st.markdown("""
## Overview

Landline is a natural language interface for geospatial databases. It uses OpenAI's GPT-4 to translate natural language queries into SQL, which are then executed against a PostGIS database containing Overture Maps data.

### How it Works

1. **Natural Language Processing**: Your query is sent to GPT-4, which has been trained with examples of spatial queries and their corresponding SQL translations.
2. **SQL Generation**: The model generates a PostGIS-compatible SQL query, handling spatial relationships, distance calculations, and complex joins.
3. **Query Execution**: The SQL is executed against our PostGIS database containing Overture Maps data.
4. **Visualization**: Results are displayed on an interactive map using Folium.

### Data Sources

The demo currently uses [Overture Maps](https://overturemaps.org) data for northeast London, including:
- Places (POIs, landmarks, businesses)
- Buildings (with height and floor information)
- Waterways (rivers, canals, basins)

### Query Types

The system supports various types of spatial queries:
- Proximity searches ("Find X near Y")
- Distance-based queries ("within X meters of")
- Intersection queries ("intersects with")
- Attribute filters (categories, names, properties)
- Combinations of the above

### Tips for Better Results

1. **Be Specific**:
   - Include numbers ("10 nearest" vs just "nearest")
   - Specify distance units ("meters" or "kilometers")
   - Use exact place names from the coverage area

2. **Supported Relationships**:
   - "near", "closest to", "nearest"
   - "within X meters/kilometers of"
   - "intersects with"
   - "contains"
   - "crosses"

3. **Data Categories**:
   - Places: restaurants, cafes, shops, stations, etc.
   - Buildings: height, floors, shape
   - Waterways: rivers, canals, basins

## What's Next?

### Towards a More Agentic System

The current system is a simple translation layer between natural language and SQL. However, we envision a more sophisticated agentic system that could:

1. **Multi-step Reasoning**:
   - Break complex queries into sub-queries
   - Combine results from multiple queries
   - Handle queries that require intermediate calculations

2. **Context Awareness**:
   - Remember previous queries and their results
   - Build on previous context
   - Understand user preferences

3. **Data Understanding**:
   - Recognize when data might be incomplete
   - Suggest alternative queries when exact matches aren't found
   - Handle variations in place names and addresses

4. **Interactive Refinement**:
   - Ask clarifying questions
   - Suggest query improvements
   - Explain why certain results were returned

5. **Spatial Reasoning**:
   - Understand relative spatial relationships
   - Handle complex geographic concepts
   - Support natural descriptions of locations

6. **Enhanced Geocoding**:
   - Better handling of addresses and postcodes
   - Integration with multiple geocoding services
   - Fuzzy matching for location names

### Technical Roadmap

1. **Short Term**:
   - Expand coverage area
   - Add more data sources
   - Improve query performance
   - Add more example queries

2. **Medium Term**:
   - Implement query memory and context
   - Add interactive query refinement
   - Improve error handling and suggestions
   - Support more complex spatial operations

3. **Long Term**:
   - Full agentic system with multi-step reasoning
   - Integration with real-time data sources
   - Support for temporal queries
   - Advanced visualization options

## Contributing

Landline is open source! Visit our [GitHub repository](https://github.com/johnx25bd/landline) to:
- Report issues
- Suggest features
- Contribute code
- Discuss ideas

## Contact

Questions, suggestions, or interested in using Landline for your project? Contact john@landline.world
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