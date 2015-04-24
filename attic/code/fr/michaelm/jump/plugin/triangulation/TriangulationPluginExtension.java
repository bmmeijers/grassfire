package fr.michaelm.jump.plugin.triangulation;

import com.vividsolutions.jump.workbench.plugin.Extension;
import com.vividsolutions.jump.workbench.plugin.PlugInContext;

public class TriangulationPluginExtension extends Extension {
    public void configure(PlugInContext context) throws Exception {
        new TriangulationPlugIn().initialize(context);
        new PolygonTriangulationPlugIn().initialize(context);
        new MDTriangulationPlugIn().initialize(context);
        //new PolygonTriangulationPlugIn().initialize(context);
    }
    public String getName() {return "Delaunay Triangulator";}
    public String getVersion() {return "0.4 2009-04-17";}
}
