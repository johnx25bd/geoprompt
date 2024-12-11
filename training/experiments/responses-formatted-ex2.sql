SELECT id,
       NAMES,
       geometry
FROM omf_place
WHERE categories::JSON->>'primary' = 'park'
  AND ST_DWithin(geometry,
                   (SELECT geometry
                    FROM omf_water
                    WHERE NAMES::JSON->>'primary' = 'Regent''s Canal'
                    LIMIT 1), 2000);
SELECT id,
       geometry,
       height,
       num_floors
FROM omf_building
WHERE num_floors > 20
  AND ST_DWithin(geometry,
                   (SELECT geometry
                    FROM omf_water
                    WHERE NAMES::JSON->>'primary' = 'River Fleet'
                    LIMIT 1), 500);
WITH basin_geometry AS
  (SELECT geometry
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
LIMIT 10;
/*
List all places categorized as restaurants that intersect
with territorial extents categorized as parks.
*/
SELECT r.id AS restaurant_id,
       r.names AS restaurant_names,
       r.geometry AS restaurant_geometry
FROM omf_place r
JOIN
  (SELECT geometry
   FROM omf_place
   WHERE categories::JSON->>'primary' = 'park') p ON ST_Intersects(r.geometry, p.geometry)
WHERE r.categories::JSON->>'primary' = 'restaurant';
/*
  This query identifies all water features that have at least one building within them
  that exceeds a height of 50 meters.
*/
SELECT w.id,
       w.geometry,
       w.names
FROM omf_water w
WHERE EXISTS
    (SELECT 1
     FROM omf_building b
     WHERE ST_Contains(w.geometry, b.geometry)
       AND b.height > 50);
