# Collecting Schema Data

We need to provide database schema data to the model so it can make predictions. This will become part of the prompt, so the LLM knows how to structure valid queries as its output.

## Data

We have a PostGIS database with the following tables:

- `omf_building`
- `omf_water`
- `omf_place`

We will download data about the columns, data types, and values in each of these tables, and document them in a structured format.

Get the data types and values for each column.

```sql
SELECT 
    column_name, 
    data_type, 
    example_values
FROM 
    information_schema.columns
WHERE 
    table_name = 'omf_building';
```

Then go through each column and get descriptive statistics. (Here's some example queries.)

```sql
-- Descriptive Statistics for height
SELECT 
    COUNT(height) AS count,
    MIN(height) AS min,
    MAX(height) AS max,
    AVG(height) AS mean,
    STDDEV(height) AS stddev,
    VARIANCE(height) AS variance,
FROM 
    omf_building;

-- Descriptive Statistics for num_floors
SELECT 
    COUNT(num_floors) AS count,
    MIN(num_floors) AS min,
    MAX(num_floors) AS max,
    AVG(num_floors) AS mean,
    STDDEV(num_floors) AS stddev,
    VARIANCE(num_floors) AS variance,
FROM 
    omf_building;

-- Counts for roof_shape groups
SELECT 
    roof_shape, 
    COUNT(*) AS count
FROM 
    omf_building
GROUP BY 
    roof_shape
ORDER BY 
    count DESC;

-- Counts for roof_orientation groups
SELECT 
    roof_orientation, 
    COUNT(*) AS count
FROM 
    omf_building
GROUP BY 
    roof_orientation
ORDER BY 
    count DESC;

-- Counts for roof_color groups
SELECT 
    roof_color, 
    COUNT(*) AS count
FROM 
    omf_building
GROUP BY 
    roof_color
ORDER BY 
    count DESC;



SELECT
   names::json->>'primary' AS primary_name,  COUNT(*)
FROM
    omf_water
	GROUP BY names::json->>'primary';

```

This is not comprehensive, but it's a good start, and good enough for testing I think.