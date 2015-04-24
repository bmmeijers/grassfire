/*
 * Library Triangulation
 * Copyright (C) 2009 Micha&euml;l MICHAUD
 * michael.michaud@free.fr
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

package fr.michaelm.geom;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Geometry;

/**
 * Base class for Delaunay Triangulation implementations.
 * In mathematics, and computational geometry, a Delaunay triangulation for
 * a set P of points in the plane is a triangulation DT(P) such that no point
 * in P is inside the circumcircle of any triangle in DT(P). Delaunay
 * triangulations maximize the minimum angle of all the angles of the triangles
 * in the triangulation; they tend to avoid skinny triangles.
 *
 * @version 1.0 (2009-09-01)
 * @author Micha&euml;l MICHAUD
 * @since version 1.0
 */

public abstract class AbstractInMemoryTriangulator extends AbstractTriangulator {


    /**
     * Triangles of the triangulation.
     * Do not contain phantom triangles located out of the convex hull.
     */
    List<Triangle> triangles = new ArrayList<Triangle>();


    /**
     * Triangulate geometries.
     * @param geometries to be triangulated
     */
    abstract public void triangulate(Iterator<Geometry> geometryIterator) throws TriangulationException;

    /**
     * Get Triangles issued from the triangulation process.
     * @return a list of Triangles
     */
     public Iterator<Triangle> getTriangleIterator() {
         return triangles.iterator();
     }

}
