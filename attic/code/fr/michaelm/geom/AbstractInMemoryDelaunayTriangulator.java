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

public abstract class AbstractInMemoryDelaunayTriangulator extends AbstractTriangulator {


    /**
     * Triangles of the triangulation.
     * Do not contain phantom triangles located out of the convex hull.
     */
    List<Triangle> triangles = new ArrayList<Triangle>();


    /**
     * A phantom Triangle located out of the convex hull and having HORIZON as
     * its C point.
     */
    protected Triangle currentExternalTriangle;


    /**
     * Fictive Coordinate representing the Horizon, or an infinite point.
     * It closes triangles around the convex hull of the triangulation
     */
    protected static final Coordinate HORIZON = new Coordinate(Double.NaN, Double.NaN);

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


    protected void link (Triangle t1, int side1, Triangle t2, int side2) {
        t1.setNeighbour(side1, t2);
        t2.setNeighbour(side2, t1);
    }


    protected void link (Triangle t1, int side1, Triangle t2) {
        if (t1.getVertex(side1) == t2.getVertex(side1)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour((side1+2)%3, t1);
        }
        else if (t1.getVertex(side1) == t2.getVertex((side1+1)%3)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour(side1, t1);
        }
        else if (t1.getVertex(side1) == t2.getVertex((side1+2)%3)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour((side1+1)%3, t1);
        }
    }
}
