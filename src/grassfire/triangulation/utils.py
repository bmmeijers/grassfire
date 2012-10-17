'''
Created on Apr 15, 2010

@author: martijn
'''
from mesh import HE_BOUNDARY, PT_INTERIOR, PT_BOUNDARY, MovingVertex
from predicates import orient2d, incircle
#from mesher.delaunay import PT_BOUNDARY, HE_AUXILARY

class MeshVisitor:
    def __init__(self, mesh):
        self.mesh = mesh
        
    def visit_regions(self):
        self.flag_half_edges(0)
        self.triangles = []
        label = 1000
        # start from large triangle
        walk = self.mesh.locate(self.mesh.vertices[0])
        edge = walk
        neighbours = []
        current = [edge]
        while neighbours or current:
#            print ".", len(current)
#            print ".", len(neighbours)
            if current:
                edge = current.pop()
                if edge.flag != 1:
                    self.triangles.append(edge)
                # flag three edge's that form triangle as visited 
                edge.flag = 1
                edge.next.flag = 1
                edge.next.next.flag = 1
                # stack three neighboring triangles
                if edge.sibling is not None: # otherwise we fall of the world ;)
                    if edge.sibling.constraint is False and edge.sibling.flag is 0:
                        current.append(edge.sibling)
                    elif edge.sibling.constraint is True and edge.sibling.flag is 0:
                        neighbours.append(edge.sibling)
                if edge.next.sibling is not None:
                    if edge.next.sibling.constraint is False and edge.next.sibling.flag is 0:
                        current.append(edge.next.sibling)
                    elif edge.next.sibling.constraint is True and edge.next.sibling.flag is 0:
                        neighbours.append(edge.next.sibling)
                if edge.next.next.sibling is not None:
                    if edge.next.next.sibling.constraint is False and edge.next.next.sibling.flag is 0:
                        current.append(edge.next.next.sibling)
                    elif edge.next.next.sibling.constraint is False and edge.next.next.sibling.flag is 0:
                        neighbours.append(edge.next.next.sibling)
            else:
                # we have finished with this region, thus re-label the 
                # triangles in this region 
                for t in self.triangles:
#                    print t, t.next, t.next.next
                    t.label = label
                    t.next.label = label
                    t.next.next.label = label
                label += 10
                self.triangles = []
                if neighbours:
                    edge = neighbours.pop()
                    current = [edge]

    def visit_exterior(self):
        self.flag_half_edges(0)
        self.triangles = []
        # start from large triangle
        walk = self.mesh.locate(self.mesh.vertices[0])
        edge = walk
        stack = [edge]
        while stack:
            edge = stack.pop()
            if edge.flag != 1:
                self.triangles.append(edge)
            # flag three edge's that form triangle as visited 
            edge.flag = 1
            edge.next.flag = 1
            edge.next.next.flag = 1
            # stack three neighboring triangles
            if edge.sibling is not None and edge.sibling.constraint is False and edge.sibling.flag is 0:
                stack.append(edge.sibling)
            if edge.next.sibling is not None and edge.next.sibling.constraint is False and edge.next.sibling.flag is 0:
                stack.append(edge.next.sibling)
            if edge.next.next.sibling is not None and edge.next.next.sibling.constraint is False and edge.next.next.sibling.flag is 0:
                stack.append(edge.next.next.sibling)

    def flag_half_edges(self, flag):
        for edge in self.mesh.half_edges:
            edge.flag = flag

    def visit_interior(self):
        self.triangles = []
        UNKNOWN = 0
        EXTERIOR = 1
        INTERIOR = 2
        self.mesh.reset_flags(UNKNOWN)
        # start at `infinity' point (from large triangle)
        start = None
        walk = self.mesh.locate(self.mesh.vertices[0])
        edge = walk
        stack = [edge]
        while stack:
            edge = stack.pop()
            # flag three edge's that form triangle as visited 
            edge.flag += EXTERIOR
            edge.next.flag += EXTERIOR
            edge.next.next.flag += EXTERIOR
            # stack neighboring triangles or break and start `interior' walk
            # first triangle
            if edge.sibling is not None and edge.sibling.constraint is True:
                start = edge.sibling
#                break
            if edge.sibling is not None and \
                edge.sibling.constraint is False and UNKNOWN == edge.sibling.flag:
                stack.append(edge.sibling)
            # second triangle
            if edge.next.sibling is not None and \
                edge.next.sibling.constraint is True:
                start = edge.next.sibling
#                break
            if edge.next.sibling is not None and \
                edge.next.sibling.constraint is False and \
                UNKNOWN == edge.next.sibling.flag:
                stack.append(edge.next.sibling)
            # third triangle
            if edge.next.next.sibling is not None and \
                edge.next.next.sibling.constraint is True:
                start = edge.next.next.sibling
#                break
            if edge.next.next.sibling is not None and \
                edge.next.next.sibling.constraint is False and \
                UNKNOWN == edge.next.next.sibling.flag:
                stack.append(edge.next.next.sibling)
        if start is None: return
        # interior walk
        assert start is not None
        stack = [start]
        while stack:
            edge = stack.pop()
            if edge.flag == INTERIOR:
                # already entered via other side, so we skip this time
                continue
            edge.flag += INTERIOR
            edge.next.flag += INTERIOR
            edge.next.next.flag += INTERIOR
            if edge.flag == INTERIOR:
                self.triangles.append(edge)
            # stack unvisited ones (flag is UNKNOWN), 
            # but do not go over constraints (this leaves out holes)
            if UNKNOWN == edge.sibling.flag:
                stack.append(edge.sibling)
            if UNKNOWN == edge.next.sibling.flag:
                stack.append(edge.next.sibling)
            if UNKNOWN == edge.next.next.sibling.flag:
                stack.append(edge.next.next.sibling)

    def label_exterior(self, label):
        self.visit_exterior()
        for edge in self.triangles:
            edge.label = label
            edge.next.label = label
            edge.next.next.label = label

    def label_interior(self):
        self.visit_interior()
        for edge in self.triangles:
#            print ">>>", edge
#            label = edge.label
##            assert edge.next.label is None or edge.next.label == label
##            assert edge.next.next.label is None or edge.next.next.label == label
#            edge.next.label = label
#            edge.next.next.label = label
            lst = [edge, edge.next, edge.next.next]
            for edge in lst:
                if edge.label is not None:
                    break
            all = edge.label
            for edge in lst:
                try:
                    assert edge.label is None or edge.label == all
                except:
                    print "WARNING: triangle found with more than 1 label"
                edge.label = all

class MeshVisualizer:
    
    def __init__(self, mesh):
        self.mesh = mesh
        
    def visit_all(self):
        self.triangles = []
        self.mesh.clear_flags()
        # start from large triangle
        edge, tp = self.mesh.locate(self.mesh.vertices[0])
        stack = set([edge])
        while stack:
            edge = stack.pop()
            # TODO: make exporting infinite triangles optional
            if edge.flag != 1:
                # do not add triangle if infinite triangle
#                if edge.origin.type != PT_BOUNDARY and \
#                    edge.next.origin.type != PT_BOUNDARY and \
#                    edge.next.next.origin.type != PT_BOUNDARY: 
                    
                    self.triangles.append(edge)
            # flag three edge's that form triangle as visited 
            edge.flag = 1
            edge.next.flag = 1
            edge.next.next.flag = 1
            # stack three neighboring triangles
            if edge.sibling is not None and edge.sibling.flag is None:
                stack.add(edge.sibling)
            if edge.next.sibling is not None and edge.next.sibling.flag is None:
                stack.add(edge.next.sibling)
            if edge.next.next.sibling is not None and edge.next.next.sibling.flag is None:
                stack.add(edge.next.next.sibling)
    
    def list_triangles_wkt(self, fh):
        self.visit_all()
        for i, t in enumerate(self.triangles):
            a, b, c, = t, t.next, t.next.next
            #l = [a.label, a.origin.point, b.label, b.origin.point, c.label, c.origin.point]
#            l = [a.label, b.label, c.label]
            fh.write( "POLYGON(({0} {1}, {2} {3}, {4} {5}, {6} {7}))\n".format(                           
                            a.origin.x, a.origin.y, 
                            b.origin.x, b.origin.y, 
                            c.origin.x, c.origin.y, 
                            a.origin.x, a.origin.y)
            )
    def list_triangles_time(self, fh, time = 0.):
        self.visit_all()
        for _, t in enumerate(self.triangles):
            a, b, c, = t, t.next, t.next.next
            #l = [a.label, a.origin.point, b.label, b.origin.point, c.label, c.origin.point]
#            l = [a.label, b.label, c.label]

            if isinstance(a.origin, MovingVertex):
                pta = a.origin.point_at(time)
                print "here", pta
            else:
                pta = a.origin.point
            
            if isinstance(b.origin, MovingVertex):
                ptb = b.origin.point_at(time)
                print "here", ptb
            else:
                ptb = b.origin.point
                
            if isinstance(c.origin, MovingVertex):
                
                ptc = c.origin.point_at(time)
                print "here", ptc
            else:
                ptc = c.origin.point
                    
            fh.write( "POLYGON(({0} {1}, {2} {3}, {4} {5}, {6} {7}))\n".format(                           
                            pta[0], pta[1], 
                            ptb[0], ptb[1], 
                            ptc[0], ptc[1], 
                            pta[0], pta[1])
            )

    def list_triangles(self):
        self.visit_all()
        from psycopg2 import connect
        from connect import auth_params
        auth = auth_params()
        connection = connect(host='%s' % auth['host'], 
                                  port=auth['port'], 
                                  database='%s' % auth['database'], 
                                  user='%s' % auth['username'], 
                                  password='%s' % auth['password'])
        cursor = connection.cursor()      
        cursor.execute("DROP TABLE IF EXISTS tmp_mesh_pl;")
        cursor.execute("""
CREATE TABLE tmp_mesh_pl
(
    id int8 UNIQUE NOT NULL,
    flag varchar,
    label varchar
) WITH OIDS;""")
        cursor.execute("""
SELECT AddGeometryColumn('tmp_mesh_pl', 'geometry', -1, 'POLYGON', 2);
""")
        print "listing #", len(self.triangles), "triangles"
        for i, t in enumerate(self.triangles):
            a, b, c, = t, t.next, t.next.next
            #l = [a.label, a.origin.point, b.label, b.origin.point, c.label, c.origin.point]
#            l = [a.label, b.label, c.label]
            cursor.execute("""INSERT INTO tmp_mesh_pl (id, flag, label, geometry) VALUES({0}, {1}, '{2}', geomfromtext('{3}') );""".format(
                            i,
                            "{0}".format(a.flag),
                            "",
                            "POLYGON(({0} {1}, {2} {3}, {4} {5}, {6} {7}))".format(                           
                            a.origin.x, a.origin.y, 
                            b.origin.x, b.origin.y, 
                            c.origin.x, c.origin.y, 
                            a.origin.x, a.origin.y)
                            ))
        connection.commit()
        cursor.close()
        connection.close()


    def list_points(self):
        for pt in self.mesh.vertices:
            print pt

    def list_half_edges(self):
        for edge in self.mesh.half_edges:
            if edge.sibling is not None:
                print "<edge<%10d>, .origin<%10d, %s>, .next<%10d>, .sibling<%10d>>" % (edge.id, edge.origin.id, edge.origin, edge.next.id, edge.sibling.id)
            else:
                print "<edge<%10d>, .origin<%10d, %s>, .next<%10d>, .sibling<None>>" % (edge.id, edge.origin.id, edge.origin, edge.next.id)

    def list_mesh(self):
        print "=" * 18
        print "Mesh"
        print "=" * 18
        print "Points"
        print "-" * 18
        self.list_points()
        print ""
        print "Halfedges"
        print "-" * 18
        self.list_half_edges()
        print "=" * 18
    
    def list_he_geometry(self):
        for edge in self.mesh.half_edges:
            print id(edge), "(", edge.origin.x, edge.origin.y, ") --> (", edge.next.origin.x, edge.next.origin.y, ")"

    def list_dot(self):
        print "# Generated by mesh.py"
        print """digraph G {        
        graph [ratio=fill];
        graph [size="20, 20"];
        graph [center="1"];
"""
        for pt in self.mesh.vertices:
            print pt.id, '[label="', pt.id, "(%.1f," % pt.x, "%.1f)" % pt.y, '"];'
        flagged = set()
        for edge in self.mesh.half_edges:
            if edge not in flagged:
                boundary = False
                if edge.type == HE_BOUNDARY:
                    boundary = True
                if boundary:
                    bold = ", style=bold"
                else:
                    bold = ""
                print edge.origin.id, "->", edge.next.origin.id, '[label="', edge.id, '"%s];' % (bold)
                flagged.add(edge)
                print edge.sibling.origin.id, "->", edge.sibling.next.origin.id, '[label="', edge.sibling.id, '", style=dotted];'
                flagged.add(edge.sibling)
        print "}"
    
    def list_labelled_he(self):
        from psycopg2 import connect
        from connect import auth_params
        auth = auth_params()
        connection = connect(host='%s' % auth['host'], 
                                  port=auth['port'], 
                                  database='%s' % auth['database'], 
                                  user='%s' % auth['username'], 
                                  password='%s' % auth['password'])
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS tmp_mesh_ln0;")
        cursor.execute("""CREATE TABLE tmp_mesh_ln0
(
    id int8 UNIQUE NOT NULL,
    ln_type integer,
    label varchar
) WITH OIDS;""")
        cursor.execute("""SELECT AddGeometryColumn('tmp_mesh_ln0', 'line', -1, 'LINESTRING', 2);""")
        for edge in self.mesh.half_edges:
            if edge.label != -1:
                cursor.execute( "INSERT INTO tmp_mesh_ln0 (id, line, ln_type, label) VALUES (%d, geomfromtext('LINESTRING(%f %f, %f %f)'), %d, '%s');" % (edge.id, edge.origin.x, edge.origin.y, edge.next.origin.x, edge.next.origin.y, edge.type, edge.label) )                

        connection.commit()    
        cursor.close()
        connection.close()     


#    def list_pg(self):
#        from psycopg2 import connect
#        from connect import auth_params
#        auth = auth_params()
#        connection = connect(host='%s' % auth['host'], 
#                                  port=auth['port'], 
#                                  database='%s' % auth['database'], 
#                                  user='%s' % auth['username'], 
#                                  password='%s' % auth['password'])
#        cursor = connection.cursor()
#        cursor.execute("DROP TABLE IF EXISTS tmp_mesh_ln0;")
#        cursor.execute("DROP TABLE IF EXISTS tmp_mesh_ln1;")
#        cursor.execute("DROP TABLE IF EXISTS tmp_mesh_pt;")
#        cursor.execute("""CREATE TABLE tmp_mesh_ln0
#(
#    id int8 UNIQUE NOT NULL,
#    ln_type integer,
#    label varchar
#) WITH OIDS;""")
#        
#        cursor.execute("""SELECT AddGeometryColumn('tmp_mesh_ln0', 'line', -1, 'LINESTRING', 2);""")
#        cursor.execute("""
#CREATE TABLE tmp_mesh_ln1
#(
#    id int8 UNIQUE NOT NULL,
#    ln_type integer,
#    label varchar
#)  WITH OIDS;
#        
#        """
#                       )
#        cursor.execute("SELECT AddGeometryColumn('tmp_mesh_ln1', 'line', -1, 'LINESTRING', 2);")
#        cursor.execute("""
#CREATE TABLE tmp_mesh_pt
#(
#    id int8 UNIQUE NOT NULL,
#    flag integer,
#    label integer, 
#    weights varchar
#)  WITH OIDS;
#        """)
#        cursor.execute("SELECT AddGeometryColumn('tmp_mesh_pt', 'point', -1, 'POINT', 2);")
#        for pt in self.mesh.vertices:
#            cursor.execute("INSERT INTO tmp_mesh_pt (id, flag, label, weights, point) VALUES (%d, %d, %d, '%s', geomfromtext('POINT(%f %f)'));" % (pt.id, pt.flag, pt.label, pt.weights, pt.x, pt.y))
#
#        flagged = set()
#        for edge in self.mesh.half_edges:
#            if edge not in flagged:
#                cursor.execute( "INSERT INTO tmp_mesh_ln0 (id, line, ln_type, label) VALUES (%d, geomfromtext('LINESTRING(%f %f, %f %f)'), %d, '%s');" % (edge.id, edge.origin.x, edge.origin.y, edge.next.origin.x, edge.next.origin.y, edge.type, "") )
#                flagged.add(edge)
#                if edge.type != HE_BOUNDARY:
#                    cursor.execute( "INSERT INTO tmp_mesh_ln1 (id, line, ln_type, label) VALUES (%d, geomfromtext('LINESTRING(%f %f, %f %f)'), %d, '%s');" % (edge.sibling.id, edge.sibling.origin.x, edge.sibling.origin.y, edge.sibling.next.origin.x, edge.sibling.next.origin.y, edge.sibling.type, ""))
#                    flagged.add(edge.sibling)
#        connection.commit()    
#        cursor.close()
#        connection.close()            
    def list_pg(self):
        print("DROP TABLE IF EXISTS tmp_mesh_ln0;")
        print("DROP TABLE IF EXISTS tmp_mesh_ln1;")
        print("DROP TABLE IF EXISTS tmp_mesh_pt;")
        print("""CREATE TABLE tmp_mesh_ln0
(
    id int8 UNIQUE NOT NULL,
    ln_type integer,
    label varchar
) WITH OIDS;""")
        
        print("""SELECT AddGeometryColumn('tmp_mesh_ln0', 'line', -1, 'LINESTRING', 2);""")
        print("""
CREATE TABLE tmp_mesh_ln1
(
    id int8 UNIQUE NOT NULL,
    ln_type integer,
    label varchar
)  WITH OIDS;
        
        """
                       )
        print("SELECT AddGeometryColumn('tmp_mesh_ln1', 'line', -1, 'LINESTRING', 2);")
        print("""
CREATE TABLE tmp_mesh_pt
(
    id int8 UNIQUE NOT NULL,
    flag integer,
    label integer, 
    weights varchar
)  WITH OIDS;
        """)
        print("SELECT AddGeometryColumn('tmp_mesh_pt', 'point', -1, 'POINT', 2);")
        for pt in self.mesh.vertices:
            print("INSERT INTO tmp_mesh_pt (id, flag, label, weights, point) VALUES (%d, %d, %d, '%s', geomfromtext('POINT(%f %f)'));" % (pt.id, pt.flag, pt.label, pt.weights, pt.x, pt.y))

        flagged = set()
        for edge in self.mesh.half_edges:
            if edge not in flagged:
                print( "INSERT INTO tmp_mesh_ln0 (id, line, ln_type, label) VALUES (%d, geomfromtext('LINESTRING(%f %f, %f %f)'), %d, '%s');" % (edge.id, edge.origin.x, edge.origin.y, edge.next.origin.x, edge.next.origin.y, edge.type, "") )
                flagged.add(edge)
#                if edge.type != HE_BOUNDARY:
                if edge.sibling != None:
                    print( "INSERT INTO tmp_mesh_ln1 (id, line, ln_type, label) VALUES (%d, geomfromtext('LINESTRING(%f %f, %f %f)'), %d, '%s');" % (edge.sibling.id, edge.sibling.origin.x, edge.sibling.origin.y, edge.sibling.next.origin.x, edge.sibling.next.origin.y, edge.sibling.type, ""))
                    flagged.add(edge.sibling)

class MeshTester:
    def __init__(self, mesh):
        self.mesh = mesh
        
    def audit(self):
        self.test_faces()
        self.test_half_edge_pointers()
        self.test_half_edges()
        self.test_relations()

    def test_faces(self):
        print "-- testing faces"
        used = set()
        for edge in self.mesh.half_edges:
            if edge in used:
                continue
            face = set()
            he_test = edge
            for _ in xrange(len(self.mesh.half_edges)):
                used.add(he_test)
                face.add(he_test)
                he_test = he_test.next
                if he_test == edge:
                    break
            else:
                print "Weird face found"
            if len(face) > 3:
                print "WEIRD FACE FOUND"
        # make rotations, do it for each half edge, to be very sure
        # triangles are represented as triangle, really
        for edge in self.mesh.half_edges:
            t0, t1, t2 = edge, edge.next, edge.next.next
            t3, t4, t5 = edge.next, edge.next.next, edge.next.next.next
            t6, t7, t8 = edge.next.next, edge.next.next.next, edge.next.next.next.next
            p0, p1, p2 = t0.origin, t1.origin, t2.origin
            p3, p4, p5 = t3.origin, t4.origin, t5.origin
            p6, p7, p8 = t6.origin, t7.origin, t8.origin
            assert p0 == p5
            assert p0 == p7
            assert p1 == p3
            assert p1 == p8
            assert p2 == p4
            assert p2 == p6
            assert orient2d(p0, p1, p2) > 0, "flat triangle in mesh"
            

            # Check whether empty circle criterion holds
            #
            # For triangle n0, n1, n2 all points of direct incident triangles 
            # should be outside this circle
            #
            # We allow co-circularity
            #            
            e0, e1, e2 = edge, edge.next, edge.next.next
            n0, n1, n2 = e0.origin, e1.origin, e2.origin
            n3, n4, n5 = None, None, None
            e3, e4, e5 = e0.sibling, e1.sibling, e2.sibling
            err = 0
            if e3 is not None:
                n3 = e3.next.next.origin
                if incircle(n0, n1, n2, n3) > 0.:
                    err += 1
            if e4 is not None:
                n4 = e4.next.next.origin
                if incircle(n0, n1, n2, n4) > 0.:
                    err += 2
            if e5 is not None:
                n5 = e5.next.next.origin                    
                if incircle(n0, n1, n2, n5) > 0.:
                    err += 4
            if err != 0:
                print 'triangle', 'POLYGON(({0[0]} {0[1]}, {1[0]} {1[1]}, {2[0]} {2[1]}, {0[0]} {0[1]}))'.format(n0, n1, n2)
                print 'points around', n3, n4, n5
                print 'violator(s):'
                if err & 1: print n3, incircle(n0, n1, n2, n3)
                if err & 2: print n4, incircle(n0, n1, n2, n4)
                if err & 4: print n5, incircle(n0, n1, n2, n5)
#                raise AssertionError('Non-Delaunay triangle found')

    def test_half_edges(self):
        v = set(self.mesh.vertices)
        h = set(self.mesh.half_edges)
        print "-- testing half edges"
        for edge in self.mesh.half_edges:
            if edge.origin not in v:
                print "missing origin"
            if edge.next not in h:
                print "missing next pointer"
            if edge.type != HE_BOUNDARY:
                if edge.sibling not in h:
                    print "missing sibling"
                if edge.sibling.sibling != edge:
                    print "mismatched sibling"
                if edge.next.origin != edge.sibling.origin:
                    print "unaligned next/sibling"

    def test_half_edge_pointers(self):
        print "-- testing half edge pointers"
        for p in self.mesh.vertices:
            if p.he not in self.mesh.half_edges:
                print "missing halfedge for point"
            if p.he.origin != p:
                print "mismatched halfedge for point"
    
    def test_relations(self):
        """Check whether mesh follows Delaunay property
        
        Based on the total number of vertices (n) and the number of vertices
        on the convex hull of the triangulation (n_c) the following properties
        should hold:
        
        # vertices = n
        # vertices on convex hull = n_c
        # triangles = 2 (n-1)-n_c = 2n - 2 - n_c
        # edges = 3 (n-1) - n_c = 3n - 3 - n_c
        """
        # number of vertices
        n = 0
        for v in self.mesh.vertices:
            if v.type == PT_INTERIOR:
                n += 1
        # number of vertices on convex hull
        n_c = 0
        for v in self.mesh.vertices:
            if v.type == PT_INTERIOR:
                on_hull = False
                start = v.he
                if start.sibling.origin.type == PT_BOUNDARY:
                    on_hull = True
                edge = start.sibling.next
                while edge is not start and not on_hull:
                    if edge.sibling.origin.type == PT_BOUNDARY:
                        on_hull = True
                    edge = edge.sibling.next
                if on_hull:
                    n_c += 1
        # count number of triangles
        ctt = 0        
        used = set()
        for edge in self.mesh.half_edges:
            if edge in used:
                continue
            he_test = edge
            all_interior = True
            for _ in xrange(len(self.mesh.half_edges)):
                used.add(he_test)
                if he_test.origin.type != PT_INTERIOR:
                    all_interior = False
                he_test = he_test.next
                if he_test == edge:
                    if all_interior: 
                        ctt += 1
                    break
        # count number of edges
        cte = 0
        used = set()
        for edge in self.mesh.half_edges:
            if edge in used:
                continue
            used.add(edge)
            if edge.sibling:
                used.add(edge.sibling)
                if edge.origin.type == PT_INTERIOR and \
                    edge.sibling.origin.type == PT_INTERIOR:
                    cte += 1
        # expected number of triangles / edges
        # these numbers only hold for a triangulation that contains triangles
        # the relation is a bit different for those without triangles...
        t = 2 * (n - 1) - n_c
        e = 3 * (n - 1) - n_c
        # check no of triangles
        if n < 3:
            assert ctt == 0
        else:
            assert ctt == t
        # check no of edges
        if n < 2:
            assert cte == 0
        else:
            assert cte == e