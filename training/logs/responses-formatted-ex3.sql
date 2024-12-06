/* Prompt: Find all parks within 2 kilometers of Regent's Canal. */ 
SELECT id, 
       NAMES, 
       geometry 
FROM omf_place 
WHERE categories::JSON->>'primary' = 'park' 
  AND ST_DWithin(ST_Transform(geometry, 3857), 
                   (SELECT ST_Transform(ST_Union(geometry), 3857) 
                    FROM omf_water 
                    WHERE NAMES::JSON->>'primary' = 'Regent''s Canal'), 2000)
-----------------------------------
/* Prompt: List all buildings with more than 20 floors 
that are within 500 meters of the River Fleet. */
SELECT id,
       geometry,
       height,
       num_floors
FROM omf_building
WHERE num_floors > 20
  AND ST_DWithin(geometry,
                   (SELECT ST_Union(geometry)
                    FROM omf_water
                    WHERE NAMES::JSON->>'primary' = 'River Fleet'), 500)
-----------------------------------
/* Prompt: Find the 10 nearest coffee shops to Battlebridge Basin. */ -- Using a common table expression (CTE) to fetch the geometry of Battlebridge Basin
WITH basin_geometry AS
  (SELECT geometry
   FROM omf_water
   WHERE NAMES::JSON->>'primary' = 'Battlebridge Basin'
   LIMIT 1)
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
       p.names,
       p.geometry
FROM omf_place p
JOIN omf_water w ON ST_Intersects(p.geometry, w.geometry)
WHERE p.categories::JSON->>'primary' = 'restaurant'
  AND w.subtype = 'park'
-----------------------------------
/* Prompt: Show all water features that contain at least one building taller than 50 meters. */
SELECT w.id,
       w.geometry,
       w.names
FROM omf_water w
WHERE EXISTS
    (SELECT 1
     FROM omf_building b
     WHERE b.height > 50
       AND ST_Contains(w.geometry, b.geometry))
-----------------------------------
