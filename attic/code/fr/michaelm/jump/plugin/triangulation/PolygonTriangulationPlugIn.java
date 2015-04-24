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
import com.vividsolutions.jts.geom.util.*;
//import com.vividsolutions.jump.workbench.ui.renderer.style.BasicStyle;
import fr.michaelm.geom.DelaunayTriangulationFactory;

public class PolygonTriangulationPlugIn extends ThreadedBasePlugIn {
    private static FeatureSchema TRIANGULATION_SCHEMA = new FeatureSchema();
    private static GeometryFactory factory = new GeometryFactory();
    
    public void initialize(PlugInContext context) throws Exception {
        context.getFeatureInstaller().addMainMenuItem(this,
                                                      new String[] { "3D-Tools", "Triangulation" },
                                                      getName(), false,
                                                      null, null);
        TRIANGULATION_SCHEMA.addAttribute("Geometry", AttributeType.GEOMETRY);
        TRIANGULATION_SCHEMA.addAttribute("Numéro", AttributeType.INTEGER);
    }
                                                      
    public boolean execute(PlugInContext context) throws Exception {
        return true;
    }
    
    public void run(TaskMonitor monitor, PlugInContext context)
                                                    throws java.lang.Exception {
        SelectionManager sm = context.getWorkbenchContext().getLayerViewPanel().getSelectionManager();
        LayerManager layerManager = context.getLayerManager();
        FeatureCollection fc = new FeatureDataset(TRIANGULATION_SCHEMA);
        Collection layersWithSelectedItems = sm.getLayersWithSelectedItems();
        Iterator itLayers = layersWithSelectedItems.iterator();
        java.util.List shapes = new ArrayList();
        Coordinate c = null;
        while (itLayers.hasNext()) {
            Layer currentLayer = (Layer)itLayers.next();
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
            List list = LinearComponentExtracter.getLines(g);
            for (int j = 0 ; j < list.size() ; j++) {
                LineString ls = (LineString)list.get(j);
                int[] breakLine = new int[ls.getNumPoints()];
                for (int k = 0, n = ls.getNumPoints() ; k < n ; k++) {
                    c = ls.getCoordinates()[k];
                    if (Double.isNaN(c.z)) {
                        // La breakline est interrompue si elle comporte
                        // un point d'altitude inconnue. Une copie partielle
                        // du tableau est réalisée
                        System.arraycopy((Object)breakLine, 0, (Object)breakLine, 0, k);
                        break;
                    }
                    else {
                        points.add(ls.getCoordinates()[k]);
                        breakLine[k] = index++;
                    }
                }
                breakLineList.add(breakLine);
            }
            // triangulation objet par objet
            
            Coordinate[] cc = (Coordinate[])points.toArray(new Coordinate[0]);
            if (cc.length==0) continue;
            int[][] breakLines = (int[][])breakLineList.toArray(new int[][]{});
            DelaunayTriangulationFactory triangulation = new DelaunayTriangulationFactory(cc, breakLines);
            triangulation.triangulate();
            cc = triangulation.getTriangulatedPoints();
            //System.out.println("nb of points in final point array " + triangulation.getUpdatedPointArray().length);
            for (int j = 0 ; j < cc.length ; j+=3) {
                Feature feature = new BasicFeature(TRIANGULATION_SCHEMA);
                Coordinate[] triangle = new Coordinate[]{cc[j], cc[j+1], cc[j+2], cc[j]};
                Coordinate centre =
                    new Coordinate((cc[j].x + cc[j+1].x + cc[j+2].x)/3,
                                   (cc[j].y + cc[j+1].y + cc[j+2].y)/3);
                if (g.distance(factory.createPoint(centre))>0.001) continue;
                factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]);
                feature.setGeometry(factory.createPolygon(factory.createLinearRing(triangle), new LinearRing[0]));
                feature.setAttribute("Numéro", new Integer(j/3));
                fc.add(feature);
            }
            
        }
        Layer layer = createNewTriangulationLayer(context);
        layer.setFeatureCollection(fc);
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
