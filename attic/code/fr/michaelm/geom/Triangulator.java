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

import java.util.Iterator;
import com.vividsolutions.jts.geom.Geometry;

/**
 * Triangulator is the interface implemented by all the tools performing
 * a triangulation from a set of point, of constraint lines or of polygons.
 *
 * @version 1.0 (2009-09-01)
 * @author Micha&euml;l MICHAUD
 * @since version 1.0
 */

public interface Triangulator {


    /**
     * Triangulate geometries obtained from a Geometry iterator
     * @param geometries to be triangulated
     */
    public void triangulate(Iterator<Geometry> geometryIterator) throws TriangulationException;


    /**
     * Get a {@link Triangle} iterator iterating through all the triangles
     * issued from the triangulation process.
     * Returning an iterator is preferred, because it can iterate through an
     * in-memory list of Triangles or from a stream (e.g. a file), depending on
     * the implementation.
     * @return an Iterator
     */
    public Iterator<Triangle> getTriangleIterator();

}
