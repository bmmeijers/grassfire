package fr.michaelm.jump.plugin.triangulation;

import java.util.*;
import java.awt.Color;

//import com.vividsolutions.jump.workbench.plugin.AbstractPlugIn;
import com.vividsolutions.jump.workbench.plugin.ThreadedBasePlugIn;
import com.vividsolutions.jump.task.TaskMonitor;
import com.vividsolutions.jump.workbench.plugin.PlugInContext;
import com.vividsolutions.jump.workbench.model.LayerManager;
import com.vividsolutions.jump.workbench.model.Layer;
import com.vividsolutions.jump.workbench.ui.SelectionManager;
import com.vividsolutions.jump.feature.*;
import com.vividsolutions.jts.geom.*;
//import com.vividsolutions.jump.workbench.ui.renderer.style.BasicStyle;
import fr.michaelm.geom.DelaunayTriangulationFactory;
import fr.michaelm.geom.DelaunayTriangulationFactory2;

/**
* Triangulation plugin
* @author micha&euml;l michaud
* @version 0.4
*/
// version 0.4 : can now triangulate points with z=NaN
public class TriangulationPlugIn extends ThreadedBasePlugIn {
    private FeatureSchema TRIANGULATION_SCHEMA;
    private GeometryFactory factory;
    
    public void initialize(PlugInContext context) throws Exception {
        context.getFeatureInstaller().addMainMenuItem(this,
                                                      new String[] { "3D-Tools", "Triangulation (v0.4)" },
                                                      getName(), false,
                                                      null, null);
        factory = new GeometryFactory();
        TRIANGULATION_SCHEMA = new FeatureSchema();
        TRIANGULATION_SCHEMA.addAttribute("Geometry", AttributeType.GEOMETRY);
        TRIANGULATION_SCHEMA.addAttribute("Num�ro", AttributeType.INTEGER);
    }
                                                      
    public boolean execute(PlugInContext context) throws Exception {
        /*
        SelectionManager sm = context.getWorkbenchContext().getLayerViewPanel().getSelectionManager();
        LayerManager layerManager = context.getLayerManager();
        Collection layersWithSelectedItems = sm.getLayersWithSelectedItems();
        Iterator itLayers = layersWithSelectedItems.iterator();
        java.util.List shapes = new ArrayList();
        Coordinate c = null;
        while (itLayers.hasNext()) {
            Layer currentLayer = (Layer)itLayers.next();
            //shapes.add(sm.getFeaturesWithSelectedItems(currentLayer));
            Collection selectedFeatures = sm.getFeaturesWithSelectedItems(currentLayer);
            Iterator it = selectedFeatures.iterator();
            while (it.hasNext()) {
                BasicFeature feature = (BasicFeature)it.next();
                shapes.add(feature.getGeometry());
            }
        }
        
        List points = new ArrayList();
        List breakLineList = new ArrayList();
        int index = 0;
        for (int i = 0 , nb = shapes.size() ; i < nb ; i++) {
            Geometry g = (Geometry)shapes.get(i);
            if (g instanceof Point && !Double.isNaN(g.getCoordinate().z)) {
                points.add(g.getCoordinate());
                index++;
            }
            else if (g instanceof LineString) {
                LineString ls = (LineString)g;
                int[] breakLine = new int[ls.getNumPoints()];
                for (int j = 0, n = ls.getNumPoints() ; j < n ; j++) {
                    c = g.getCoordinates()[j];
                    if (Double.isNaN(c.z)) {
                        // La breakline est interrompue si elle comporte
                        // un point d'altitude inconnue. Une copie partielle
                        // du tableau est r�alis�e
                        System.arraycopy((Object)breakLine, 0, (Object)breakLine, 0, j);
                        break;
                    }
                    else {
                        points.add(g.getCoordinates()[j]);
                        breakLine[j] = index++;
                    }
                }
                breakLineList.add(breakLine);
            }
            else {}
        }
        Coordinate[] cc = (Coordinate[])points.toArray(new Coordinate[0]);
        if (cc.length==0) return false;
        int[][] breakLines = (int[][])breakLineList.toArray(new int[][]{});
        Triangulation triangulation = new Triangulation(cc, breakLines);
        triangulation.trianguler();
        cc = triangulation.getTriangulatedPoints();
        FeatureCollection fc = new FeatureDataset(TRIANGULATION_SCHEMA);
        for (int i = 0 ; i < cc.length ; i+=3) {
            Feature feature = new BasicFeature(TRIANGULATION_SCHEMA);
            Coordinate[] triangle = new Coordinate[]{cc[i], cc[i+1], cc[i+2], cc[i]};
            factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]);
            feature.setGeometry(factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]));
            feature.setAttribute("Num�ro", new Integer(i/3));
            fc.add(feature);
        }
        Layer layer = createNewTriangulationLayer(context);
        layer.setFeatureCollection(fc);
        */
        return true;
    }
    
    public void run(TaskMonitor monitor, PlugInContext context)
                                                    throws java.lang.Exception {
        chrono("MM-Selection");
        SelectionManager sm = context.getWorkbenchContext().getLayerViewPanel().getSelectionManager();
        LayerManager layerManager = context.getLayerManager();
        Collection layersWithSelectedItems = sm.getLayersWithSelectedItems();
        Iterator itLayers = layersWithSelectedItems.iterator();
        java.util.List shapes = new ArrayList();
        Coordinate c = null;
        while (itLayers.hasNext()) {
            Layer currentLayer = (Layer)itLayers.next();
            //shapes.add(sm.getFeaturesWithSelectedItems(currentLayer));
            Collection selectedFeatures = sm.getFeaturesWithSelectedItems(currentLayer);
            Iterator it = selectedFeatures.iterator();
            while (it.hasNext()) {
                BasicFeature feature = (BasicFeature)it.next();
                shapes.add(feature.getGeometry());
            }
        }
        
        List<Coordinate> points = new ArrayList<Coordinate>();
        List<Coordinate> breakLines = new ArrayList<Coordinate>();
        int index = 0;
        chrono("MM-Tri");
        for (int i = 0 , nb = shapes.size() ; i < nb ; i++) {
            Geometry g = (Geometry)shapes.get(i);
            if (g instanceof Point /* && !Double.isNaN(g.getCoordinate().z)*/) {
                points.add(g.getCoordinate());
                index++;
            }
            else if (g instanceof LineString) {
                LineString ls = (LineString)g;
                //int[] breakLine = new int[ls.getNumPoints()];
                points.add(ls.getCoordinates()[0]);
                for (int j = 1, n = ls.getNumPoints() ; j < n ; j++) {
                    points.add(ls.getCoordinates()[j]);
                    breakLines.add(ls.getCoordinates()[j-1]);
                    breakLines.add(ls.getCoordinates()[j]);
                    /*if (Double.isNaN(c.z)) {
                        // La breakline est interrompue si elle comporte
                        // un point d'altitude inconnue. Une copie partielle
                        // du tableau est r�alis�e
                        System.arraycopy((Object)breakLine, 0, (Object)breakLine, 0, j);
                        break;
                    }*/
                    //else {
                        //points.add(g.getCoordinates()[j]);
                        //breakLine[j] = index++;
                    //}
                }
                //breakLineList.add(breakLine);
            }
            else {}
        }
        
        Coordinate[] cc = (Coordinate[])points.toArray(new Coordinate[0]);
        if (cc.length==0) return;
        //int[][] breakLines = (int[][])breakLineList.toArray(new int[][]{});
        Coordinate[] bl = breakLines.toArray(new Coordinate[breakLines.size()]);
        chrono("MM-start-triangulation");
        DelaunayTriangulationFactory2 triangulation = new DelaunayTriangulationFactory2(cc, bl);
        //triangulation.triangulate();
        chrono("MM-end-triangulation");
        cc = triangulation.getTriangulatedPoints();
        FeatureCollection fc = new FeatureDataset(TRIANGULATION_SCHEMA);
        chrono("MM-create-features");
        for (int i = 0 ; i < cc.length ; i+=3) {
            Feature feature = new BasicFeature(TRIANGULATION_SCHEMA);
            Coordinate[] triangle = new Coordinate[]{cc[i], cc[i+1], cc[i+2], cc[i]};
            factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]);
            feature.setGeometry(factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]));
            feature.setAttribute("Num�ro", new Integer(i/3));
            fc.add(feature);
        }
        Layer layer = createNewTriangulationLayer(context);
        layer.setFeatureCollection(fc);
        chrono("MM-end");
    }

    private static void chrono(String s) {
        long t = System.currentTimeMillis();
        //long s = t/1000;
        //long ms = t%1000;
        System.out.printf("%16s: %2$tH:%2$tM:%2$tS.%2$tL",s,t);
        System.out.println("");
    }
    
    private Layer createNewTriangulationLayer(final PlugInContext context) {
        LayerManager lm = context.getWorkbenchContext().getLayerManager();
        lm.addCategory("Triangulations");
        return lm.addLayer("Triangulations",
                            new Layer("Triangulation",
                            Color.YELLOW,
                            new FeatureDataset(TRIANGULATION_SCHEMA),
                            lm));
    }

}
