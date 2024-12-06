/* Prompt: Find all parks within 2 kilometers of Regent's Canal. */ 
SELECT id, 
       NAMES, 
       geometry
FROM omf_place 
WHERE categories::JSON->>'primary' = 'park' 
  AND ST_DWithin(geometry, 
                   (SELECT ST_Union(geometry) 
                    FROM omf_water 
                    WHERE NAMES::JSON->>'primary' = 'Regent''s Canal'), 2000)
-----------------------------------
/* Prompt: List all buildings with more than 20 floors that are within 500 meters of the River Fleet. */
SELECT id,
       geometry,
       num_floors
FROM omf_building
WHERE num_floors > 20
  AND ST_DWithin(geometry,
                   (SELECT ST_Union(geometry)
                    FROM omf_water
                    WHERE NAMES::JSON->>'primary' = 'River Fleet'), 500)
-----------------------------------
/* Prompt: Find the 10 nearest coffee shops to Battlebridge Basin. */ WITH basin_geometry AS
  (SELECT ST_Union(geometry) AS geometry
   FROM omf_water
   WHERE NAMES::JSON->>'primary' = 'Battlebridge Basin')
SELECT id,
       NAMES,
       geometry,
       ST_Distance(geometry,
                     (SELECT geometry
                      FROM basin_geometry)) AS distance
FROM omf_place
WHERE categories::JSON->>'primary' = 'coffee_shop'
ORDER BY distance
LIMIT 10
-----------------------------------
/* Prompt: List all restaurants that intersect with areas categorized as parks. */
SELECT p.id,
       p.names::JSON->>'primary' AS restaurant_name,
       p.geometry
FROM omf_place AS p
JOIN
  (SELECT geometry
   FROM omf_place
   WHERE categories::JSON->>'primary' = 'park') AS parks ON ST_Intersects(p.geometry, parks.geometry)
WHERE p.categories::JSON->>'primary' = 'restaurant'
-----------------------------------
/* Prompt: Show all water features that contain at least one building taller than 50 meters. */
SELECT w.id,
       w.names,
       w.geometry
FROM omf_water w
WHERE EXISTS
    (SELECT 1
     FROM omf_building b
     WHERE b.height > 50
       AND ST_Within(b.geometry, w.geometry))
-----------------------------------
