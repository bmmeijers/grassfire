/*
 * 12/02/2001 - 18:02:17
 *
 * Library geometrie3D - librairie incluant les principales géométries 3D
 * Copyright (C) 2001 Michaël MICHAUD
 * michael.michaud@free.fr
 * 
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


import java.util.*;
import java.util.logging.*;
import java.io.IOException;
import com.vividsolutions.jts.geom.*;

// Version 0.8 (2009-08-02)
// Fixed a bug caused by the maxDepth limitation while trying to triangulate
// a regular grid
// Init method now starts with a simple edge (two adjacent infinite triangles)
// instead of a triangle and the three adjacent infinit triangles in order
// to handle the case where first points are aligned
// Better handling of colinear points in the 

// Version 0.7
// Retour à un tri suivant l'axe des x (plus simple) plutôt que concentrique
// Introduction des génériques (java 1.5)
// Recyclage de triangles invalides plutôt que suppression / création
// Plusieurs petites optimisations
// Amélioration de la doc

// Version 0.6 :
// a - implementation de la methode hashCode de la
// classe PointT indispensable pour garantir l'unicité des points
// dans le HashSet
// b - l'ordre est défini par une distance croissante par rapport
// au point de coordonnees xIni, yIni (propriete statique initialisee
// dans le constructeur).
// c - tout le plan est triangulé, les triangles situés à l'exterieur
// de l'enveloppe convexe sont constitués de deux points de l'enveloppe
// et de l'objet HORIZON (un PointT d'indice i = -1)

// Version 0.5 :
// Remplacement de la propriété booleenne "valide" des Triangle(s)
// par un entier permettant de signaler un segment de contrainte


/**
 * Class implementing algorithms to perform a 2D Delaunay Triangulation
 * or a constrained 2D Delaunay Triangulation.
 */
public class DelaunayTriangulationFactory2 {
  
    //**************************************************************************
    //**************************************************************************
    //*******************           Les variables            *******************
    //**************************************************************************
    //**************************************************************************
    
    Triangulation triangulation;
    
    //List<Coordinate> coordinates;
   /** Candidate coordinates for the triangulation.*/
    //private Coordinate[] pts;
    
   /** Unique ordered points containing reference to points in the pts array.*/
    //private PointT[] pts_i;
    
   /** Constraint segments.
    * Every array in this array refer to points describing a linestring
    * Each segment of these linestring must be edges in the triangulation.
    */
    //private int[][] breaklines;
    
   /** Triangles of the triangulation.*/
    //private List<Triangle> triangles;
    
    // Compteur comptabilisant les triangles à supprimer
    //private int delT = 0;
    
    // triangle quelconque, exterieur à l'enveloppe convexe
    //private Triangle t0;
    
    // triangle courant
    //private Triangle currentT;
    
    // PointT représentant l'infini et utilisé pour définir les triangles
    // extérieurs à l'envelope convexe du semis de points
    //private final PointT HORIZON = new PointT(-1);
    
    // Limite évitant aux opérations de flip de tourner en boucle
    // (cas qui ne devrait théoriquement pas se produire)
    private static final int maxDepth = 32767;
    private int depth = 0;
    
    private static final Coordinate.DimensionalComparator COORD2DCOMP =
        new Coordinate.DimensionalComparator();

    // Longueur limite pour subdiviser un segment
    // (au-dessous, le segment n'est plus subdivisé, même si le critère de
    // Delaunay n'est pas respecté
    //private double minLength = 0.1;
    
    private Logger log = Logger.getLogger("Triangulation");
    
    public static void main(String[] args) {
        /*
        // case one : triangulate a regular grid
        Coordinate[] tp = new Coordinate[330];
        for (int i = 0 ; i < 110 ; i++) tp[i] = new Coordinate(0, (double)i-10.0,0);
        for (int i = 0 ; i < 110 ; i++) tp[i+110] = new Coordinate(1.0, (double)i-10.0,0);
        for (int i = 0 ; i < 110 ; i++) tp[i+220] = new Coordinate(2.0, (double)i-10.0,0);
        */
        
        
        // case 2 : triangulate a small set of points
        Coordinate[] tp = new Coordinate[]{
        new Coordinate(-889149,747993),
        new Coordinate(-120807,313530),
        new Coordinate(-67521, 844974),
        new Coordinate(-43825, 462779),
        new Coordinate(318773, 267484),
        new Coordinate(447116, -190178),
        new Coordinate(485538, -729207),
        new Coordinate(497882, 563841)};
        
        
        
        // case 3 : triangulate a large set of points
        /*
        int size = 10;
        Coordinate[] tp = new Coordinate[size];
        for (int i = 0 ; i < size ; i++) tp[i] = new Coordinate(Math.random()*1000000.0, Math.random()*1000000.0);
        */
        
        long t0 = System.currentTimeMillis();
        Set<Coordinate> set = new HashSet<Coordinate>(Arrays.asList(tp));
        List<Coordinate> pts = new ArrayList<Coordinate>(set);
        //Collections.sort(pts, COORD2DCOMP);
        long t1 = System.currentTimeMillis();
        Triangulation T = new Triangulation();
        //System.out.println("Sorting time : " + pts.size() + " points " + (t1-t0) + " ms");
        //T.addSortedVertices(pts);
        long t2 = System.currentTimeMillis();
        //System.out.println("Triangulation time : " + pts.size() + " triangulated ordered points " + (t2-t1) + " ms");
        //System.out.println("Total time : " + pts.size() + " triangulated points " + (t2-t0) + " ms");
        //System.out.println("" + T.triangles.size() + " triangles created");
        //for (Triangulation.Triangle tri : T.triangles) System.out.println("   ---" + tri);
        
        
        t0 = System.currentTimeMillis();
        Collections.shuffle(pts);
        t1 = System.currentTimeMillis();
        //System.out.println("Shuffle time : " + pts.size() + " points " + (t1-t0) + " ms");
        T = new Triangulation();
        T.initFirstEdge(pts.get(0), pts.get(1));
        for (int i = 2 ; i < pts.size() ; i++) {T.insert(pts.get(i));}
        t2 = System.currentTimeMillis();
        System.out.println("Triangulation time : " + pts.size() + " triangulated random points " + (t2-t1) + " ms");
    }
    
    //**************************************************************************
    //**************************************************************************
    //*******************          Les constructeurs         *******************
    //**************************************************************************
    //**************************************************************************
    
   /** Constructeur de l'objet Triangulation.
    * @param points tableau des points à trianguler.
    * @param breaklines tableau des segments de contrainte (paires de PointT)
    */
    public DelaunayTriangulationFactory2(Coordinate[] points, /*int[][] breaklines*/Coordinate[] breaklines) {
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
        Set<Coordinate> set = new HashSet<Coordinate>(Arrays.asList(points));
        List<Coordinate> pts = new ArrayList<Coordinate>(set);
        //List<Coordinate> pts = new ArrayList<Coordinate>(Arrays.asList(points));
        Collections.sort(pts, COORD2DCOMP);
        triangulation = new Triangulation();
        triangulation.addSortedVertices(pts);
        //triangulation.initFirstEdge(pts.get(0), pts.get(1));
        //for (int i = 2 ; i < pts.size() ; i++) {triangulation.insert(pts.get(i));}
        
        //Set hs = new TreeSet();
        //this.pts = points;
        //this.breaklines = breaklines;
        //this.triangles = new ArrayList<Triangle>();
        
        // Les points sont ordonnés et les doublons éliminés
        //for (int i = 0 ; i < points.length ; i++) {
        //  hs.add(new PointT(i));
        //}
        //this.pts_i = (PointT[])hs.toArray(new PointT[]{});
        long t1 = System.currentTimeMillis();
        System.out.println("   " + pts.size() + " points triangulés en " + (t1-t0) + " ms");
        triangulation.addBreakLines(breaklines);
        long t2 = System.currentTimeMillis();
        System.out.println("   " + (breaklines.length/2) + " contraintes ajoutées en " + (t2-t1) + " ms");
    }
    
   /**
    * Return the triangulated points, i.e.
    * <ul>
    * <li>the point array used at construction time</li>
    * <li>minus points equals to each other</li>
    * <li>plus the points introduced to keep the delaunay property while adding
    * breaklines.</li>
    * <ul>
    */
    /*
    public Coordinate[] getUniqueTriangulatedPoints() {
        Coordinate[] coordinates = new Coordinate[pts_i.length];
        for (int i = 0 ; i < pts_i.length ; i++) {
            coordinates[i] = pts[pts_i[i].i];
        }
        return coordinates;
    }
    */
    
    /*
    public Triangle[] getTriangles() {
        return triangles.toArray(new Triangle[triangles.size()]);
    }
    */


    /*private void init() {
        assert (triangulation.pts.length>2) : "Cannot triangulate a set of less than 3 points";
        // Initialise le premier triangle (le plus à gauche)
        //Triangle t = new Triangle(pts_i[0], pts_i[1], pts_i[2]);
        Triangle t = new Triangle(pts_i[0], pts_i[1], HORIZON);
        t0 = new Triangle(pts_i[1], pts_i[0], HORIZON);
        t.ttt[0] = t0;
        t.ttt[1] = t0;
        t.ttt[2] = t0;
        t0.ttt[0] = t;
        t0.ttt[1] = t;
        t0.ttt[2] = t;
        triangles.add(t);
        triangles.add(t0);
        currentT = t;
        log.fine("Creation of the first concrete triangle and 3 exterior triangles");
    }*/

   /**
    * Insérer un point dans la triangulation
    * TODO : vérifier si la méthode marche uniquement pour des points ajoutés à
    * droite ou si elle est valable pour l'ajout de n'importe quel point situé
    * à l'exterieur de l'enveloppe convexe.
    * @param p point à inserer dans la triangulation.
    */
    /*
    public void addExteriorPoint(Coordinate c) {
        log.fine("Insertion du point " + c);
        //System.out.println("   Insertion du point " + p + " (" + pts[p.i] + ")");
        // Find exterior triangles which 0-1 segment is visible from p
        List<Triangle> newTriangles = addPointOnRight(p);
        // Apply Delaunay creteria on new triangles
        for (int i = 0, max = newTriangles.size() ; i < max ; i++) {
            depth = 0;
            Triangle t = newTriangles.get(i);
            if (t.property==-1 || t.ppp[2] == HORIZON) continue;
            delaunay(t, null);
        }
    }
    */
    
   /** Recherche les points de l'enveloppe convexe visibles du point p
    * et s'appuie dessus pour créer de nouveaux triangles.
    * @param p point de vue
    * @return liste des nouveaux triangles (sans les triangles extérieurs)
    */
    /*
    public List<Triangle> createTrianglesFromExteriorPointToConvexHull(Coordinate c) {
        Triangle[] boundingT = outerTriangles(p);
        List<Triangle> list = new ArrayList<Triangle>();
        for (Triangle t = boundingT[1] ; t != boundingT[3] && t!= null ; t = t.ttt[2]) {
            // Change le triangle exterieur t par un triangle s'appuyant sur p
            t.ppp[2] = p;
            //System.out.println("nouveau triangle " + t);
            list.add(t);
        }
        Triangle tOut1 = new Triangle(p,boundingT[0].ppp[0],HORIZON);
        lierC(tOut1, 1, boundingT[0]);
        if (boundingT[1]!=null) lierC(tOut1, 0, boundingT[1]); // en fait, boundingT1 est devenu un triangle normal
        //log.finer("      nouveau tOut1 = " + tOut1.toStringAll());
        
        Triangle tOut2 = new Triangle(boundingT[3].ppp[1], p, HORIZON);
        lierC(tOut2, 2, boundingT[3]);
        if (boundingT[2]!=null) lierC(tOut2, 0, boundingT[2]);
        //log.finer("      nouveau tOut2 = " + tOut2.toStringAll());
        
        lierC(tOut1, 2, tOut2);
        if (boundingT[1]==null && boundingT[2]==null) lierC(tOut1,0,tOut2);
        //System.out.println("  tOut1 : " + tOut1.toStringAll());
        //System.out.println("  tOut2 : " + tOut2.toStringAll());
        triangles.add(tOut1);
        triangles.add(tOut2);
        
        t0 = tOut1; // pour s'assurer que t0 est toujour un triangle exterieur
        return list;
    }
    */
    
    /** Step throw every exterior triangles (a,b,HORIZON) in a ccw to find those
    * having their a,b segment visible from p.
    * @return the Triangles using the segment before the first visible segment,
    * the first visible segment, the last visible segment and the segment after
    * the last visble segment.Trexterior Triangle and the first invisible outerTriangle
    * while looking through outer triangles in a ccw
    */
    /*
    Triangle[] outerTriangles(PointT p) {
        Triangle currentT = t0;
        PointT start = currentT.ppp[0];
        Triangle nextT = null;
        //log.info("   liste des points formant l'enveloppe");
        //StringBuffer sb = new StringBuffer();
        //sb.append(""+t0.ppp[1] + "/");
        int currentTccw = ccw(pts[currentT.ppp[0].i].x,
                              pts[currentT.ppp[0].i].y,
                              pts[currentT.ppp[1].i].x,
                              pts[currentT.ppp[1].i].y,
                              pts[p.i].x,
                              pts[p.i].y);
        boolean currentTVisible = currentTccw > 0;
        Triangle beforeFirstVisibleExtT=null;
        Triangle firstVisibleExtT=null;
        Triangle lastVisibleExtT=null;
        Triangle afterLastVisibleExtT=null;
        while (true) {
            nextT = currentT.ttt[2];
            //sb.append(""+nextT.ppp[1] + "/");
            int nextTccw = ccw(pts[nextT.ppp[0].i].x, pts[nextT.ppp[0].i].y,
                    pts[nextT.ppp[1].i].x, pts[nextT.ppp[1].i].y,
                    pts[p.i].x, pts[p.i].y);
            boolean nextTVisible = nextTccw > 0;
            if (!currentTVisible && nextTVisible) {
                beforeFirstVisibleExtT = currentT;
                firstVisibleExtT = nextT;
            }
            if (currentTVisible && !nextTVisible) {
                lastVisibleExtT = currentT;
                afterLastVisibleExtT = nextT;
            }
            if (firstVisibleExtT!=null && lastVisibleExtT!=null) {
                return new Triangle[]{beforeFirstVisibleExtT, firstVisibleExtT,
                                      lastVisibleExtT, afterLastVisibleExtT};
            }
            if (currentTccw == 0 && nextTccw == 0 && currentT.ppp[0]==nextT.ppp[1]) {
                return new Triangle[]{currentT, null, null, nextT};
            }
            currentT = nextT;
            currentTccw = nextTccw;
            currentTVisible = nextTVisible;
        }
    }
    */
    
   /** 
    * Check the delaunay property of this triangle. If the circumcircle contains
    * one of the opposite vertex, the two triangles forming the quadrilatera are
    * flipped. The method is iterative.
    * @param t triangle to check and to modify (if needed)
    * @return true if a flip occured during the delaunay property check
    */
    /*
    private void delaunay (Triangle t, Triangle previous) {
        //if (depth>maxDepth) {return;}
        Triangle curr = t.clone();
        Triangle prev = previous==null?null:previous.clone();
        // Pour chaque coté du triangle
        // System.out.println("   enter delaunay procedure for " + t);
        for (int cote = 0 ; cote < 3 ; cote++) {
            Triangle opp = t.ttt[cote];
            //System.out.println("      with " + opp);
            if (opp.ppp[2] == HORIZON) continue; // pas de flip avec des triangles exterieurs
            // Récupérer le point opposé
            int i = t.getOpposite(cote);
            // si cote est un segment de contrainte, passer au cote suivant
            int prop = cote==0?1:cote==1?2:4;
            if ((t.property & prop) == prop) continue;
            
            // S'il existe et est situé dans le cercle circonscrit
            if (i!=-1 && fastInCircle(t.ppp[0],t.ppp[1],t.ppp[2],opp.ppp[i])>0) {
                PointT p = opp.ppp[i];
                // Les 2 triangles sont flippés;
                
                // Recyclage des anciens triangles t et t.ttt[cote]
                // pour éviter la création et la suppression d'objets inutiles
                // Sommets des 2 nouveaux triangles
                PointT v10 = p;
                PointT v11 = t.ppp[(cote+2)%3];
                PointT v12 = t.ppp[cote];
                PointT v20 = p;
                PointT v21 = t.ppp[(cote+1)%3];
                PointT v22 = t.ppp[(cote+2)%3];
                //Voisins des 2 nouveaux triangles
                Triangle t11 = t.ttt[(cote+2)%3];
                Triangle t12 = opp.ttt[(i+2)%3];
                int property1 = (t.getConstraint((cote+2)%3)?2:0) + (opp.getConstraint((i+2)%3)?4:0);
                Triangle t20 = opp.ttt[i];
                Triangle t21 = t.ttt[(cote+1)%3];
                int property2 = (opp.getConstraint(i)?1:0) + (t.getConstraint((cote+1)%3)?2:0);
                
                t.ppp[0] = v10;
                t.ppp[1] = v11;
                t.ppp[2] = v12;
                t.ttt[0] = opp;
                lierC(t,1,t11);
                lierC(t,2,t12);
                t.property = property1;
                opp.ppp[0] = v20;
                opp.ppp[1] = v21;
                opp.ppp[2] = v22;
                lierC(opp,0,t20);
                lierC(opp,1,t21);
                opp.ttt[2] = t;
                opp.property = property2;
                depth++;
                if (!t.equals(prev)) delaunay(t,curr);
                if (!opp.equals(prev)) delaunay(opp, curr);
                break;
            }
            else;
        }
    }
    */

  /**
    * Return a positive value if the point p4 lies inside the
    * circle passing through pa, pb, and pc; a negative value if
    * it lies outside; and zero if the four points are cocircular.
    * The points pa, pb, and pc must be in counterclockwise
    * order, or the sign of the result will be reversed.
    */
    /*
    private double fastInCircle(PointT p1, PointT p2, PointT p3, PointT p4) {
        double adx, ady, bdx, bdy, cdx, cdy;
        double abdet, bcdet, cadet;
        double alift, blift, clift;

        adx = pts[p1.i].x-pts[p4.i].x;
        ady = pts[p1.i].y-pts[p4.i].y;
        bdx = pts[p2.i].x-pts[p4.i].x;
        bdy = pts[p2.i].y-pts[p4.i].y;
        cdx = pts[p3.i].x-pts[p4.i].x;
        cdy = pts[p3.i].y-pts[p4.i].y;

        abdet = adx * bdy - bdx * ady;
        bcdet = bdx * cdy - cdx * bdy;
        cadet = cdx * ady - adx * cdy;
        alift = adx * adx + ady * ady;
        blift = bdx * bdx + bdy * bdy;
        clift = cdx * cdx + cdy * cdy;

        return alift * bcdet + blift * cadet + clift * abdet;
    }
    */


   /**
    *Cette fonction permet de déterminer si le triangle p0-p1-p2
    * tourne dans le sens des aiguilles d'une montre (renvoie -1),
    * ou dans le sens inverse (renvoie 1).
    * La fonction renvoie 0 si le triangle est plat.*/
    /*
    public static int ccw (double p0x, double p0y, double p1x, double p1y,
                            double p2x, double p2y) {
        double dx1 = p1x - p0x;
        double dy1 = p1y - p0y;
        double dx2 = p2x - p0x;
        double dy2 = p2y - p0y;
        if (dx1 * dy2 > dy1 * dx2) return 1;
        else if (dx1 * dy2 < dy1 * dx2) return -1;
        else {
          if (dx1 * dx2 < 0 || dy1 * dy2 < 0) return -1;
          else if (dx1*dx1 + dy1*dy1 >= dx2*dx2 + dy2*dy2) return 0;
          else return 1;
        }
    }
    */

    /** lier 2 triangles.*/
    /*
    private boolean lier (Triangle T1, Triangle T2) {
        try {
            if (T1.ppp[0].i==T2.ppp[0].i && T1.ppp[1].i==T2.ppp[2].i) {
                T1.ttt[0] = T2; T2.ttt[2] = T1; return true;
            }
            else if (T1.ppp[0].i==T2.ppp[2].i && T1.ppp[1].i==T2.ppp[1].i) {
                T1.ttt[0] = T2; T2.ttt[1] = T1; return true;
            }
            else if (T1.ppp[0].i==T2.ppp[1].i && T1.ppp[1].i==T2.ppp[0].i) {
                T1.ttt[0] = T2; T2.ttt[0] = T1; return true;
            }
            else if (T1.ppp[1].i==T2.ppp[0].i && T1.ppp[2].i==T2.ppp[2].i) {
                T1.ttt[1] = T2; T2.ttt[2] = T1; return true;
            }
            else if (T1.ppp[1].i==T2.ppp[2].i && T1.ppp[2].i==T2.ppp[1].i) {
                T1.ttt[1] = T2; T2.ttt[1] = T1; return true;
            }
            else if (T1.ppp[1].i==T2.ppp[1].i && T1.ppp[2].i==T2.ppp[0].i) {
                T1.ttt[1] = T2; T2.ttt[0] = T1; return true;
            }
            else if (T1.ppp[2].i==T2.ppp[0].i && T1.ppp[0].i==T2.ppp[2].i) {
                T1.ttt[2] = T2; T2.ttt[2] = T1; return true;
            }
            else if (T1.ppp[2].i==T2.ppp[2].i && T1.ppp[0].i==T2.ppp[1].i) {
                T1.ttt[2] = T2; T2.ttt[1] = T1; return true;
            }
            else if (T1.ppp[2].i==T2.ppp[1].i && T1.ppp[0].i==T2.ppp[0].i) {
                T1.ttt[2] = T2; T2.ttt[0] = T1; return true;
            }
            else {return false;}
        }
        catch(NullPointerException npe) {
            return false;
        }
    }
    */


    /** lier les triangles T1 et T2 adjacents à T1 par son coté c.*/
    /*
    private boolean lierC (Triangle T1, int c, Triangle T2) {
        //if (T1==null || T2==null) return false;
        try {
            int c_prop = c==0?1:c==1?2:4;
            // Le coté c de T1 est égal au coté 2 de T2
            if (T1.ppp[c].i==T2.ppp[0].i) {
                // si le coté 2 de T2 est un segment contraint, la contrainte est ajoutée à T1
                if ((T2.property & 4) == 4 && (T1.property & c_prop) != c_prop) T1.property += c_prop;
                T1.ttt[c] = T2; T2.ttt[2] = T1; return true;
            }
            // Le coté c de T1 est égal au coté 1 de T2
            else if (T1.ppp[c].i==T2.ppp[2].i) {
                // si le coté 1 de T2 est un segment contraint, la contrainte est ajoutée à T1
                if ((T2.property & 2) == 2 && (T1.property & c_prop) != c_prop) T1.property += c_prop;
                T1.ttt[c] = T2; T2.ttt[1] = T1; return true;
            }
            // Le coté c de T1 est égal au coté 0 de T2
            else if (T1.ppp[c].i==T2.ppp[1].i) {
                // si le coté 0 de T2 est un segment contraint, la contrainte est ajoutée à T1
                if ((T2.property & 1) == 1 && (T1.property & c_prop) != c_prop) T1.property += c_prop;
                T1.ttt[c] = T2; T2.ttt[0] = T1; return true;
            }
            else {return false;}
        }
        catch(NullPointerException npe) {
            log.severe("NullPointerException dans la méthode lierC");
            return false;
        }
    }
    */

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
    /*
    public void insert(Triangle tIni, Coordinate p) {
        Triangle t = locate(tIni, p);
        // Le point p est situé en dehors de l'enveloppe
        if (t.ppp[2] == HORIZON) {
            Coordinate[] ptsTemp = new Coordinate[pts.length+1];
            System.arraycopy(pts, 0, ptsTemp, 0, pts.length);
            this.pts = ptsTemp; ptsTemp = null;
            PointT[] pts_iTemp = new PointT[pts_i.length+1];
            System.arraycopy(pts_i, 0, pts_iTemp, 0, pts_i.length);
            pts_i = pts_iTemp; pts_iTemp = null;
            pts[pts.length-1] = p;
            pts_i[pts_i.length-1] = new PointT(pts.length-1);
            // ATTENTION, insert(pts_i) est normalement réservé aux points
            // rajoutés à droite de la triangulation
            // VERIFIER qu'il est appliquable dans ce contexte
            insert(pts_i[pts_i.length-1]);
            return;
        }
        // Le point p est situé à l'intérieur de l'enveloppe
            double ccw0 = ccw(p.x, p.y,
                pts[t.ppp[0].i].x, pts[t.ppp[0].i].y,
                pts[t.ppp[1].i].x, pts[t.ppp[1].i].y);
            double ccw1 = ccw(p.x, p.y,
                pts[t.ppp[1].i].x, pts[t.ppp[1].i].y,
                pts[t.ppp[2].i].x, pts[t.ppp[2].i].y);
            double ccw2 = ccw(p.x, p.y,
                pts[t.ppp[2].i].x, pts[t.ppp[2].i].y,
                pts[t.ppp[0].i].x, pts[t.ppp[0].i].y);
        // if p is strictly inside t, every ccw must be > 0
        if (ccw0<=0 || ccw1 <=0 || ccw2 <=0) return;
        //if (t.ppp[2].i==-1) return;
        // if p equals to a point of the triangle, return
        if (pts[t.ppp[0].i].x==p.x && pts[t.ppp[0].i].y==p.y) return;
        if (pts[t.ppp[1].i].x==p.x && pts[t.ppp[1].i].y==p.y) return;
        if (pts[t.ppp[2].i].x==p.x && pts[t.ppp[2].i].y==p.y) return;
        if (pts[t.ppp[0].i].x==p.x && pts[t.ppp[0].i].y==p.y) return;
        if (pts[t.ppp[1].i].x==p.x && pts[t.ppp[1].i].y==p.y) return;
        if (pts[t.ppp[2].i].x==p.x && pts[t.ppp[2].i].y==p.y) return;
        if (pts[t.ppp[0].i].x==p.x && pts[t.ppp[0].i].y==p.y) return;
        if (pts[t.ppp[1].i].x==p.x && pts[t.ppp[1].i].y==p.y) return;
        if (pts[t.ppp[2].i].x==p.x && pts[t.ppp[2].i].y==p.y) return;
        Coordinate[] ptsTemp = new Coordinate[pts.length+1];
        System.arraycopy(pts, 0, ptsTemp, 0, pts.length);
        this.pts = ptsTemp; ptsTemp = null;
        PointT[] pts_iTemp = new PointT[pts_i.length+1];
        System.arraycopy(pts_i, 0, pts_iTemp, 0, pts_i.length);
        pts_i = pts_iTemp; pts_iTemp = null;
        pts[pts.length-1] = p;
        pts_i[pts_i.length-1] = new PointT(pts.length-1);
        // Create 3 new triangles from p to t vertices
        Triangle tn0 = new Triangle(t.ppp[0], t.ppp[1], pts_i[pts_i.length-1]);
        Triangle tn1 = new Triangle(t.ppp[1], t.ppp[2], pts_i[pts_i.length-1]);
        Triangle tn2 = new Triangle(t.ppp[2], t.ppp[0], pts_i[pts_i.length-1]);
        lierC(tn0, 0, t.ttt[0]);
        lierC(tn1, 0, t.ttt[1]);
        lierC(tn2, 0, t.ttt[2]);
        tn0.ttt[1] = tn1; tn1.ttt[2] = tn0;
        tn1.ttt[1] = tn2; tn2.ttt[2] = tn1;
        tn2.ttt[1] = tn0; tn0.ttt[2] = tn2;
        // instead of deleting t and adding 3 new triangles,
        // reuse t and add two triangles to the list
        //t.property = -1; delT++;
        t.ppp = tn0.ppp;
        t.ttt = tn0.ttt;
        t.property = tn0.property;
        //triangles.add(tn0);
        triangles.add(tn1);
        triangles.add(tn2);
        depth = 0;
        delaunay(tn0,null);
        depth = 0;
        delaunay(tn1,null);
        depth = 0;
        delaunay(tn2,null);
    }
    */

   /**
    * Test if Fonction booleenne renvoyant vrai s'il existe déjà une arete
    * de triangle entre le point p1 appartenant au triangle t1 et
    * le point p2.
    * Cette fonction est utilisée comme condition d'arrêt lors de la
    * subdivision des segments de contrainte.
    * @param p1 premier point
    * @param t1 un triangle dont p1 constitue un sommet.
    * @param p2 point dont on veut savoir s'il est connecté à p1.
    * @return un Triangle reliant p1 et p2 ou null sinon
    */
    /*
    private Triangle isLinked(PointT p1, Triangle t1, PointT p2) {
        int pos = 0;
        if (p1 == t1.ppp[0]) pos = 0;
        else if (p1 == t1.ppp[1]) pos = 1;
        else if (p1 == t1.ppp[2]) pos = 2;
        else return null;
        if (p2==t1.ppp[(pos+1)%3]) return t1;
        if (p2==t1.ppp[(pos+2)%3]) return t1;
        int indice = t1.ppp[(pos+1)%3].i;
        Triangle t2 = t1.ttt[(pos+2)%3];
        while (true) {
            if (p1 == t2.ppp[0]) pos = 0;
            else if (p1 == t2.ppp[1]) pos = 1;
            else if (p1 == t2.ppp[2]) pos = 2;
            else return null;
            if (p2==t2.ppp[(pos+1)%3]) return t2;
            if (p2==t2.ppp[(pos+2)%3]) return t2;
            if (t2.ppp[(pos+1)%3].i == indice) break;
            t2 = t2.ttt[(pos+2)%3];
        }
        return null;
    }
    */

  /** Ajouter une contrainte sur le segment p1-p2.*/
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

  /** Localise le triangle contenant le point p.
    * @param tIni un triangle quelconque à partir duquel
    * va s'effectuer la localisation.
    * @param p point à localiser.
    * @return un triangle contenant p (inclusion stricte ou limite.
    * Retourne null si p est à l'exterieur de l'enveloppe convexe
    */
    /*
    public Triangle locate(Triangle tIni, Coordinate p) {
        Triangle t = tIni;
        Triangle[] lastTriangles = new Triangle[3];
        lastTriangles[0] = tIni;
        // S'il s'agit d'un triangle périphérique (ppp[2]=-1)
        // partir d'un triangle adjacent non périphérique
        if (t.ppp[2].i==-1) t = t.ttt[0];
        int loop = 0;
        while (t.ppp[2].i!=-1) {
            int next = nextTriangle(t, p);
            if (next<0) {break;}
            else {
              t = t.ttt[next];
              lastTriangles[loop%3] = t;
              if (t.ppp[2].i==-1) {
                  //log.info("locate " + p.toString() + " : EXTERIEUR");
                  return t;
              }
            }
            if (++loop%100==0 && lastTriangles[0]!=null && lastTriangles[1]!=null && lastTriangles[2]!=null) {
                if (lastTriangles[2].equals(lastTriangles[1]) ||
                    lastTriangles[2].equals(lastTriangles[0]) ) {
                    log.warning("Break the infinite loop to : " + p.toString());
                    break;
                }
            }
        }
        return t;
    }
    */
    
   /** localise le triangle contenant le point p.*/
    /*
    public PointT locateP(Triangle tIni, Coordinate p) {
        int loop = 0;
        Triangle t = tIni;
        Triangle[] lastTriangles = new Triangle[3];
        lastTriangles[0] = t;
        if (t.ppp[2].i==-1) t = t.ttt[0];
        while (t.ppp[2].i!=-1) {
            int next = nextTriangle(t, p);
            if (next == -111) return t.ppp[0];
            else if (next == -222) return t.ppp[1];
            else if (next == -333) return t.ppp[2];
            else if (next == -11) return null;
            else if (next == -22) return null;
            else if (next == -33) return null;
            else if (next == -1) return null;
            else {
                t = t.ttt[next];
                lastTriangles[loop%3] = t;
            }
            loop++;
            if (loop%100==0 && lastTriangles[0]!=null && lastTriangles[1]!=null && lastTriangles[2]!=null) {
                if (lastTriangles[2].equals(lastTriangles[1]) ||
                    lastTriangles[2].equals(lastTriangles[0]) || (loop>10000)) {
                    System.out.println("Recherche de p = " + p.toString());
                    System.out.println("Triangle0 = " + lastTriangles[0].toStringAll());
                    System.out.println("Triangle1 = " + lastTriangles[1].toStringAll());
                    System.out.println("Triangle2 = " + lastTriangles[2].toStringAll());
                    log.warning("Break the infinite loop to : " + p.toString());
                    break;
                }
            }
        }
        return null;
    }
    */
    
    /** Trouve le triangle adjacent à t dans la direction de p.
      * @param t triangle de départ
      * @param p point indiquant la direction
      * @return un entier donnant l'information suivante
      *         -111, -222, -333 : point p sur un sommet de t
      *          -11,  -22,  -33 : point p sur un coté de t
      *           -1 : point p à l'interieur
      *            0, 1 ou 2 : coté du triangle suivant
      */
    /*
    public int nextTriangle(Triangle t, Coordinate p) {
        if (pts[t.ppp[0].i].equals2D(p)) return -111;
        else if (pts[t.ppp[1].i].equals2D(p)) return -222;
        else if (pts[t.ppp[2].i].equals2D(p)) return -333;
        int ccw0 = ccw(pts[t.ppp[0].i].x, pts[t.ppp[0].i].y,
                       pts[t.ppp[1].i].x, pts[t.ppp[1].i].y,
                       p.x, p.y);
        if (ccw0 < 0) return 0;
        else if (ccw0==0) return -11;
        int ccw1 = ccw(pts[t.ppp[1].i].x, pts[t.ppp[1].i].y,
                       pts[t.ppp[2].i].x, pts[t.ppp[2].i].y,
                       p.x, p.y);
        if (ccw1 < 0) return 1;
        else if (ccw1==0) return -22;
        int ccw2 = ccw(pts[t.ppp[2].i].x, pts[t.ppp[2].i].y,
                       pts[t.ppp[0].i].x, pts[t.ppp[0].i].y,
                       p.x, p.y);
        if (ccw2 < 0) return 2;
        else if (ccw2==0) return -33;
        // ccw0>0 && ccw1>0 && ccw2>0 ==> p strictement à l'interieur
        else return -1;
    }
    */
    
    /**
     * Return triangulated points 3 by 3 in order to make it easy to create
     * the jts corresponding triangles.
     */
    public Coordinate[] getTriangulatedPoints() {
        return triangulation.getTriangulatedPoints();
      /*List nouveau = new ArrayList();
      for (int i = 0 ; i < triangles.size() ; i++) {
          Triangle t = (Triangle)triangles.get(i);
          if (null!=t && t.property!=-1 && t.ppp[2]!=HORIZON) {
              nouveau.add(pts[t.ppp[0].i]);
              nouveau.add(pts[t.ppp[1].i]);
              nouveau.add(pts[t.ppp[2].i]);
          }
      }
      return (Coordinate[]) nouveau.toArray(new Coordinate[]{});
      */
    }
    
    public String toString() {
        return "non implémenté";
    }
    
   /**
    * A PointT just contains the index of a coordinate in the points array
    */
    /*
    public class PointT implements Comparable {
    
        public int i = 0 ;         //indice dans le tableau de point

        public PointT(int i) {
            this.i = i;
        }

        public int compareTo(Object o) {
            if (o instanceof PointT && i>=0 && ((PointT)o).i>=0) {
                int oi = ((PointT)o).i;
                if (pts[oi].x < pts[i].x) return 1;
                else if (pts[oi].x > pts[i].x) return -1;
                else {
                    if (pts[oi].y < pts[i].y) return 1;
                    else if (pts[oi].y > pts[i].y) return -1;
                    else return 0;
                }
            }
            else return -1;
        }

        public boolean equals(Object obj) {
            if (obj instanceof PointT) {
                PointT p = (PointT)obj;
                return (pts[i].x==pts[p.i].x && pts[i].y==pts[p.i].y);
            }
            else return false;
        }
    
        public int hashCode() {
            return (new Double(pts[i].x)).hashCode() +
                    (new Double(pts[i].y)).hashCode();
        }
    
        public String toString(){return "" + i;}
    
    }
    */
    
    /**
    * Classe Triangle définissant un triangle et ses voisins.
    * Un Triangle est composé :
    * - d'un tableau de 3 PointT (désignant des Points)
    * Les trois PointT, d'indice 0,1,2 tournent dans le sens trigo (ccw)
    * - d'un tableau de 3 références vers les triangles voisins
    * Le triangle voisin ttt[0] partage le segment ppp[0]-ppp[1]
    * - une propriété permettant de mémoriser les cotés représentant des
    * contraintes
    *               
    *         _ _ _t.ppp[2]_ _ 
    *         \      /\      /
    *      ttt[0]   /  \    ttt[2]
    *           \  / t  \  /
    *   t.ppp[0] \/______\/ t.ppp[1]
    *             \      /
    *              ttt[1]
    *               \  /
    *                \/
    */
    /*
    public class Triangle {
        // points d'angle dans le sens trigo (anti-horaire)
        public PointT[] ppp = new PointT[3];
        // triangles voisins (T1 à droite de p[0]-p[1])
        Triangle[] ttt = new Triangle[3];
        // indique si le triangle est valide
        // boolean valide = true;
        // Propriété du triangle (remplace et enrichie le booleen valide)
        int property = 0;
        // property = -1 : obsolète (correspond à valide = false)
        // property = 0 : normal (triangle actif sujet à modification)
        // property = 1 : le coté 0 est un segment de contrainte
        // property = 2 : le coté 1 est un segment de contrainte
        // property = 4 : le coté 2 est un segment de contrainte
        // remarque : à enrichir avec des notions de frontières
        // exterieures et interieures

        Triangle(PointT p0, PointT p1, PointT p2) {
            if (p2 == HORIZON || ccw(pts[p0.i].x, pts[p0.i].y,
                                     pts[p1.i].x, pts[p1.i].y,
                                     pts[p2.i].x, pts[p2.i].y) >= 0) {
                this.ppp[0] = p0;
                this.ppp[1] = p1;
                this.ppp[2] = p2;
            }
            else {
                this.ppp[0] = p0;
                this.ppp[2] = p1;
                this.ppp[1] = p2;
            }
        }


        public int getOpposite(int cote) {
            // Test si i est valide et non nul
            try {
                if (ttt[cote].ppp[0] == ppp[cote]) return 1;
                else if (ttt[cote].ppp[1] == ppp[cote]) return 2;
                else if (ttt[cote].ppp[2] == ppp[cote]) return 0;
                else return -1;
            }
            catch(NullPointerException npe) {
                log.severe("NullPointerException dans le triangle " + this.toStringAll());
                return -1;
            }
        }

        public void setConstraint(int cote) {
            if (cote==0 && ((property & 1) != 1)) property += 1;
            else if (cote==1 && ((property & 2) != 2)) property += 2;
            else if (cote==2 && ((property & 4) != 4)) property += 4;
            else;
            int coteOpp = (getOpposite(cote)+1)%3;
            if (coteOpp==0 && ((ttt[cote].property & 1) != 1))
                ttt[cote].property += 1;
            else if (coteOpp==1 && ((ttt[cote].property & 2) != 2))
                ttt[cote].property += 2;
            else if (coteOpp==2 && ((ttt[cote].property & 4) != 4))
                ttt[cote].property += 4;
            else;
        }


        public boolean getConstraint(int cote) {
            if (cote==0 && (property & 1)==1) return true;
            else if (cote==1 && (property & 2)==2) return true;
            else if (cote==2 && (property & 4)==4) return true;
            else return false;
        }

        public boolean isValid() {
            if (ppp == null || ppp[0]==null || ppp[1]==null || ppp[2]==null) {
                return false;
            }
            else if (ttt == null || ttt[0]==null || ttt[1]==null || ttt[2]==null) {
                return false;
            }
            else if (property == -1) return false;
            return true;
        }

        public String toString() {
            StringBuffer sb = new StringBuffer("Triangle ");
            if (ppp!=null && ppp[0]!=null) sb.append(ppp[0].i + "-");
            else sb.append("null-");
            if (ppp!=null && ppp[1]!=null) sb.append(ppp[1].i + "-");
            else sb.append("null-");
            if (ppp!=null && ppp[2]!=null) sb.append(ppp[2].i);
            else sb.append("null");
            return sb.toString();
        }
        

        public String toStringAll() {
            StringBuffer sb = new StringBuffer(this.toString() + "\n");
            sb.append("   (voisins : ");
            if (ttt!=null && ttt[0]!=null) sb.append(ttt[0].toString());
            sb.append(" - ");
            if (ttt!=null && ttt[1]!=null) sb.append(ttt[1].toString());
            sb.append(" - ");
            if (ttt!=null && ttt[2]!=null) sb.append(ttt[2].toString());
            sb.append(")");
            return sb.toString();
        }

        public Triangle clone() {
            Triangle clone = new Triangle(ppp[0], ppp[1], ppp[2]);
            clone.ttt = this.ttt;
            clone.property = this.property;
            return clone;
        }
        

        public boolean equals(Triangle t) {
            if (t == null) return false;
            return (ppp[0]==t.ppp[0] && ppp[1]==t.ppp[1] && ppp[2]==t.ppp[2])
            || (ppp[0]==t.ppp[1] && ppp[1]==t.ppp[2] && ppp[2]==t.ppp[0])
            || (ppp[0]==t.ppp[2] && ppp[1]==t.ppp[0] && ppp[2]==t.ppp[1]);
        }
    }
    */

}

