-- as individual linestrings
-- see also http://www.spatialdbadvisor.com/postgis_tips_tricks/128/exploding-a-linestring-or-polygon-into-individual-vectors-in-postgis/
drop table if exists foosegs;
create table foosegs as
SELECT ST_MakeLine(sp,ep) as line_geom FROM 
   (SELECT
      ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
      ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
    FROM
       -- extract the individual linestrings
      (SELECT (ST_Dump(ST_Boundary(geom))).geom
       FROM 
       (
       		-- the polygons
		   select st_geomfromtext('POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))') as geom 
		   union 
		   select st_geomfromtext('POLYGON((5 5, 5 15, 15 15, 15 5, 5 5))') as geom
       ) as polys
       ) AS linestrings
    ) AS segments;

-- get the union of all line segments
select st_astext(st_union(line_geom)) from foosegs;

-- dump the union of these segments, should be noded segments!
select (st_dump(st_union(line_geom))).geom from foosegs;
