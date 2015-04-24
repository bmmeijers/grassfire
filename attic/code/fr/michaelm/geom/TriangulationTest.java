/*
 * 2009-08-15
 *
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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import com.vividsolutions.jts.geom.*;


/**
 * Utility class to test the Triangulation methods.
 */
public class TriangulationTest {
    
    static Coordinate[] pts1 = null;
    
    static final Coordinate.DimensionalComparator COORD2DCOMP = new Coordinate.DimensionalComparator();
    
    static {
        pts1 = new Coordinate[]{
            new Coordinate(2,8),
            new Coordinate(2,2),
            new Coordinate(8,2),
            new Coordinate(8,8),
            new Coordinate(7,6),
            new Coordinate(3,6),
            new Coordinate(3,4),
            new Coordinate(7,4)
        };
        pts1 = new Coordinate[]{
            new Coordinate(7,6),
            new Coordinate(2,8),
            new Coordinate(2,2),
            new Coordinate(8,8),
            new Coordinate(3,6),
            new Coordinate(3,4),
            new Coordinate(8,2),
            new Coordinate(7,4)
        };
        pts1 = new Coordinate[1000000];
        for (int i=0 ; i<1000000 ; i++) pts1[i] = new Coordinate(Math.random()*1000000, Math.random()*1000000);
    }

    public static void main(String[] args) {
        TriangulationTest test = new TriangulationTest();
        test.testTriangulationOfOrderedPoints(pts1);
        test.testTriangulationOfOrderedPoints(pts1);
        //test.testTriangulationOfOrderedPoints(pts1);
        //test.testTriangulationOfOrderedPoints(pts1);
        test.testTriangulationOfRandomPoints(pts1);
        test.testTriangulationOfRandomPoints(pts1);
        //test.testTriangulationOfRandomPoints(pts1);
        //test.testTriangulationOfRandomPoints(pts1);
        test.testFastDelaunayTriangulator(pts1);
        test.testFastDelaunayTriangulator(pts1);
    }
    
    private void testTriangulationOfOrderedPoints(Coordinate[] tp) {
        System.out.println("testTriangulationOfOrderedPoints with " + tp.length + " points");
        long t0 = System.currentTimeMillis();
        Set<Coordinate> set = new HashSet<Coordinate>(Arrays.asList(tp));
        List<Coordinate> pts = new ArrayList<Coordinate>(set);
        long t1 = System.currentTimeMillis();
        System.out.printf("   set created in %10.3f sec\n", (0.001*(t1-t0)));
        
        Collections.sort(pts, COORD2DCOMP);
        long t2 = System.currentTimeMillis();
        System.out.printf("   sorted in %10.3f sec\n", (0.001*(t2-t1)));
        
        Triangulation T = new Triangulation();
        T.addSortedVertices(pts);
        long t3 = System.currentTimeMillis();
        System.out.printf("   triangulated in %10.3f sec\n", (0.001*(t3-t2)));
    }
    
    private void testTriangulationOfRandomPoints(Coordinate[] tp) {
        System.out.println("testTriangulationOfRandomPoints with " + tp.length + " points");
        long t0 = System.currentTimeMillis();
        //Set<Coordinate> set = new HashSet<Coordinate>(Arrays.asList(tp));
        List<Coordinate> pts = new ArrayList<Coordinate>(/*set*/Arrays.asList(tp));
        long t1 = System.currentTimeMillis();
        System.out.printf("   set created in %10.3f sec\n", (0.001*(t1-t0)));
        
        //Collections.shuffle(pts);
        long t2 = System.currentTimeMillis();
        System.out.printf("   shuffled in %10.3f sec\n", (0.001*(t2-t1)));
        
        Triangulation T = new Triangulation();
        T.initFirstEdge(pts.get(0), pts.get(1));
        for (int i = 2 ; i < pts.size() ; i++) {T.insert(pts.get(i));}
        long t3 = System.currentTimeMillis();
        System.out.printf("   triangulated in %10.3f sec\n", (0.001*(t3-t2)));
    }
    
    private void testFastDelaunayTriangulator(Coordinate[] tp) {
        System.out.println("testFastDelaunayTriangulator with " + tp.length + " points");
        long t0 = System.currentTimeMillis();
        List<Geometry> list = new ArrayList<Geometry>();
        GeometryFactory gf = new GeometryFactory();
        for (Coordinate c : tp) list.add(gf.createPoint(c));
        //Set<Coordinate> set = new HashSet<Coordinate>(Arrays.asList(tp));
        //List<Coordinate> pts = new ArrayList<Coordinate>(set);
        long t1 = System.currentTimeMillis();
        System.out.printf("   set created in %10.3f sec\n", (0.001*(t1-t0)));
        
        //Collections.sort(pts, COORD2DCOMP);
        long t2 = System.currentTimeMillis();
        //System.out.printf("   sorted in %10.3f sec\n", (0.001*(t2-t1)));
        
        FastDelaunayTriangulator FDT = new FastDelaunayTriangulator();
        try {
            FDT.triangulate(list.iterator());
        } catch(TriangulationException te) {te.printStackTrace();}
        long t3 = System.currentTimeMillis();
        System.out.printf("   triangulated in %10.3f sec\n", (0.001*(t3-t2)));
    }


}
