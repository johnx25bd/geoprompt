/*
  This query retrieves all parks that are located within 2 kilometers of 'Regent's Canal'.
  It uses PostGIS spatial functions to find features in proximity to a specified water body.
*/ 
SELECT p.names, 
       p.addresses, 
       p.categories, 
       ST_AsText(p.geometry) AS geometry_text
FROM omf_place AS p, 
     omf_water AS w 
WHERE w.names = 'Regent''s Canal' -- fixed this line manually ....
  AND ST_DWithin(p.geometry, w.geometry, 2000)
  AND p.categories LIKE '%park%';
/*
Query to list all buildings with more than 20 floors that are within 500 meters of the River Fleet
*/
SELECT b.*
FROM omf_building AS b
JOIN omf_water AS w ON ST_DWithin(b.geometry, w.geometry, 500)
WHERE w.names = 'River Fleet'
  AND b.num_floors > 20;
/*
Query to find the 10 nearest coffee shops to Battlebridge Basin.

Steps:
1. Identify the location of Battlebridge Basin from the omf_water table.
2. Find all places categorized as 'coffee_shop' from the omf_place table.
3. Use PostGIS function ST_Distance to calculate the distance between
   Battlebridge Basin and each coffee shop.
4. Order the results by distance and limit the output to 10.
*/ WITH battlebridge_basin_location AS
  (SELECT geometry
   FROM omf_water
   WHERE NAMES = 'Battlebridge Basin')
SELECT place.id,
       place.names,
       place.geometry,
       ST_Distance(place.geometry, basin.geometry) AS distance
FROM omf_place AS place,
     battlebridge_basin_location AS basin
WHERE place.categories = 'coffee_shop'
ORDER BY distance
LIMIT 10;
/*
This query selects all places categorized as 'restaurant' from the 'omf_place' table
that intersect with areas categorized as 'park' in the 'omf_place' table.
We'll use a self-join approach, utilizing the ST_Intersects PostGIS function.
We assume that the 'categories' column contains relevant tags for filtering the places.
*/ 
SELECT restaurants.id, 
       restaurants.names, 
       restaurants.addresses
FROM omf_place AS restaurants
JOIN omf_place AS parks ON ST_Intersects(restaurants.geometry, parks.geometry) 
WHERE restaurants.categories = 'restaurant' 
  AND parks.categories = 'park';
/* This query retrieves all water features from 'omf_water' that contain
 * at least one building from 'omf_building' with a height greater than 50 meters.
 */
SELECT water.id,
       water.names,
       water.geometry
FROM omf_water AS water
WHERE EXISTS
    (SELECT 1
     FROM omf_building AS building
     WHERE ST_Contains(water.geometry, building.geometry)
       AND building.height > 50);
