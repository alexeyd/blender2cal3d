from operator import attrgetter

class MaterialColor:
	def __init__(self, r, g, b, a):
		self.r = r
		self.g = g
		self.b = b
		self.a = a



class Material:
	def __init__(self, name, index, xml_version):
		self.ambient = MaterialColor(255, 255, 255, 255)
		self.diffuse = MaterialColor(255, 255, 255, 255)
		self.specular = MaterialColor(255, 255, 255, 255)
		self.shininess = 1.0
		self.maps_filenames = []
    
		self.name = name
		self.index = index
		self.xml_version = xml_version


	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XRF\" VERSION=\"{0}\"/>\n".format(self.xml_version)
		s += "  <MATERIAL NUMMAPS=\"{0}\">\n".format(len(self.maps_filenames))

		s += "  <AMBIENT>{0} {1} {2} {3}</AMBIENT>\n".format(self.ambient_r, 
		                                                     self.ambient_g, 
		                                                     self.ambient_b, 
		                                                     self.ambient_a)

		s += "  <DIFFUSE>{0} {1} {2} {3}</DIFFUSE>\n".format(self.diffuse_r,
		                                                     self.diffuse_g,
		                                                     self.diffuse_b,
		                                                     self.diffuse_a)

		s += "  <SPECULAR>{0} {1} {2} {3}</SPECULAR>\n".format(self.specular.r,
		                                                       self.specular.g, 
		                                                       self.specular.b,
		                                                       self.specular.a)

		s += "  <SHININESS>{0}</SHININESS>\n".format(self.shininess)

		for map_filename in self.maps_filenames:
			s += "  <MAP>{0}</MAP>\n".format(map_filename)
		s += "</MATERIAL>\n"
		return s



class Map:
	def __init__(self, u, v):
		self.u = u
		self.v = v
    
    
	def to_cal3d_xml(self):
		return "      <TEXCOORD>{0} {1}</TEXCOORD>\n".format(self.u, self.v)



class Influence:
	def __init__(self, bone_index, weight):
		self.bone_index = bone_index
		self.weight = weight
    
	
	def to_cal3d_xml(self):
		return "      <INFLUENCE ID=\"{0}\">{1}</INFLUENCE>\n".format(self.bone_index, 
		                                                              self.weight)



class Vertex:
	def __init__(self, submesh, index, loc, normal):
		self.submesh = submesh
		self.index = index

		self.loc = loc.copy()
		self.normal = normal.copy()
		self.maps = []
		self.influences = []
		self.weight = 0.0
		self.hasweight = False


	def to_cal3d_xml(self):
		# normalize weights
		total_weight = 0.0
		for influence in self.influences:
			total_weight += influence.weight

		for influence in self.influences:
			influence.weight /= total_weight
		
		s = "    <VERTEX ID=\"{0}\" NUMINFLUENCES=\"{1}\">\n".format(self.index,
		                                                             len(self.influences))
		s += "      <POS>{0} {1} {2}</POS>\n".format(self.loc[0],
		                                             self.loc[1], 
		                                             self.loc[2])

		s += "      <NORM>{0} {1} {2}</NORM>\n".format(self.normal[0],
		                                               self.normal[1],
		                                               self.normal[2])

		s += "".join(map(Map.to_cal3d_xml, self.maps))
		s += "".join(map(Influence.to_cal3d_xml, self.influences))
		if self.hasweight:
			s += "      <PHYSIQUE>{0}</PHYSIQUE>\n".format(self.weight)
		s += "    </VERTEX>\n"
		return s



class Face:
	def __init__(self, submesh, vertex1, vertex2, vertex3, vertex4):
		self.vertex1 = vertex1
		self.vertex2 = vertex2
		self.vertex3 = vertex3
		self.vertex4 = vertex4
    
		self.can_collapse = 0
    
		self.submesh = submesh
		submesh.faces.append(self)


	def to_cal3d_xml(self):
		if self.vertex4:
			s = "    <FACE VERTEXID=\"{0} {1} {2}\"/>\n".format(self.vertex1.index,
			                                                    self.vertex2.index,
			                                                    self.vertex3.index)

			s += "    <FACE VERTEXID=\"{0} {1} {2}\"/>\n".format(self.vertex1.index,
			                                                     self.vertex3.index,
			                                                     self.vertex4.index)
			return s
		else:
			return "    <FACE VERTEXID=\"{0} {1} {2}\"/>\n".format(self.vertex1.index,
			                                                       self.vertex2.index,
			                                                       self.vertex3.index)



class SubMesh:
	def __init__(self, mesh, index, material_id):
		self.mesh = mesh
		self.index = index
		self.material_id = material_id

		self.vertices = []
		self.faces = []
		self.nb_lodsteps = 0
		self.springs = []


	def to_cal3d_xml(self):
		self.vertices = sorted(self.vertices, key=attrgetter('index'))
		texcoords_num = 0
		if self.vertices and len(self.vertices) > 0:
			texcoords_num = len(self.vertices[0].maps)

		faces_num = 0
		for face in self.faces:
			if face.vertex4:
				faces_num += 2
			else:
				faces_num += 1

		s = "  <SUBMESH NUMVERTICES=\"{0}\" NUMFACES=\"{1}\" MATERIAL=\"{2}\" ".format(len(self.vertices),
		                                                                               faces_num,
		                                                                               self.material_id)

		s += "NUMLODSTEPS=\"{0}\" NUMSPRINGS=\"{1}\" NUMTEXCOORDS=\"{2}\">\n".format(self.nb_lodsteps,
		                                                                             len(self.springs),
		                                                                             texcoords_num)

		s += "".join(map(Vertex.to_cal3d_xml, self.vertices))
		s += "".join(map(Face.to_cal3d_xml, self.faces))
		s += "  </SUBMESH>\n"
		return s



class Mesh:
	def __init__(self, name, xml_version):
		self.name = name
		self.xml_version = xml_version
		self.submeshes = [] 


	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XMF\" VERSION=\"{0}\"/>\n".format(self.xml_version)
		s += "<MESH NUMSUBMESH=\"{0}\">\n".format(len(self.submeshes))
		s += "".join(map(SubMesh.to_cal3d_xml, self.submeshes))
		s += "</MESH>\n"
		return s

