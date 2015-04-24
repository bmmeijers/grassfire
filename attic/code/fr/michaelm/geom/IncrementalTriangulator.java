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

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Geometry;

/**
 * Triangulator able to add new vertices to a triangulation, repeatedly, one
 * vertex at a time.
 * With such a triangulator, there is no pre-condition on vertex order.
 *
 * @version 1.0 (2009-09-01)
 * @author Micha&euml;l MICHAUD
 * @since version 1.0
 */

public interface IncrementalTriangulator extends Triangulator {

    /**
     * Add a new Geometry to be inserted in an existing triangulation.
     */
    public void add(Geometry geometry) throws TriangulationException;

    /**
     * Add a new Vertex to be inserted into an existing triangulation.
     */
    public void add(Coordinate coord) throws TriangulationException;

}
