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
import java.util.Collections;
import java.util.List;
import com.vividsolutions.jts.geom.*;


/**
 * Data structure and methods to perform a Delaunay Triangulation
 * Input must be a set of {@link Coordinate}s.
 */
// Version 1.0 is a complete redesign of version 0.8 version
// * main Triangulation class has been split into Triangle and Triangulator
// * PointT internal class has been replaced by direct references to Coordinates
// * flip method has been separated from delaunay
// * ccw now returns 0 every time dx1*dy2 == dy1*dx2
// * delaunay method is now applied on valid candidates, no more !
// * the first triangle input in the locate method is now carefully choosen
// * for the triangulation of an ordered set of points, it's about 2 x faster
// * for an incremental triangulation, it is about 4 times faster

public class Triangulation {


    /**
     * List of unique input vertices.
     */
    private List<Coordinate> pts = new ArrayList<Coordinate>();


    /** Steiner points do not belong to the original set of points.
     * Instead, they are points added to the triangulation to add constraints
     * or to refine the triangulation.
     */
    private List<Coordinate> steinerPoints = new ArrayList<Coordinate>();


    private double minimumBreakLineLength = 0.5;


    /**
     * Triangles of the triangulation.
     * Do not contain phantom triangles located out of the convex hull
     */
    List<Triangle> triangles = new ArrayList<Triangle>();


    /**
     * A phantom external infinite triangle located out of the convex hull.
     */
    private Triangle currentExternalTriangle;


    /**
     * Fictive Coordinate representing the Horizon, or an infinite point
     * closing triangles around the convex hull of the triangulation
     */
    private static final Coordinate HORIZON = new Coordinate(Double.NaN, Double.NaN);


    /**
     * The comparator used to sort coordinates
     */
    private static final Coordinate.DimensionalComparator COORD2DCOMP =
        new Coordinate.DimensionalComparator();

    // Logger, even deactivated, takes to much ressources ==>
    // use simple {if (debug) System.out.println} statements instead
    boolean chrono = false;
    private static int debugLevel = 0;
    final static int NO = 0;
    final static int SHORT = 1;
    final static int NORMAL = 2;
    final static int VERBOSE = 3;
    final static int ALL = 4;
    
    private final static String[] INDENT = new String[]{"","    ","        ","            ","                "};
    
    public static void debug(int indent, String message) {System.out.println(INDENT[indent]+message);}


    public Triangulation() {
    }


    /**
     * Main method to triangulate a known list of {@link Coordinate}s.
     * If the coordinate list is well known, use this method rather than
     * incremental method which is much slower.
     * @param list list of {@link Coordinate}s to triangulate. This list is
     * supposed to have been sorted with the COORD2DCOMP comparator.
     */
    public void addSortedVertices(List<Coordinate> list) {
        assert pts.size()==0 : "triangulation must be empty";
        assert list.size()>2 : "coordinate list must contains more than two points";
        
        Runtime runtime = Runtime.getRuntime();
        long t0 = System.currentTimeMillis();
        long mem0 = runtime.totalMemory() - runtime.freeMemory();

        if (chrono) System.out.println("" + list.size() +
            " points to triangulate (" + (mem0)/1024 + " kb memory used)");

        pts.addAll(list);
        initFirstEdge(pts.get(0), pts.get(1));
        for (int i = 2 ; i < pts.size() ; i++) {
            if (debugLevel!=0) debug(0, "Add vertex " + i + " (" + pts.get(i) + ")");
            addExternalVertex(pts.get(i));
        }
        long t1 = System.currentTimeMillis();
        long mem1 = runtime.totalMemory() - runtime.freeMemory();

        if (chrono) System.out.println("" + pts.size() +
            " points triangulated in " + (t1-t0) + "ms (" + (mem1)/1024 + " kb memory used)");

    }


    // TODO : try to generalize in order to remove this method
    public void initFirstEdge(Coordinate c0, Coordinate c1) {
        Triangle t0 = new Triangle(c0, c1, HORIZON);
        Triangle t1 = new Triangle(c1, c0, HORIZON);
        t0.setNeighbours(t1, t1, t1);
        t1.setNeighbours(t0, t0, t0);
        if (debugLevel!=0) debug(0,"Initialisation : t0 = " + t0);
        if (debugLevel!=0) debug(0,"Initialisation : t1 = " + t1);
        currentExternalTriangle = t1;
    }

    /**
     * Add a new vertex to the triangulation. The new Vertex is supposed
     * to be an external Vertex (out of the convex hull).
     * A simple way to guarantee that every new point is out of the convex hull
     * is to sort vertices in an x (then y) order before insertion.
     * @param c coordinate of the point to insert.
     */
    private void addExternalVertex(Coordinate c) {
        List<Triangle> newTriangles = getTrianglesFromCToConvexHull(c);
        for (int i = 0, max = newTriangles.size() ; i < max ; i++) {
            Triangle t = newTriangles.get(i);
            if (debugLevel>=NORMAL) debug(2,"new triangle before delaunay " + t);
            if (/*t.property==-1 ||*/ t.getC() == HORIZON) continue;
            delaunay(t, 0);
        }
        if (debugLevel>=SHORT) {
            for (Triangle t : newTriangles) debug(1,"add triangle " + t);
        }
        triangles.addAll(newTriangles);
    }


    /**
     * Iterates throw every exterior triangles in a ccw orientation.
     * An exterior Triangle is a triangle located out of the point set convex
     * hull. It is composed of three vertices : A, B, HORIZON, where horizon
     * is a fictive point "closing" those infinite triangles.
     * While every exterior triangle is visited, one check if the AB segment
     * of this triangle (i.e. a segment belonging to the convex hull) is visible
     * from the new point c.
     * nextTccw > 0 means next.AB segment is visible
     * nextTccw = 0 means next.AB segment is collinear
     * nextTccw < 0 means next.AB segment is not visible
     *
     * @param c the coordinate to add to the right of the triangulation
     * 
     * @return All triangles visible from c
     */
    private List<Triangle> getTrianglesFromCToConvexHull(Coordinate c) {
        //Triangle currentT = beforeMaxT;
        Triangle currentT = currentExternalTriangle;
        Triangle nextExternalTriangle = currentExternalTriangle.getNeighbour(2);
        int lastCCW = abcOrientation(currentT, c);
        int currentCCW = lastCCW;
        Triangle beforeFirstVisibleT = currentExternalTriangle;
        Triangle firstVisibleT = null;
        Triangle lastVisibleT = null;
        Triangle afterLastVisibleT = nextExternalTriangle;
        List<Triangle> newT = new ArrayList<Triangle>();
        boolean oneCycleCompleted = false;
        //if (debug) System.out.println("   searching visible sides of convex hull");
        while (true) {
            currentT = currentT.getACO();
            currentCCW = abcOrientation(currentT, c);
            if (currentCCW > 0) {
                if (lastCCW <= 0) {
                    firstVisibleT = currentT;
                    beforeFirstVisibleT = currentT.getCBO();
                }
                if (firstVisibleT!=null) {
                    if (debugLevel>=VERBOSE) debug(2,"visible side : " + currentT.getA()+"-"+currentT.getB());
                    currentT.setC(c);
                    newT.add(currentT);
                }
                else {
                    if (debugLevel>=VERBOSE) debug(2,"before first visible side : " + currentT.getA()+"-"+currentT.getB());
                }
            }
            else {
                if (debugLevel>=VERBOSE) debug(2,"invisible side : " + currentT);
                if (firstVisibleT!=null && lastCCW>0) {
                    lastVisibleT = currentT.getCBO();
                    afterLastVisibleT = currentT;
                }
            }
            lastCCW = currentCCW;
            if (firstVisibleT!=null && lastVisibleT!=null) break;
            if (oneCycleCompleted && firstVisibleT==null && lastVisibleT==null) break;
            if (currentT==currentExternalTriangle) oneCycleCompleted = true;
        }

        currentExternalTriangle = new Triangle(c, beforeFirstVisibleT.getA(), HORIZON);
        nextExternalTriangle = new Triangle(afterLastVisibleT.getB(), c, HORIZON);
        linkExteriorTriangles(beforeFirstVisibleT, currentExternalTriangle);
        if (firstVisibleT!=null || lastVisibleT!=null) {
            link(currentExternalTriangle, 0, firstVisibleT, 1);
            link(nextExternalTriangle, 0, lastVisibleT, 2);
        }
        else link(currentExternalTriangle, 0, nextExternalTriangle, 0);
        linkExteriorTriangles(nextExternalTriangle, afterLastVisibleT);
        
        linkExteriorTriangles(currentExternalTriangle, nextExternalTriangle);

        if (debugLevel>=VERBOSE) debug(2,"new exterior triangle : " + currentExternalTriangle);
        if (debugLevel>=VERBOSE) debug(2,"new exterior triangle : " + nextExternalTriangle);
        
        return newT;
    }


    /**
     * Orientation of ABC, useful to determine if AB segment of Triangle ABH
     * lying on the convex hull is visible from C.
     * @return 1 if AB is visible from C, -1 if it is hidden and 0 if collinear
     */
    private int abcOrientation(Triangle ABH, Coordinate C) {
        return ccw(ABH.getA().x, ABH.getA().y,
                   ABH.getB().x, ABH.getB().y,
                   C.x, C.y);
    }

    /**
     * Link t1 and t2 where t1 and t2 are both infinite exterior triangles,
     * t2 following t1 if one iterates around the triangulation in ccw.
     */
    private boolean linkExteriorTriangles(Triangle t1, Triangle t2) {
        assert(t1.getC()==HORIZON && t2.getC()==HORIZON && t1.getA()==t2.getB());
        t1.setACO(t2);
        t2.setCBO(t1);
        return true;
    }


    private boolean link (Triangle t1, int side1, Triangle t2, int side2) {
        t1.setNeighbour(side1, t2);
        t2.setNeighbour(side2, t1);
        return true;
    }


    private boolean link (Triangle t1, int side1, Triangle t2) {
        if (t1.getVertex(side1) == t2.getVertex(side1)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour((side1+2)%3, t1);
            return true;
        }
        else if (t1.getVertex(side1) == t2.getVertex((side1+1)%3)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour(side1, t1);
            return true;
        }
        else if (t1.getVertex(side1) == t2.getVertex((side1+2)%3)) {
            t1.setNeighbour(side1, t2);
            t2.setNeighbour((side1+1)%3, t1);
            return true;
        }
        else return false;
    }
    


    /**
     * Return triangulated points 3 by 3 in order to make it easy to create
     * the jts corresponding triangles.
     */
    public Coordinate[] getTriangulatedPoints() {
      List<Coordinate> triangulatedPoints = new ArrayList<Coordinate>();
      for (int i = 0 ; i < triangles.size() ; i++) {
          Triangle t = triangles.get(i);
          if (null!=t && t.getC()!=HORIZON) {
              triangulatedPoints.add(t.getA());
              triangulatedPoints.add(t.getB());
              triangulatedPoints.add(t.getC());
          }
      }
      return (Coordinate[]) triangulatedPoints.toArray(new Coordinate[]{});
    }

    /*public void addConstraint(Coordinate A, Coordinate B) {
        constraints.add(new T_Edge(A,B));
    }*/
    
   /** Constructeur de l'objet Triangulation.
    * @param points tableau des points à trianguler.
    * @param breaklines tableau des segments de contrainte (paires de PointT)
    */
    /*public Triangulation(Coordinate[] points, int[][] breaklines) {
        try {
            FileHandler fh = new FileHandler("Triangulation.log");
            fh.setFormatter(new SimpleFormatter(){
                    public String format(LogRecord record) {
                        return "" + record.getLevel() + " : " + record.getMessage() + "\r\n";
                    }
            });
            log.addHandler(fh);
            log.setLevel(Level.INFO);
        }
        catch (IOException ioe) {ioe.printStackTrace();}
        
        long t0 = System.currentTimeMillis();
        
        Set hs = new TreeSet();
        this.pts = points;
        this.breaklines = breaklines;
        this.triangles = new ArrayList<Triangle>();
        
        // Les points sont ordonnés et les doublons éliminés
        for (int i = 0 ; i < points.length ; i++) {
          hs.add(new PointT(i));
        }
        this.pts_i = (PointT[])hs.toArray(new PointT[]{});
        
        long t1 = System.currentTimeMillis();
        log.info("Initialisation : " + hs.size() + "/" + points.length + " points triés en " + (t1-t0) + " ms");
    }*/
    
    
    /*
    public Triangle[] getTriangles() {
        return triangles.toArray(new Triangle[triangles.size()]);
    }
    */

    /*
    public void triangulate(){
        long t0 = System.currentTimeMillis();
        
        // Initialisation du premier triangle
        init();
        
        // Insertion des points à trianguler
        for (int i = 2 ; i < pts_i.length ; i++) {
            insert(pts_i[i]);
        }
        // Insertion des contraintes
        if (breaklines != null) {
            for (int i = 0 ; i < breaklines.length ; i++) {
                for (int j = 0 ; j < breaklines[i].length-1 ; j++) {
                    PointT p1 = locateP(currentT, pts[breaklines[i][j]]);
                    PointT p2 = locateP(currentT, pts[breaklines[i][j+1]]);
                    // contraindre la triangulation sur le segment p1-p2
                    depth = 0;
                    if (p1!=null && p2!=null && p1.i!=p2.i) {
                      //System.out.println("Ajouter contrainte " + p1.i + "-" + p2.i);
                      breakAlong(p1,p2);
                    }
                    else {
                        log.warning("Try to insert an invalid breakline");
                    }
                }
            }
        }
        //nettoyerTriangles();
        long t2 = System.currentTimeMillis();
        log.info("" + pts.length + " points triangulés en " + (t2-t0) + " ms");
    }
    */

   /** 
    * Check the delaunay property of this triangle. If the circumcircle contains
    * one of the opposite vertex, the two triangles forming the quadrilatera are
    * flipped. The method is iterative.
    * While triangulating an ordered set of coordinates about
    * <ul>
    * <li>40% of time is spent in flip() method,</li>
    * <li>15% of time is spent in fastInCircle() method and</li>
    * <li>10% of time is spent in getOpposite() method</li>
    * </ul>
    * @param t triangle to check and to modify (if needed)
    * @return true if a flip occured during the delaunay property check
    */
    private void delaunay (Triangle t, int side) {

        if (t.getEdgeType(side)==Triangle.EdgeType.HARDBREAK) return;

        Triangle opp = t.getNeighbour(side);
        if (opp.getC()==HORIZON) return;
        int i = t.getOpposite(side);

        Coordinate p = opp.getVertex(i);
        if (fastInCircle(t.getA(), t.getB(), t.getC(), p) > 0) {
            // Flip triangles without creating new triangle objects

            if (debugLevel>VERBOSE) {
                debug(3,"triangles to flip :");
                debug(3,"   " + t);
                debug(3,"   " + opp);
            }
            flip(t, side, opp, (i+1)%3, false);

            delaunay(t,1);
            delaunay(t,2);
            delaunay(opp,0);
            delaunay(opp,1);

            if (debugLevel>VERBOSE) {
                debug(3,"triangles to flip :");
                debug(3,"   " + t);
                debug(3,"   " + opp);
            }
        }
    }

    /**
     * If t0 and t1 are two triangles sharing a common edge AB,
     * the method replaces ABC and BAD triangles by DCA and DBC, respectively.
     * To be fast, this method supposed that input triangles share a common
     * edge and that this common edge is known.
     * A check may be performed to ensure these conditions are verified.
     */
    public void flip(Triangle t0, int side0, Triangle t1, int side1, boolean check) throws IllegalArgumentException {
        int side0_1 = (side0+1)%3;
        int side0_2 = (side0+2)%3;
        int side1_1 = (side1+1)%3;
        int side1_2 = (side1+2)%3;
        if (check) {
            if (t0.getVertex(side0) != t1.getVertex(side1_1) ||
                t1.getVertex(side1) != t0.getVertex(side0_1)) {
                throw new IllegalArgumentException("flip method can only flip triangles sharing a common edge");
            }
        }
        Coordinate t0A = t1.getVertex(side1_2);
        Coordinate t0B = t0.getVertex(side0_2);
        Coordinate t0C = t0.getVertex(side0);
        Coordinate t1A = t0A;
        Coordinate t1B = t0.getVertex(side0_1);
        Coordinate t1C = t0B;
        // New neighbours
        Triangle newt0N1 = t0.getNeighbour(side0_2);
        Triangle newt0N2 = t1.getNeighbour(side1_1);
        //int property1 = (t.getConstraint((cote+2)%3)?2:0) + (opp.getConstraint((i+2)%3)?4:0);
        Triangle newt1N0 = t1.getNeighbour(side1_2);
        Triangle newt1N1 = t0.getNeighbour(side0_1);
        //int property2 = (opp.getConstraint(i)?1:0) + (t.getConstraint((cote+1)%3)?2:0);
        t0.setABC(t0A, t0B, t0C);
        t0.setBAO(t1);
        link(t0,1,newt0N1);
        link(t0,2,newt0N2);
        //t.property = property1;
        t1.setABC(t1A, t1B, t1C);
        link(t1,0,newt1N0);
        link(t1,1,newt1N1);
        t1.setACO(t0);
    }


  /**
    * Return a positive value if the point p4 lies inside the
    * circle passing through pa, pb, and pc; a negative value if
    * it lies outside; and zero if the four points are cocircular.
    * The points pa, pb, and pc must be in counterclockwise
    * order, or the sign of the result will be reversed.
    */
    private double fastInCircle(Coordinate p1, Coordinate p2, Coordinate p3, Coordinate p4) {
        double adx, ady, bdx, bdy, cdx, cdy;
        double abdet, bcdet, cadet;
        double alift, blift, clift;

        adx = p1.x-p4.x;
        ady = p1.y-p4.y;
        bdx = p2.x-p4.x;
        bdy = p2.y-p4.y;
        cdx = p3.x-p4.x;
        cdy = p3.y-p4.y;

        abdet = adx * bdy - bdx * ady;
        bcdet = bdx * cdy - cdx * bdy;
        cadet = cdx * ady - adx * cdy;
        alift = adx * adx + ady * ady;
        blift = bdx * bdx + bdy * bdy;
        clift = cdx * cdx + cdy * cdy;

        return alift * bcdet + blift * cadet + clift * abdet;
    }


   /**
    * Orientation of the p0-p1-p2 triangle
    * @return -1 if p0-p1-p2 triangle is described in a cw order, 1 if it is
    * described in a ccw order and 0 if it is flat.
    */
    public static int ccw (double p0x, double p0y, double p1x, double p1y,
                           double p2x, double p2y) {
        //double dx1 = p1x - p0x;
        //double dy1 = p1y - p0y;
        //double dx2 = p2x - p0x;
        //double dy2 = p2y - p0y;
        double dx1dy2 = (p1x - p0x) * (p2y - p0y);
        double dy1dx2 = (p1y - p0y) * (p2x - p0x);
        if (dx1dy2 > dy1dx2) return 1;
        else if (dx1dy2 < dy1dx2) return -1;
        else {
            return 0;
          //if (dx1 * dx2 < 0 || dy1 * dy2 < 0) return -1;
          //else if (dx1*dx1 + dy1*dy1 >= dx2*dx2 + dy2*dy2) return 0;
          //else return 1;
        }
    }


   /** Insert a new point in the original pts coordinate array
    * and in the pts_i reference array.
    * This method is used to introduce new points in the triangulation
    * (for exemple to add breaklines while preserving the delaunay property)
    * WARNING, new pts_i are added at the end of the array (after that, the
    * array is no more ordered).
    * @param tIni triangle quelconque à partir duquel le point p
    * est localisé par le jeu des relations d'adjacence.
    * @param p point à ajouter à la triangulation.
    */
    public void insert(Coordinate p) {
        if (debugLevel>=SHORT) debug(0,"Insert point " + p);
        
        // Choose a starting triangle by sampling the triangle list and
        // chhosing the nearest triangle among the sample
        // with this technique, triagulation time is divided by 2 or 3 !
        Triangle ini = chooseTriangleToInitiatePointLocation(p);
        Triangle t = locate(ini, p);
        if (debugLevel>=NORMAL) debug(1,"the point is localized in " + t);
        if (t.getC()==HORIZON) {
            pts.add(p);
            addExternalVertex(p);
        }
        else {
            // TODO : part of operations done by t.locate have already been
            // done in locate(ini, p) ==> try to keep previous information
            // and avoid some ccw calculation
            int pos = t.locate(p);
            int global_pos = pos/100 * (pos/10)%10 * pos%10;
            if (/*global_pos != 1*/global_pos > 1 || pos == 1 || pos == 10 || pos == 100) { // p is out of t or p is on t border
                return;
            }
            pts.add(p);
            // Transform t into ABp and create two new triangles BCp and CAp
            // Be careful, following instructions order is very important
            Triangle tn1 = new Triangle(t.getB(), t.getC(), p);
            Triangle tn2 = new Triangle(t.getC(), t.getA(), p);
            t.setC(p);
            //link(tn0, 0, t.getNeighbour(0));
            link(tn1, 0, t.getNeighbour(1));
            link(tn2, 0, t.getNeighbour(2));
            t.setNeighbour(1,tn1);
            tn1.setNeighbour(2,t);
            tn1.setNeighbour(1,tn2);
            tn2.setNeighbour(2,tn1);
            tn2.setNeighbour(1,t);
            t.setNeighbour(2,tn2);
            // instead of deleting t and adding 3 new triangles,
            // reuse t and add two triangles to the list
            //t.property = -1; delT++;

            //t.setABC(tn0.getA(), tn0.getB(), tn0.getC());
            //t.setNeighbours(tn0.getNeighbour(0), tn0.getNeighbour(1), tn0.getNeighbour(2));
            
            //t.property = tn0.property;
            //triangles.add(tn0);
            triangles.add(tn1);
            triangles.add(tn2);
            if (debugLevel>=NORMAL) {
                debug(2,"new triangle before delaunay " + t);
                debug(2,"new triangle before delaunay " + tn1);
                debug(2,"new triangle before delaunay " + tn2);
            }
            //depth = 0;
            delaunay(t,0);
            //depth = 0;
            delaunay(tn1,0);
            //depth = 0;
            delaunay(tn2,0);
            if (debugLevel>=VERBOSE) {
                debug(2,"Triangulation after insert");
                for (int i = 0 ; i < triangles.size() ; i++) {
                    Triangle tt = triangles.get(i);
                    if (tt.getC()!=HORIZON) debug(3,"" + tt);
                }
            }
        }
    }
    
    private Triangle chooseTriangleToInitiatePointLocation(Coordinate p) {
        Triangle candidate = currentExternalTriangle;
        int totalSize = triangles.size();
        int sampleSize = (int)(Math.sqrt(totalSize)/25);
        double min = Double.MAX_VALUE;
        for (int i = 0 ; i < sampleSize ; i++) {
            Triangle randomTriangle = triangles.get((int)(Math.random()*totalSize));
            double dist = randomTriangle.getA().distance(p);
            if (dist < min) {
                min = dist;
                candidate = randomTriangle;
            }
        }
        return candidate;
    }


    /**
     * Add breaklines for each pair of segments
     * constraintLines[2n] - constraintLines[2n+1]
     * @param constraintLines pairs of coordinates forming edges of the
     * final triangulation
     */
    public void addBreakLines(Coordinate[] constraintLines) {
        for (int i = 1 ; i < constraintLines.length ; i+=2) {
            insertBreakLine(constraintLines[i-1], constraintLines[i], Triangle.EdgeType.HARDBREAK);
        }
    }

    /**
     * Add a breakline along p1-p2.
     * p1 and p2 are supposed to be vertices of the current triangulation.
     * If not, insert those points as new vertices with insert method.
     * @param p1 first point of the BreakLine
     * @param p2 first point of the BreakLine
     * @param type type of BreakLine (maybe VIRTUAL, SOFTBREAK or HARDBREAK)
     */
    private void insertBreakLine(Coordinate p1, Coordinate p2, Triangle.EdgeType type) {
        if (p1.distance(p2) < minimumBreakLineLength) return;
        Triangle ini = chooseTriangleToInitiatePointLocation(p1);
        Triangle t0 = locate(ini, p1);
        // pos should be >=0 as p1 is already a triangulation vertex
        int pos = t0.getIndex(p1);
        Triangle next = null;
        boolean p1p2Exists = t0.getVertex((pos+1)%3)==p2;
        while (!p1p2Exists && (next != t0)) {
            if (null == next) next = t0;
            next = next.getNeighbour((pos+2)%3);
            pos = next.getIndex(p1);
            if (next.getVertex((pos+1)%3)==p2) {
                next.setEdgeType(pos, type);
                next = next.getNeighbour((pos));
                pos = next.getIndex(p2);
                next.setEdgeType(pos, type);
                p1p2Exists = true;
            }
        }
        if (!p1p2Exists) {
            // Introducing a small offset in intermediate mid-points
            // avoid some robustness problems due to colinearity in this method
            // Without this tip, my 600 000 points linear dataset ended
            // in an infinite while loop in this method
            // TODO : find a more elegant way to make the code robust
            Coordinate pi = new Coordinate(
                (p1.x+p2.x)/2+(Math.random()-0.5)*minimumBreakLineLength*0.1,
                (p1.y+p2.y)/2+(Math.random()-0.5)*minimumBreakLineLength*0.1,
                (p1.z+p2.z)/2
            );
            insert(pi);
            insertBreakLine(p1, pi, type);
            insertBreakLine(pi, p2, type);
        }
    }
    /*
    private void breakAlong(PointT p1, PointT p2) {
        //log.fine("Contraindre sur : " + p1.toString() + " - " + p2.toString());
        //if (depth>maxDepth) {return;}
        
        // Do not apply the constraint if the segment is less than minLength
        if (pts[p1.i].distance(pts[p2.i]) < minLength) {return;}
        Triangle t1 = locate(currentT, pts[p1.i]);
        currentT = t1; // rapproche le triangle courant de p1, p2
        Triangle t2 = locate(currentT, pts[p2.i]);
        currentT = t2; // rapproche le triangle courant de p1, p2
        
        Triangle t3 = isLinked(p2, t2, p1);
        // Si p1-p2 est déjà une arête, on se contente d'écrire les contraintes
        // sur les cotés des 2 triangles concernés
        if (null != t3) {
            if (t3.ppp[0].i == p1.i && t3.ppp[1].i == p2.i) {
                t3.setConstraint(0);
            }
            else if (t3.ppp[1].i == p1.i && t3.ppp[2].i == p2.i) {
                t3.setConstraint(1);
            }
            else if (t3.ppp[2].i == p1.i && t3.ppp[0].i == p2.i) {
                t3.setConstraint(2);
            }
            else if (t3.ppp[0].i == p1.i && t3.ppp[2].i == p2.i) {
                t3.setConstraint(2);
            }
            else if (t3.ppp[1].i == p1.i && t3.ppp[0].i == p2.i) {
                t3.setConstraint(0);
            }
            else if (t3.ppp[2].i == p1.i && t3.ppp[1].i == p2.i) {
                t3.setConstraint(1);
            }
            return;
        }
        // Si p1-p2 n'est pas encore une contrainte, on crée un point
        // intermédiaire p2
        Coordinate pi = new Coordinate((pts[p1.i].x+pts[p2.i].x)/2,
                                       (pts[p1.i].y+pts[p2.i].y)/2,
                                       (pts[p1.i].z+pts[p2.i].z)/2);
        //if (Math.abs(t1.isAligned(pi)*t2.isAligned(pi))<0.000001) return;
        insert(currentT, pi);
        int indice_i = pts_i.length-1;
        breakAlong(pts_i[indice_i], p1);
        breakAlong(pts_i[indice_i], p2);
    }
    */

    /**
     *Localise le triangle contenant le point p.
     * @param tIni un triangle quelconque à partir duquel
     * va s'effectuer la localisation.
     * @param p point à localiser.
     * @return un triangle contenant p (inclusion stricte ou limite.
     * Retourne null si p est à l'exterieur de l'enveloppe convexe
     */
    public Triangle locate(Triangle ini, Coordinate p) {
        if (debugLevel>VERBOSE) {debug(3,"searching p " + ini);}
        Triangle t = ini;
        Coordinate C = t.getC();
        double px = p.x;
        double py = p.y;
        if (C==HORIZON) {
            int ccw = ccw(t.getA().x, t.getA().y, t.getB().x, t.getB().y, px, py);
            if (ccw > 0) return t;
            else return locate(t.getNeighbour(0), p);
        }
        int count = 0;
        Triangle previous = null;
        while ((C=t.getC())!=HORIZON && count++<10000) {
            if (debugLevel>VERBOSE) {debug(3,"searching p " + t);}
            double Ax = t.getA().x;
            double Ay = t.getA().y;
            double Bx = t.getB().x;
            double By = t.getB().y;
            double Cx = C.x;
            double Cy = C.y;
            if (t.getBAO() != previous && ccw(Ax, Ay, Bx, By, p.x, py) < 0) {
                previous = t;
                t = t.getNeighbour(0);
                continue;
            }
            if (t.getCBO() != previous && ccw(Bx, By, Cx, Cy, p.x, py) < 0) {
                previous = t;
                t = t.getNeighbour(1);
                continue;
            }
            if (t.getACO() != previous && ccw(Cx, Cy, Ax, Ay, p.x, py) < 0) {
                previous = t;
                t = t.getNeighbour(2);
                continue;
            }
            //System.out.println(count);
            return t;
        }
        return t;
    }



}

