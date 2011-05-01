#!BPY
#fingers 2 each, knees 2.5, feet 2.5
"""
Name: 'Cal3D Exporter'
Blender: 249
Group: 'Export'
Tip: 'Export armature/bone data to the Cal3D library.'
"""

__author__ = ["Jean-Baptiste Lamy (Jiba)", "Chris Montijin", "Damien McGinnes", "David Young", "Alexey Dorokhov"]
__url__ = ("blender", "elysiun", "Cal3D, http://cal3d.sf.net")
__version__ = "1.0"

__bpydoc__ = """\
This script exports armature / bone data to the well known open source Cal3D
library.

Usage:

Simply run the script to export available armatures.

Supported:<br>
	Cal3D format versions 0.7 -> 0.9.

Known issues:<br>
	Animation export requires an open 3d graphics window.
	When you finish an animation and run the script you can get an error
(something with KeyError). Just save your work and reload the model. This is
usually caused by deleted items hanging around;<br>
	Cloth export only works reliably on a planar mesh (like a cape, or a
ribbon), not on a connected mesh (like a ball);

Notes:<br>
	Objects/bones/actions whose names start by "_" are not exported so call IK
and null bones _LegIK, for example;<br>
	Actions that start with '@' will be exported as actions, others will be
exported as cycles;<br>
	Meshes whose names are prefixed with Cloth_ or cloth_ will have a spring
system created. Vertex group _cloth_weight is used to define the parts of
the mesh that act as anchors - give the 0 weight in this group. Otherwise 0.01
is a good weight. For now all springs have a coeff of 1000<br>
(The weights in _cloth_weight are stored as each included vertex's <PHYSIQUE> value.
Whatever that does);<br>
	Faces with more than 3 sides are automatically split into triangles when they're
exported;<br>
    
"""

# $Id: blender2cal3d.py,v 1.4 2010/07/16 00:00:00 elefth Exp $
#
# Copyright (C) 2003 Jean-Baptiste LAMY -- jiba@tuxfamily.org
# Copyright (C) 2004 Chris Montijin
# Copyright (C) 2004 Damien McGinnes
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


# This script is a Blender 2.49 => Cal3D 0.7/0.8/0.9/0.11 converter.
# (See http://blender.org and http://cal3d.sourceforge.net)
#

# This script was written by Jiba, modified by Chris and later modified by Damien
# and even later it was modified Alexey

# Changes:

# 1.4 Alexey Dorokhov <alexey.dorokhov at gmail.com>
#     Updated to work with 2.49a
#     Replaced internal linear math routines 
#       with the ones provided by blender Matutils API
#     Replaced "Export to Soya" option with more general
#       model transformations
# 1.1 David Young <dcyoung at pobox dot com>
#     Updated to work with the Blender 2.41 python API
#     Animations are exported from the pose matrix rather 
#       than ipos; this works around the broken animation
#       baking in 2.41
#     Fixed bug which caused some bones to be exported several
#       times
#
#(Also small changes to 2.24a - note that mesh and armature need to have same position - bookeater)"
#
# 1.0 Damien McGinnes <mcginnes at netspeed.com.au>
#     Forked from blender2cal3d because we have had 2
#       independant efforts working on the same script
#     Fixed springs so now you can have uv discontinuities
#       or multiple textures on a cloth mesh - this
#       requires a patch to cal3d to work properly
#
# 0.8 Damien McGinnes <mcginnes at netspeed.com.au>
#    Added Cloth export
#    Fixed bone child translation bug 
#    Added material colors
#
# 0.7 Damien McGinnes <mcginnes at netspeed com au>
#    Added NLA functionality for IPOs - this simplifies
#      the animation export and speeds it up significantly
#      it also removes the constraints on channel names -
#      they no longer have to match the bone or action and
#      .L .R etc are supported
#    bones starting with _ are not exported
#    textures no longer flipped vertically
#    fixed a filename bug for .csf and .cfg
#    actions that are prefixed with '@' go into the cfg file
#      as actions rather than cycles    
#    works with baked IK actions, unbaked ones wont work well
#      because you wont have the constraints evaluated
#    added an FPS slider into the gui
#    added registry saving for gui state. 
#    
# 0.6 Chris Montjin
#    Updated for Blender 2.32, 2.33
#    added basic GUI
#    generally improved flexibility
#
# 0.5 Jiba <jiba@tuxfamily.org>
#    Initial Release for Blender 2.28



# HOW TO USE :
# 1 - load the script in Blender's text editor
# 2 - type M-P (meta/alt + P) and wait until script execution is finished
# or install it in .scripts and access from the export menu

# ADVICE
# - Objects/bones/actions whose names start by "_" are not exported
#   so call IK and null bones _LegIK for example
# - Actions that start with '@' will be exported as actions, others will be
#   exported as cycles

# BUGS / TODO :
# - Armature can not be scaled (i.e. you can scale bones in edit mode,
#   but if you try to scale armature in object mode script will fail
#   to export your animations correctly)

# REMARKS
# 1. When you finished an animation and run the script
#    you can get an error (something with KeyError). Just save your work,
#    and reload the model. This is usualy caused by deleted items hanging around
# 2. If a vertex is assigned to one or more bones, but is has a for each
#    bone a weight of zero, there was a subdivision by zero somewhere
#    Made a workaround (if sum is 0.0 then sum becomes 1.0).
#    Generally vertices with no weight simply dont deform at all - regardless
#    of what you do with the skeleton - it is generally undesirable for this to
#    happen
# 3. You can place armature anywhere on the scene and you can place root bone 
#    anywhere within bonespace, but in the exported model root bone will always
#    be at point (0,0,0). All other objects (bones and meshes) will be moved 
#    accordingly, so the exported model will look right. All rotations (of armature,
#    bones, meshes) will be preserved. Mesh scale transformations will also be 
#    preserved, armature scale transformaions will make you animations a mess (=

# Parameters :

# The directory where the data are saved.
SAVE_TO_DIR = ""

# Delete all existing Cal3D files in directory?
DELETE_ALL_FILES = 1

# Should the script translate root bone origin to (0,0,0)?
ROOT_TO_ZERO = 1

EXPORT_SKELETON = 1
EXPORT_ANIMATION = 1
EXPORT_MESH = 1
EXPORT_MATERIAL = 0

#custom
FILE_SKELETONNAME = "skel"

# Prefix for all created files
FILE_PREFIX = "model_"

# Remove path from imagelocation
REMOVE_PATH_FROM_IMAGE = 0

# prefix or subdir for imagepathname (if you place your textures in a
# subdir or just need a prefix or something). Only used when
# REMOVE_PATH_FROM_IMAGE = 1. Set to "" if none.
IMAGE_PREFIX = "textures/"

# Export to new (>= 900) Cal3D XML-format
EXPORT_TO_XML = 1


# frames per second - used to convert blender frames to times
FPS = 25

RENAME_ANIMATIONS = {
  # "OldName" : "NewName",
  
	}


# These define initial model transformation (a generalisation of 
# 'export for Soya' functionality). The order of rotation is the following:
# 1) rotate model around X axis for ROT_X degrees
# 2) rotate model around Y axis for ROT_Y degress
# 3) rotate model around Z axis for ROT_Z degress

ROT_X = 0.0
ROT_Y = 0.0
ROT_Z = 0.0
SCALE = 1.0

CHANGE_ROT_X_EVENT_ID = 100
CHANGE_ROT_Y_EVENT_ID = 101
CHANGE_ROT_Z_EVENT_ID = 102
CHANGE_SCALE_EVENT_ID = 103
CHANGE_RTZ_EVENT_ID = 104

# Enables LODs computation. LODs computation is quite slow, and the algo is 
# surely not optimal :-(
LODS = 0

#remove the word '.BAKED' from exported baked animations
REMOVE_BAKED = 1
EXPORT_ALL_SCENES = 0

################################################################################
# Code starts here.
# 

import sys, os, os.path, struct, math, string
import Blender
from Blender.BGL import *
from Blender.Draw import *
from Blender.Armature import *
from Blender.Registry import *
from Blender.Mathutils import Matrix

# HACK -- it seems that some Blender versions don't define sys.argv,
# which may crash Python if a warning occurs.

if not hasattr(sys, "argv"): sys.argv = ["???"]

# Cal3D data structures

CAL3D_VERSION = 700
CAL3D_XML_VERSION = 900

# Define globals
BONES = {}
MATERIALS = {}
ANIMATIONS = {}

NEXT_MATERIAL_ID = 0
class Material:
	def __init__(self, name):
		self.ambient_r = 255
		self.ambient_g = 255
		self.ambient_b = 255
		self.ambient_a = 255
		self.diffuse_r = 255
		self.diffuse_g = 255
		self.diffuse_b = 255
		self.diffuse_a = 255
		self.specular_r = 255
		self.specular_g = 255
		self.specular_b = 255
		self.specular_a = 255
		self.shininess = 1.0
		self.maps_filenames = []
    
		MATERIALS[name] = self
		self.name = name
    
		global NEXT_MATERIAL_ID
		self.id = NEXT_MATERIAL_ID
		NEXT_MATERIAL_ID += 1
    
	def to_cal3d(self):
		s = "CRF\0" + struct.pack("iBBBBBBBBBBBBfi", CAL3D_VERSION,
			self.ambient_r, self.ambient_g, self.ambient_b, self.ambient_a,
			self.diffuse_r, self.diffuse_g, self.diffuse_b, self.diffuse_a,
			self.specular_r, self.specular_g, self.specular_b, self.specular_a,
			self.shininess, len(self.maps_filenames))
		for map_filename in self.maps_filenames:
			s += struct.pack("i", len(map_filename) + 1)
			s += map_filename + "\0"
		return s
  
	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XRF\" VERSION=\"%i\"/>\n" % CAL3D_XML_VERSION
		s += "  <MATERIAL NUMMAPS=\"%i\">\n" % len(self.maps_filenames)
		s += "  <AMBIENT>%i %i %i %i</AMBIENT>\n" % \
			(self.ambient_r, self.ambient_g, self.ambient_b, self.ambient_a)   
		s += "  <DIFFUSE>%i %i %i %i</DIFFUSE>\n" % \
			(self.diffuse_r, self.diffuse_g, self.diffuse_b, self.diffuse_a)
		s += "  <SPECULAR>%i %i %i %i</SPECULAR>\n" % \
			(self.specular_r, self.specular_g, self.specular_b, self.specular_a)
		s += "  <SHININESS>%f</SHININESS>\n" % self.shininess
		for map_filename in self.maps_filenames:
			s += "  <MAP>%s</MAP>\n" % map_filename
		s += "</MATERIAL>\n"
		return s
  
class Mesh:
	def __init__(self, name):
		self.name = name
		self.submeshes = []
    
		self.next_submesh_id = 0
    
	def to_cal3d(self):
		s = "CMF\0" + struct.pack("ii", CAL3D_VERSION, len(self.submeshes))
		s += "".join(map(SubMesh.to_cal3d, self.submeshes))
		return s
  
	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XMF\" VERSION=\"%i\"/>\n" % CAL3D_XML_VERSION
		s += "<MESH NUMSUBMESH=\"%i\">\n" % len(self.submeshes)
		s += "".join(map(SubMesh.to_cal3d_xml, self.submeshes))
		s += "</MESH>\n"
		return s
  
class SubMesh:
	def __init__(self, mesh, material_id):
		self.material_id = material_id
		self.vertices = []
		self.faces = []
		self.nb_lodsteps = 0
		self.springs = []
    
		self.next_vertex_id = 0
    
		self.mesh = mesh
		self.id = mesh.next_submesh_id
		mesh.next_submesh_id += 1
		mesh.submeshes.append(self)
    
	def compute_lods(self):
		"""Computes LODs info for Cal3D (there's no Blender related stuff here)."""
    
		print "Start LODs computation..."
		vertex2faces = {}
		for face in self.faces:
			for vertex in (face.vertex1, face.vertex2, face.vertex3):
				l = vertex2faces.get(vertex)
				if not l:
					vertex2faces[vertex] = [face]
				else:
					l.append(face)
        
		couple_treated = {}
		couple_collapse_factor = []
		nn = 0
		for face in self.faces:
			for a, b in ((face.vertex1, face.vertex2), (face.vertex1, face.vertex3),
				(face.vertex2, face.vertex3)):
				a = a.cloned_from or a
				b = b.cloned_from or b
				if a.id > b.id:
					a, b = b, a
				if not couple_treated.has_key((a, b)):
					# The collapse factor is simply the distance between the 2 points :-(
					# This should be improved !!
					if a.normal.dot(b.normal) < 0.1:
							continue
					dist_vec = b.loc - a.loc
					couple_collapse_factor.append((dist_vec.length, a, b))
					couple_treated[a, b] = 1
				#else:
				#	nn+=1
				#	print nn
				#	
		couple_collapse_factor.sort()
    
		collapsed = {}
		new_vertices = []
		new_faces = []
		for factor, v1, v2 in couple_collapse_factor:
			# Determines if v1 collapses to v2 or v2 to v1.
			# We choose to keep the vertex which is on the 
			# smaller number of faces, since
			# this one has more chance of being in an extrimity of the body.
			# Though heuristic, this rule yields very good results in practice.
			if len(vertex2faces[v1]) <  len(vertex2faces[v2]):
				v2, v1 = v1, v2
			elif len(vertex2faces[v1]) == len(vertex2faces[v2]):
				if collapsed.get(v1, 0): v2, v1 = v1, v2 # v1 already collapsed, try v2
        
			if (not collapsed.get(v1, 0)) and (not collapsed.get(v2, 0)):
				collapsed[v1] = 1
				#collapsed[v2] = 1
	        
				# Check if v2 is already collapsed
				while v2.collapse_to:
					v2 = v2.collapse_to
	        
				common_faces = filter(vertex2faces[v1].__contains__, vertex2faces[v2])
	        
				v1.collapse_to = v2
				v1.face_collapse_count = len(common_faces)
	        
				for clone in v1.clones:
					# Find the clone of v2 that correspond to this clone of v1
					possibles = []
					for face in vertex2faces[clone]:
						possibles.append(face.vertex1)
						possibles.append(face.vertex2)
						possibles.append(face.vertex3)
					clone.collapse_to = v2
					for vertex in v2.clones:
						if vertex in possibles:
							clone.collapse_to = vertex
							break
	            
					clone.face_collapse_count = 0
					new_vertices.append(clone)
	
				# HACK -- all faces get collapsed with v1 
				# (and no faces are collapsed with v1's
				# clones). This is why we add v1 in new_vertices after v1's clones.
				# This hack has no other incidence that consuming 
				# a little few memory for the
				# extra faces if some v1's clone are collapsed but v1 is not.
				new_vertices.append(v1)
	        
				self.nb_lodsteps += 1 + len(v1.clones)
	        
				new_faces.extend(common_faces)
				for face in common_faces:
					face.can_collapse = 1
	          
				# Updates vertex2faces
				if vertex2faces[face.vertex1].count(face):
					vertex2faces[face.vertex1].remove(face)
				if vertex2faces[face.vertex2].count(face):					
					vertex2faces[face.vertex2].remove(face)
				if vertex2faces[face.vertex3].count(face):					
					vertex2faces[face.vertex3].remove(face)
				vertex2faces[v2].extend(vertex2faces[v1])
#end loop        
		new_vertices.extend(filter(lambda vertex: not vertex.collapse_to, 
			self.vertices))
		new_vertices.reverse() # Cal3D want LODed vertices at the end
		for i in range(len(new_vertices)): new_vertices[i].id = i
		self.vertices = new_vertices
    
		new_faces.extend(filter(lambda face: not face.can_collapse, self.faces))
		new_faces.reverse() # Cal3D want LODed faces at the end
		self.faces = new_faces
    
		print "LODs computed : %s vertices can be removed (from a total of %s)." % \
			(self.nb_lodsteps, len(self.vertices))
    
	def rename_vertices(self, new_vertices):
		"""Rename (change ID) of all vertices, such as self.vertices == 
			new_vertices.
		"""
		for i in range(len(new_vertices)):
			new_vertices[i].id = i
		self.vertices = new_vertices
    
	def to_cal3d(self):
		texcoords_num = 0
		if self.vertices and len(self.vertices) > 0:
			texcoords_num = len(self.vertices[0].maps)

		s =  struct.pack("iiiiii", self.material_id, len(self.vertices), 
			len(self.faces), self.nb_lodsteps, len(self.springs), texcoords_num)
		s += "".join(map(Vertex.to_cal3d, self.vertices))
		s += "".join(map(Spring.to_cal3d, self.springs))
		s += "".join(map(Face.to_cal3d, self.faces))
		return s

	def to_cal3d_xml(self):
		texcoords_num = 0
		if self.vertices and len(self.vertices) > 0:
			texcoords_num = len(self.vertices[0].maps)

		s = "  <SUBMESH NUMVERTICES=\"%i\" NUMFACES=\"%i\" MATERIAL=\"%i\" " % \
			(len(self.vertices), len(self.faces), self.material_id)
		s += "NUMLODSTEPS=\"%i\" NUMSPRINGS=\"%i\" NUMTEXCOORDS=\"%i\">\n" % \
			(self.nb_lodsteps, len(self.springs), texcoords_num)
		s += "".join(map(Vertex.to_cal3d_xml, self.vertices))
		s += "".join(map(Spring.to_cal3d_xml, self.springs))
		s += "".join(map(Face.to_cal3d_xml, self.faces))
		s += "  </SUBMESH>\n"
		return s

class Vertex:
	def __init__(self, submesh, loc, normal):
		self.loc = loc.copy()
		self.normal = normal.copy()
		self.collapse_to = None
		self.face_collapse_count = 0
		self.maps = []
		self.influences = []
		self.weight = 0.0
		self.hasweight = 0
		
		
		self.cloned_from = None
		self.clones = []
    
		self.submesh = submesh
		self.id = submesh.next_vertex_id
		submesh.next_vertex_id += 1
		submesh.vertices.append(self)
    
	def to_cal3d(self):
		if self.collapse_to:
			collapse_id = self.collapse_to.id
		else:
			collapse_id = -1
		s = struct.pack("ffffffii", self.loc[0], self.loc[1], self.loc[2], 
			self.normal[0], self.normal[1], self.normal[2], collapse_id,
			self.face_collapse_count)
		s += "".join(map(Map.to_cal3d, self.maps))
		s += struct.pack("i", len(self.influences))
		s += "".join(map(Influence.to_cal3d, self.influences))
		if self.hasweight:
			s += struct.pack("f", self.weight)
		return s
  
	def to_cal3d_xml(self):
		if self.collapse_to:
			collapse_id = self.collapse_to.id
		else:
			collapse_id = -1
		s = "    <VERTEX ID=\"%i\" NUMINFLUENCES=\"%i\">\n" % \
			(self.id, len(self.influences))
		s += "      <POS>%f %f %f</POS>\n" % (self.loc[0], self.loc[1], self.loc[2])
		s += "      <NORM>%f %f %f</NORM>\n" % \
			(self.normal[0], self.normal[1], self.normal[2])
		if collapse_id != -1:
			s += "      <COLLAPSEID>%i</COLLAPSEID>\n" % collapse_id
			s += "      <COLLAPSECOUNT>%i</COLLAPSECOUNT>\n" % \
				self.face_collapse_count
		s += "".join(map(Map.to_cal3d_xml, self.maps))
		s += "".join(map(Influence.to_cal3d_xml, self.influences))
		if self.hasweight:
			s += "      <PHYSIQUE>%f</PHYSIQUE>\n" % self.weight
		s += "    </VERTEX>\n"
		return s
  
class Map:
	def __init__(self, u, v):
		self.u = u
		self.v = v
    
	def to_cal3d(self):
		return struct.pack("ff", self.u, self.v)
    
	def to_cal3d_xml(self):
		return "      <TEXCOORD>%f %f</TEXCOORD>\n" % (self.u, self.v)
    
class Influence:
	def __init__(self, bone, weight):
		self.bone = bone
		self.weight = weight
    
	def to_cal3d(self):
		return struct.pack("if", self.bone.id, self.weight)
    
	def to_cal3d_xml(self):
		return "      <INFLUENCE ID=\"%i\">%f</INFLUENCE>\n" % \
			(self.bone.id, self.weight)
    
class Spring:
	def __init__(self, vertex1, vertex2):
		self.vertex1 = vertex1
		self.vertex2 = vertex2
		self.spring_coefficient = 0.0
		self.idlelength = 0.0
    
	def to_cal3d(self):
		return struct.pack("iiff", self.vertex1.id, self.vertex2.id,
			self.spring_coefficient, self.idlelength)

	def to_cal3d_xml(self):
		return "    <SPRING VERTEXID=\"%i %i\" COEF=\"%f\" LENGTH=\"%f\"/>\n" % \
			(self.vertex1.id, self.vertex2.id, self.spring_coefficient,
			self.idlelength)

class Face:
	def __init__(self, submesh, vertex1, vertex2, vertex3):
		self.vertex1 = vertex1
		self.vertex2 = vertex2
		self.vertex3 = vertex3
    
		self.can_collapse = 0
    
		self.submesh = submesh
		submesh.faces.append(self)
    
	def to_cal3d(self):
		return struct.pack("iii", self.vertex1.id, self.vertex2.id, self.vertex3.id)
    
	def to_cal3d_xml(self):
		return "    <FACE VERTEXID=\"%i %i %i\"/>\n" % \
			(self.vertex1.id, self.vertex2.id, self.vertex3.id)
    
class Skeleton:
	def __init__(self):
		self.bones = []
    
		self.next_bone_id = 0
    
	def to_cal3d(self):
		s = "CSF\0" + struct.pack("ii", CAL3D_VERSION, len(self.bones))
		s += "".join(map(Bone.to_cal3d, self.bones))
		return s

	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XSF\" VERSION=\"%i\"/>\n" % CAL3D_XML_VERSION
		s += "<SKELETON NUMBONES=\"%i\">\n" % len(self.bones)
		s += "".join(map(Bone.to_cal3d_xml, self.bones))
		s += "</SKELETON>\n"
		return s

BONES = {}

class Bone:
	def __init__(self, skeleton, parent, name, loc, quat):
		self.parent = parent
		self.name = name
		self.loc = loc.copy()
		self.quat = quat.copy()
		self.children = []

		# calculate absolute rotation matrix
		matrix = quat.toMatrix()
		if parent:
			self.matrix = parent.matrix * matrix
			parent.children.append(self)
		else:
			self.matrix = matrix.copy()

		#calculate absolute translaton vector
		if parent:
			self.abs_trans = parent.abs_trans + parent.matrix * self.loc
		else:
			self.abs_trans = self.loc
		
		# lloc and lquat are the model => bone space transformation 
		m = self.matrix.copy()
		m.invert()
		self.lquat = m.toQuat()
		self.lloc = m * (-self.abs_trans)
		
		self.skeleton = skeleton
		self.id = skeleton.next_bone_id
		skeleton.next_bone_id += 1
		skeleton.bones.append(self)
    
		BONES[self.name] = self
    
	def to_cal3d(self):
		s = struct.pack("i", len(self.name) + 1) + self.name + "\0"
		s += struct.pack("ffffffffffffff", self.loc[0], self.loc[1], self.loc[2],
			self.quat.x, self.quat.y, self.quat.z, self.quat.w,
			self.lloc[0], self.lloc[1], self.lloc[2],
			self.lquat.x, self.lquat.y, self.lquat.z, self.lquat.w)
		if self.parent:
			s += struct.pack("i", self.parent.id)
		else:
			s += struct.pack("i", -1)
		s += struct.pack("i", len(self.children))
		s += "".join(map(lambda bone: struct.pack("i", bone.id), self.children))
		return s
  
	def to_cal3d_xml(self):
		s = "  <BONE ID=\"%i\" NAME=\"%s\" NUMCHILDS=\"%i\">\n" % \
			(self.id, self.name, len(self.children))
		s += "    <TRANSLATION>%f %f %f</TRANSLATION>\n" % \
			(self.loc[0], self.loc[1], self.loc[2])
		s += "    <ROTATION>%f %f %f %f</ROTATION>\n" % \
			(self.quat.x, self.quat.y, self.quat.z, self.quat.w)
		s += "    <LOCALTRANSLATION>%f %f %f</LOCALTRANSLATION>\n" % \
			(self.lloc[0], self.lloc[1], self.lloc[2])
		s += "    <LOCALROTATION>%f %f %f %f</LOCALROTATION>\n" % \
			(self.lquat.x, self.lquat.y, self.lquat.z, self.lquat.w)
		if self.parent:
			s += "    <PARENTID>%i</PARENTID>\n" % self.parent.id
		else:
			s += "    <PARENTID>%i</PARENTID>\n" % -1
		s += "".join(map(lambda bone: "    <CHILDID>%i</CHILDID>\n" % bone.id,
			self.children))
		s += "  </BONE>\n"
		return s
  
class Animation:
	def __init__(self, name, action, duration = 0.0):
		self.name = name
		self.action = action
		self.duration = duration
		self.tracks = {} # Map bone names to tracks
    
	def to_cal3d(self):
		s = "CAF\0" + struct.pack("ifi", 
			CAL3D_VERSION, self.duration, len(self.tracks))
		s += "".join(map(Track.to_cal3d, self.tracks.values()))
		return s
    
	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XAF\" VERSION=\"%i\"/>\n" % CAL3D_XML_VERSION
		s += "<ANIMATION DURATION=\"%f\" NUMTRACKS=\"%i\">\n" % \
			(self.duration, len(self.tracks))
		s += "".join(map(Track.to_cal3d_xml, self.tracks.values()))
		s += "</ANIMATION>\n"
		return s
    
class Track:
	def __init__(self, animation, bone):
		self.bone = bone
		self.keyframes = []
    
		self.animation = animation
		animation.tracks[bone.name] = self
    
	def to_cal3d(self):
		s = struct.pack("ii", self.bone.id, len(self.keyframes))
		s += "".join(map(KeyFrame.to_cal3d, self.keyframes))
		return s
    
	def to_cal3d_xml(self):
		s = "  <TRACK BONEID=\"%i\" NUMKEYFRAMES=\"%i\">\n" % \
			(self.bone.id, len(self.keyframes))
		s += "".join(map(KeyFrame.to_cal3d_xml, self.keyframes))
		s += "  </TRACK>\n"
		return s
    
class KeyFrame:
	def __init__(self, track, time, loc, quat):
		self.time = time
		self.loc = loc.copy()
		self.quat = quat.copy()
    
		self.track = track
		track.keyframes.append(self)
    
	def to_cal3d(self):
		return struct.pack("ffffffff", self.time, self.loc[0], self.loc[1], 
			self.loc[2], self.quat.x, self.quat.y, self.quat.z, self.quat.w)

	def to_cal3d_xml(self):
		s = "    <KEYFRAME TIME=\"%f\">\n" % self.time
		s += "      <TRANSLATION>%f %f %f</TRANSLATION>\n" % \
			(self.loc[0], self.loc[1], self.loc[2])
		s += "      <ROTATION>%f %f %f %f</ROTATION>\n" % \
			(self.quat.x, self.quat.y, self.quat.z, self.quat.w)
		s += "    </KEYFRAME>\n"
		return s


def calculate_base_translation(scene):
	base_translation = Blender.Mathutils.Vector([0,0,0])
	armature_translation = Blender.Mathutils.Vector([0,0,0])
	root_bone_translation = Blender.Mathutils.Vector([0,0,0])
	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			armature_translation = obj.getMatrix().translationPart()
			
			for b in data.bones.values():
				if not b.hasParent():
					root_bone_translation = b.head['BONESPACE'].copy()
					rotation = obj.getMatrix().rotationPart()
					rotation.invert()
					root_bone_translation = rotation * \
						                    root_bone_translation
					break
	base_translation = armature_translation + root_bone_translation
	base_translation.negate()
	return base_translation.copy()


def get_armature_translation(scene):
	armature_translation = Blender.Mathutils.Vector([0,0,0])
	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			armature_translation = obj.getMatrix().translationPart()
	return armature_translation.copy()


def treat_bone(b, base_matrix, arm_matrix, parent, skeleton, scene):
	global SCALE
	global ROOT_TO_ZERO

	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0: return
	if b.name[0] == '_' : return
	name = b.name

	bone_head = b.head['BONESPACE'].copy()
	bone_tail = b.tail['BONESPACE'].copy()

	if not ROOT_TO_ZERO and not parent:
		bone_tail = bone_tail - bone_head
		bone_head = bone_head + \
		            arm_matrix.rotationPart()*get_armature_translation(scene)
		bone_tail = bone_tail + bone_head

	if bone_head.length != 0: 
		if not ROOT_TO_ZERO and not parent:
			if base_matrix and arm_matrix:
				dummy_arm_matrix = arm_matrix.copy()
				dummy_arm_matrix.invert()
				dummy_base_matrix = base_matrix.copy()
				dummy_base_matrix.invert()
				result_matrix = dummy_base_matrix * dummy_arm_matrix
				tmp_quat = result_matrix.toQuat()
			else:
				tmp_quat = Blender.Mathutils.Quaternion()

			tmp_loc = Blender.Mathutils.Vector([0.0,0.0,0.0])
			parent = Bone(skeleton, None, "service_root",
			              tmp_loc.copy(), tmp_quat.copy())
			parent.child_loc = Blender.Mathutils.Vector([0.0,0.0,0.0])

		# in this case create a service 
		# bone between child and parent
		if parent:
			interm_loc = parent.child_loc.copy()

			interm_loc *= SCALE
			interm_quat = Blender.Mathutils.Quaternion()
			interm_bone = Bone(skeleton, parent, name+"_interm",
		    	               interm_loc, interm_quat)
			interm_bone.child_loc = bone_head
			parent = interm_bone
		else:
			bone_tail -= bone_head
			bone_head -= bone_head


	local_rot_mat = b.matrix['BONESPACE'].rotationPart()

	# convert to cal3d rotation
	local_rot_mat.invert()

	if base_matrix and arm_matrix and not parent:
		dummy_arm_matrix = arm_matrix.copy()
		dummy_arm_matrix.invert()
		dummy_base_matrix = base_matrix.copy()
		dummy_base_matrix.invert()
		cal3d_base_matrix = dummy_base_matrix * dummy_arm_matrix
		local_rot_mat = cal3d_base_matrix.rotationPart() * local_rot_mat

	if parent:
		loc = parent.child_loc.copy()
	else:
		loc = Blender.Mathutils.Vector([0.0,0.0,0.0])


	loc *= SCALE
	quat = local_rot_mat.toQuat()
	bone = Bone(skeleton, parent, name, loc, quat)

	# if I got it right, root bone
	# shouldn't have translation =>
	# moving all translations one 
	# bone forward
	bone.child_loc = bone_tail - bone_head
	bone_matrix = b.matrix['BONESPACE'].rotationPart()
	bone.child_loc = bone_matrix * bone.child_loc

	has_children = False
	if b.hasChildren():
		for child in b.children:
			if len(child.name):
				if child.name[0] != '_':
					has_children = True
					break
	
	if has_children:
		for child in b.children:
			treat_bone(child, base_matrix.copy(), arm_matrix.copy(), 
			           bone, skeleton, scene)
	else:
		# service bone for skeletons to look the 
		# same both in Blender and cal3d
		ender_loc = bone.child_loc.copy()
		ender_loc *= SCALE
		ender_quat = Blender.Mathutils.Quaternion()
		Bone(skeleton, bone, name+"_ender", ender_loc, ender_quat)


def create_actions_dict():
	global BONES

	legal_curve_types = ("LocX", "LocY", "LocZ", 
		                   "QuatX", "QuatY", "QuatZ", "QuatW")
	arm_actions_dict = {}

	blender_actions = Blender.Armature.NLA.GetActions()
	for name, action in blender_actions.items():
		if len(name) == 0:
			continue
		# skip actions that are named _something
		if name[0] == "_":
			print "skipping animation ", name
			continue
		
		# check if this action has channels for 
		# our armature bones
		belongs_to_armature = False
		for channel_name in action.getChannelNames():
			if channel_name in BONES.keys():
				belongs_to_armature = True
				break
		if not belongs_to_armature:
			continue

		arm_tracks_dict = {}
		
		ok_to_add = True
		for channel_name in action.getChannelNames():
			if not channel_name in BONES.keys():
				continue

			# get rotation and translation keyframes
			keyframes = []
			
			ipo = action.getChannelIpo(channel_name)
			for curve in ipo.curves:
				if curve.name in legal_curve_types:
					for point in curve.bezierPoints:
						keyframes.append(point.vec[1][0])
				else:
					ok_to_add = False

			# remove double keyframes
			keyframes_set = set(keyframes)
			keyframes = []
			for keyframe in keyframes_set:
				keyframes.append(keyframe)
			keyframes.sort()

			arm_tracks_dict[channel_name] = keyframes

		if ok_to_add:
			arm_actions_dict[name] = arm_tracks_dict
		else:
			print "skipping animation", name,": incorrect keyframe types"
	return arm_actions_dict


def popup_block(header, body):
	global STATUS
	block = []
	block.append(header)
	Blender.Draw.PupBlock("Export message", block)
	STATUS = body
	Draw()


def scene_is_ok(scene):
	armatures_num = 0
	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			armatures_num += 1
	
	if armatures_num != 1:
		popup_block("Export error", 
		            "only 1 armature allowed, found %d armatrues" 
		            % (armatures_num))
		return False

	for obj in scene.objects:
		data = obj.getData()
		root_bones_names = []
		if type(data) is Blender.Types.ArmatureType:
			arm_scale = obj.getMatrix().scalePart()
			if (abs(arm_scale.x - 1.0) > 0.001 or
			    abs(arm_scale.y - 1.0) > 0.001 or
				abs(arm_scale.z - 1.0) > 0.001):
				popup_block("Skeleton export error",
				            "Armature is scaled (%f, %f, %f)" % 
							(arm_scale.x, arm_scale.y, arm_scale.z))
				return False
			root_bones_num = 0
			for b in data.bones.values():
				if not b.hasParent() and b.name[0] != "_":
					root_bones_names.append(b.name)
					root_bones_num += 1

			if root_bones_num != 1:
				error_string = "only 1 root bone allowed, found %d root bones: "\
				               % (root_bones_num)
				for root_bone_name in root_bones_names:
					error_string += "[%s] " % (root_bone_name)
				popup_block("Skeleton export error", 
				            error_string)
				return False
	return True


def export_skeleton(scene, base_matrix):
	global BONES

	skeleton = Skeleton()
	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			arm_matrix = obj.getMatrix().copy()
			
			for b in data.bones.values():
				if not b.hasParent() and not BONES.has_key(b.name) \
				   and b.name[0] != "_":
					treat_bone(b, base_matrix.copy(), arm_matrix.copy(),
					           None, skeleton, scene)
					break
	return skeleton




def export_animations(scene):
	global BONES, ANIMATIONS

	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			armature_obj = obj

	actions = {}
	for action_name, bones_dict in create_actions_dict().items():
		tracks = {}
		for bone_name, keytimes_list in bones_dict.items():
			keyframes_list = []
			for keytime in keytimes_list:
				action = Blender.Armature.NLA.GetActions()[action_name]
				action.setActive(armature_obj)
				armature_obj.evaluatePose(keytime)
				pose = armature_obj.getPose()
				pose_bone = pose.bones[bone_name]
				keyframes_list.append(((keytime - 1.0)/FPS, 
				                      pose_bone.loc.copy(), 
				                      pose_bone.quat.copy()))
			tracks[bone_name] = keyframes_list
		actions[action_name] = tracks

	for action_name, bones in actions.items():
		# it can be a single action, or an animation loop
		# if its name begins with @ then it is an action
		# otherwise it's an animation loop
		is_action = False
		if action_name[0] == '@':
			action_name = action_name.split("@")[1]
			is_action = True

		if REMOVE_BAKED:
			action_name = "".join(action_name.split('.BAKED'))


		# check for duplicate animation names and work around
		if action_name in ANIMATIONS.keys():
			print "Warning %s already exists!! renaming" % action_name
			test = action_name
			suffix = 1
			while test in ANIMATIONS.keys():
				test = "%s__%i" % (action_name, suffix)
				suffix += 1
			
		animation = ANIMATIONS[action_name] = Animation(action_name, is_action)
		for bone_name, keyframes_list in bones.items():
			bone = BONES[bone_name]
			track = animation.tracks[bone_name] = Track(animation, bone)
			for time, loc, quat in keyframes_list:
				loc *= SCALE
				loc += bone.loc
				# to cal3d rotation
				quat.inverse()
				quat = quat.cross(bone.quat)
				KeyFrame(track, time, loc, quat)
				if time > animation.duration:
					animation.duration = time


def export_materials():
	global NEXT_MATERIAL_ID
	NEXT_MATERIAL_ID = 0

	for obj in Blender.Material.Get():
		data = obj
		if type(data) is Blender.Types.MaterialType:
			if obj.name[0] == '_':
				print "Skipping material", obj.name
				continue
              
			# Material stores it in MATERIALS
			material = Material(obj.name)

			amb  = map(lambda x: int(x*255), Blender.World.GetActive().getAmb() + [1.0])
			rgba = map(lambda x: int(x*255), data.getRGBCol() + [data.getAlpha()])
			spec = map(lambda x: int(x*255), data.getSpecCol() + [data.getAlpha()])

			material.shininess = data.getSpec()
			material.diffuse_r = rgba[0]
			material.diffuse_g = rgba[1]
			material.diffuse_b = rgba[2]
			material.diffuse_a = rgba[3]
			material.ambient_r = amb[0]
			material.ambient_g = amb[1]
			material.ambient_b = amb[2]
			material.ambient_a = amb[3]            
			material.specular_r = spec[0]
			material.specular_g = spec[1]
			material.specular_b = spec[2]
			material.specular_a = spec[3]
          
			# Just gets the image for each texture, ignoring
			# all the possible blending flags.
			for mtex in data.getTextures():
				if mtex == None:
					continue
				tex = mtex.tex
				if tex.getType() != "Image":
					print "Warning: Non-image texture", tex.name, "will be ignored."
					continue
				image = tex.getImage()
				if image != None:
					filename = image.filename
					if REMOVE_PATH_FROM_IMAGE:
						if image.filename[0] == "/":
							tmplist = image.filename.split("/")
						else:
							tmplist = image.filename.split("\\")
						filename = IMAGE_PREFIX + tmplist[-1] 
					material.maps_filenames.append(filename)
                  


def get_armature_matrix(scene):
	for obj in scene.objects:
		data = obj.getData()
		if type(data) is Blender.Types.ArmatureType:
			matrix = obj.getMatrix().copy()
			matrix.resize4x4()
			return matrix


def export_meshes(scene, base_matrix, base_translation):
	global MATERIALS, BONES, MESHES

	bad_vgs = []

	base_matrix.invert()

	for obj in scene.objects:
		data = obj.getData()
		if (type(data) is Blender.Types.NMeshType) and data.faces:
			mesh = Mesh(obj.name)

			if mesh.name[0] == '_' :
				print "skipping object ", mesh.name
				continue

			# Update materials list from the actual mesh
			MESHES.append(mesh)
			mat_list = data.getMaterials(1) 
		
			print "base translation is:", base_translation

			matrix = obj.mat.copy()
			matrix.resize4x4()


			backup_verts = data.verts[:]

			data.transform(matrix, True)

			faces = data.faces
			while faces:
				mat_index = faces[0].mat
				material = None
				if mat_index < len(mat_list):
					if mat_list[mat_index].name in MATERIALS.keys():
						material = MATERIALS[mat_list[mat_index].name]
				
				material_id = -1
				if material:
					material_id = material.id

				submesh = SubMesh(mesh, material_id)
				vertices = {}
				for face in faces[:]:
					if face.mat == mat_index:
						faces.remove(face)
            
						if not face.smooth:
							v1 = face.v[1].co - face.v[2].co
							v2 = face.v[0].co - face.v[1].co
							normal = v2.cross(v1)
							normal = base_matrix * normal
							normal *= SCALE # for mirror transformations
							normal.normalize()
							
						
						face_vertices = []
						for i in range(len(face.v)):
							vertex = vertices.get(face.v[i].index)
							if not vertex:
								coord = face.v[i].co.copy()
								coord += base_translation
								coord = base_matrix * coord
								coord *= SCALE

								normal = Blender.Mathutils.Vector([0.0, 1.0, 0.0])

								if face.smooth:
									if face.v[i].no[0] == 0 and face.v[i].no[1] == 0 and face.v[i].no[1] == 0: 
										print "FOUND 0 vector normalgaa"
									else:
										normal = face.v[i].no.copy()
										normal = base_matrix * normal
										normal *= SCALE
										normal.normalize()
								vertex = vertices[face.v[i].index] = Vertex(submesh, coord, normal)
								influences = data.getVertexInfluences(face.v[i].index)
								if not influences:
									print "Warning: vertex %i (%i) has no influence !" % \
										(face.v[i].index, face.v[i].sel)
                
								# sum of influences is not always 1.0 in Blender ?!?!
								sum = 0.0
								for bone_name, weight in influences:
									if BONES.has_key(bone_name):
										sum += weight
                
								# Select vertex with no weight at all (sum = 0.0).
								# To find out which one it is, select part of vertices in mesh,
								# exit editmode and see if value between brackets is 1. If so,
								# the vertex is in selection. You can narrow the selection
								# this way, to find the offending vertex...
								if sum == 0.0:
									print "Warning: vertex %i in mesh %s (selected: %i) has influence sum of 0.0!" % \
									      (face.v[i].index, mesh.name, face.v[i].sel)
									print "Set the sum to 1.0, otherwise there will " + \
									      "be a division by zero. Better find the offending " + \
									      "vertex..."
									# face.v[i].sel = 1 # does not work???
									sum = 1.0

								#if face.v[i].sel:
								#	print "In mesh: %s, Vertex %i is selected" % (mesh.name, face.v[i].index)
                    
								for bone_name, weight in influences:
									if BONES.has_key(bone_name):
										vertex.influences.append(Influence(BONES[bone_name], 
										                         weight / sum))
									else:
										if bone_name not in bad_vgs:
											print "Warning: vertex group %s on mesh %s doesn't correspond to a bone. It will be ignored." % \
											      (bone_name, mesh.name)
											bad_vgs.append(bone_name)

							if data.hasFaceUV():
								uv = [face.uv[i][0], 1.0 - face.uv[i][1]]
								if not vertex.maps:
									vertex.maps.append(Map(*uv))
								elif (vertex.maps[0].u != uv[0]) or (vertex.maps[0].v != uv[1]):
									# This vertex can be shared for Blender, but not for Cal3D !!!
									# Cal3D does not support vertex sharing for 2 vertices with
									# different UV texture coodinates.
									# => we must clone the vertex.
									for clone in vertex.clones:
										if (clone.maps[0].u == uv[0]) and \
											(clone.maps[0].v == uv[1]):
											vertex = clone
											break
									else: # Not yet cloned...
										old_vertex = vertex
										vertex = Vertex(submesh, vertex.loc, vertex.normal)
										vertex.cloned_from = old_vertex
										vertex.influences = old_vertex.influences
										vertex.maps.append(Map(*uv))
										old_vertex.clones.append(vertex)


							face_vertices.append(vertex)

						# Split faces with more than 3 vertices
						for i in range(1, len(face.v) - 1):
							Face(submesh, face_vertices[0], face_vertices[i],
							     face_vertices[i + 1])

				data.verts = backup_verts

				# Computes LODs info
				if LODS:
					submesh.compute_lods()
					faces.reverse()



def export():
	global STATUS, ROT_X, ROT_Y, ROT_Z, SCALE
	global BONES, MATERIALS, ANIMATIONS, MESHES
	global ROOT_TO_ZERO
	
	STATUS = "Start export..."
	Draw()

	rot_x_matrix = Blender.Mathutils.RotationMatrix(ROT_X, 4, "x")
	rot_y_matrix = Blender.Mathutils.RotationMatrix(ROT_Y, 4, "y")
	rot_z_matrix = Blender.Mathutils.RotationMatrix(ROT_Z, 4, "z")

	# Get the scene
	scene = Blender.Scene.getCurrent()

	# Reset the globals
	BONES = {}
	MATERIALS = {}
	ANIMATIONS = {}
	MESHES = []
  
	STATUS = "Checking scene"
	Draw()

	if not scene_is_ok(scene):
		Draw()
		return

	BASE_MATRIX = rot_z_matrix * rot_y_matrix * rot_x_matrix

	if ROOT_TO_ZERO:
		BASE_TRANSLATION = calculate_base_translation(scene)
	else:
		BASE_TRANSLATION = Blender.Mathutils.Vector([0.0, 0.0, 0.0])
		

	STATUS = "Calculate skeleton"
	Draw()

	skeleton = export_skeleton(scene, BASE_MATRIX.copy())

	STATUS = "Calculate animations"
	Draw()
	export_animations(scene)


	# Export material data
	if EXPORT_MATERIAL:
		STATUS = "Calculate materials"
		Draw()
		export_materials()
      

	# Export Mesh data
	if EXPORT_MESH:
		STATUS = "Calculate meshes"
		Draw()
		export_meshes(scene, BASE_MATRIX.copy(),
		              BASE_TRANSLATION.copy())

	# Save all data
	STATUS = "Save files"
	Draw()

	EXPORT_ALL = EXPORT_SKELETON and EXPORT_ANIMATION and \
		EXPORT_MESH and EXPORT_MATERIAL
	cfg_buffer = ""

	if FILE_PREFIX == "":
		std_fname = "cal3d"
	else:
		std_fname = ""
  
	if not os.path.exists(SAVE_TO_DIR):
		try:
			os.makedirs(SAVE_TO_DIR)
		except os.error:
			popup_block("Export error", 
			            "failed to create dir \"%s\"" 
			            % (SAVE_TO_DIR))
			Draw()
			return
			
	else:
		if DELETE_ALL_FILES:
			for file in os.listdir(SAVE_TO_DIR):
				if file.endswith(".cfg") or file.endswith(".caf") or \
					file.endswith(".cmf") or file.endswith(".csf") or \
					file.endswith(".crf") or file.endswith(".xsf") or \
					file.endswith(".xaf") or file.endswith(".xmf") or \
					file.endswith(".xrf"):
					os.unlink(os.path.join(SAVE_TO_DIR, file))
        
	cfg_buffer += "# Cal3D model exported from Blender with blender2cal3d.py\n\n"
	if not EXPORT_ALL:
		cfg_buffer += "# Append this file to the model configuration file\n\n"
  
	if EXPORT_SKELETON:
		cfg_buffer += "# --- Skeleton ---\n"
		if EXPORT_TO_XML:
		 	f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + FILE_SKELETONNAME + \
				".xsf"), "wb")
			if f:
				f.write(skeleton.to_cal3d_xml())
				cfg_buffer += "skeleton=%s.xsf\n" %  (FILE_PREFIX + FILE_SKELETONNAME)
			else:
				popup_block("Export error", 
				            "failed to open %s" 
				            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
				            FILE_SKELETONNAME + ".xsf")))
				Draw()
				return
		else:
			f = open(os.path.join(SAVE_TO_DIR,  FILE_PREFIX + FILE_SKELETONNAME + \
				".csf"), "wb")
			if f:
				f.write(skeleton.to_cal3d())
				cfg_buffer += "skeleton=%s.csf\n" %  (FILE_PREFIX + FILE_SKELETONNAME)
			else:
				popup_block("Export error", 
				            "failed to open %s" 
				            % (os.path.join(SAVE_TO_DIR,  FILE_PREFIX + \
				                            FILE_SKELETONNAME + ".csf")))
				Draw()
				return
		cfg_buffer += "\n"
  
	if EXPORT_ANIMATION:
		cfg_buffer += "# --- Animations ---\n"
		for animation in ANIMATIONS.values():
      # Cal3D does not support animation with only one state
			if animation.duration:
				animation.name = RENAME_ANIMATIONS.get(animation.name) or animation.name

				action_suffix=""
				if animation.action:
					action_suffix = "_action"

				if EXPORT_TO_XML:
					f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
						animation.name + ".xaf"), "wb")
					if f:
						f.write(animation.to_cal3d_xml())
						cfg_buffer += "animation%s=%s.xaf\n" % (action_suffix, (FILE_PREFIX + animation.name))
					else:
						popup_block("Export error", 
						            "failed to open %s" 
						            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
						               animation.name + ".xaf")))
						Draw()
						return
				else:
					f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
					         animation.name + ".caf"), "wb")
					if f:
						f.write(animation.to_cal3d())
						cfg_buffer += "animation%s=%s.caf\n" % (action_suffix, (FILE_PREFIX + animation.name))
					else:
						popup_block("Export error", 
						            "failed to open %s" 
						            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
						               animation.name + ".caf")))
						Draw()
						return


		cfg_buffer += "\n"

	if EXPORT_MESH:
		cfg_buffer += "# --- Meshes ---\n"
		for mesh in MESHES:
			if not mesh.name.startswith("_"):
				if EXPORT_TO_XML:
					f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + mesh.name + ".xmf"),
						"wb")
					if f:
						f.write(mesh.to_cal3d_xml())
						cfg_buffer += "mesh=%s.xmf\n" % (FILE_PREFIX + mesh.name)
					else:
						popup_block("Export error", 
						            "failed to open %s" 
						            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
									  mesh.name + ".xmf")))
						Draw()
						return
				else:
					f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + mesh.name + ".cmf"),
						"wb")
					if f:
						f.write(mesh.to_cal3d())
						cfg_buffer += "mesh=%s.cmf\n" % (FILE_PREFIX + mesh.name)
					else:
						popup_block("Export error", 
						            "failed to open %s" 
						            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
						               mesh.name + ".cmf")))
						Draw()
						return
		cfg_buffer += "\n"
  
	if EXPORT_MATERIAL:
		cfg_buffer += "# --- Materials ---\n"
		materials = MATERIALS.values()
		materials.sort(lambda a, b: cmp(a.id, b.id))
		for material in materials:
			if material.maps_filenames:
				fname = os.path.splitext(os.path.basename(material.maps_filenames[0]))[0]
			else:
				fname = "plain"
			if EXPORT_TO_XML:
				f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + fname + ".xrf"),
					"wb")
				if f:
					f.write(material.to_cal3d_xml())
					cfg_buffer += "material=%s.xrf\n" % (FILE_PREFIX + fname)
				else:
					popup_block("Export error", 
					            "failed to open %s" 
					            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
					               fname + ".xrf")))
					Draw()
					return
			else:
				f = open(os.path.join(SAVE_TO_DIR, FILE_PREFIX + fname + ".crf"),
					"wb")
				if f:
					f.write(material.to_cal3d())
					cfg_buffer += "material=%s.crf\n" % (FILE_PREFIX + fname)
				else:
					popup_block("Export error", 
					            "failed to open %s" 
					            % (os.path.join(SAVE_TO_DIR, FILE_PREFIX + \
					               fname + ".crf")))
					Draw()
					return
		cfg_buffer += "\n"

	if EXPORT_ALL:
		cfg_prefix = ""
	else:
		cfg_prefix = "append_to_"

	cfg = open(os.path.join(SAVE_TO_DIR, cfg_prefix + FILE_PREFIX + std_fname +\
		os.path.basename(SAVE_TO_DIR) + ".cfg"), "wb")
	if cfg:
		print >> cfg, cfg_buffer
		cfg.close()

		print "Saved to", SAVE_TO_DIR
		print "Done."

		STATUS = "Export finished."
	else:
		popup_block("Export error", 
		            "failed to open %s" 
		            % (os.path.join(SAVE_TO_DIR, cfg_prefix + FILE_PREFIX + std_fname +\
		               os.path.basename(SAVE_TO_DIR) + ".cfg")))
	Draw()


# ::: GUI around the whole thing, not very clean, but it works for me...
# Alexey: works for me too (=

_save_dir = Create(SAVE_TO_DIR)
_file_prefix = Create(FILE_PREFIX)
_image_prefix = Create(IMAGE_PREFIX)
_scale = Create(SCALE)
_rot_x = Create(ROT_X)
_rot_y = Create(ROT_Y)
_rot_z = Create(ROT_Z)
_framepsec = Create(FPS)
STATUS = "Done nothing yet"

def gui():
	global EXPORT_TO_XML, EXPORT_SKELETON, EXPORT_ANIMATION, EXPORT_MESH, \
		EXPORT_MATERIAL, SAVE_TO_DIR, _save_dir, \
		REMOVE_PATH_FROM_IMAGE, LODS, _file_prefix, \
		FILE_PREFIX, _image_prefix, IMAGE_PREFIX, DELETE_ALL_FILES, STATUS, \
		_framepsec, FPS, \
		ROT_X, ROT_Y, ROT_Z, SCALE, ROOT_TO_ZERO, \
		_scale, _rot_x, _rot_y, _rot_z, \
		CHANGE_SCALE_EVENT_ID, CHANGE_ROT_X_EVENT_ID, \
		CHANGE_ROT_Y_EVENT_ID, CHANGE_ROT_Z_EVENT_ID, \
		CHANGE_RTZ_EVENT_ID

	glRasterPos2i(8, 14)
	Text("Status: %s" % STATUS)

	_export_button = Button("Export (E)", 1, 8, 36, 150, 20, 
		"Start export to Cal3D format")
	_quit_button = Button("Quit (Q)", 5, 158, 36, 150, 20, "Exit from script")

	_delete_toggle = Toggle("X", 15, 8, 64, 20, 20, DELETE_ALL_FILES, 
		"Delete all existing Cal3D files in export directory")
	_SF_toggle = Toggle("_SF", 6, 28, 64, 70, 20, EXPORT_SKELETON, 
		"Export skeleton (CSF/XSF)")
	_AF_toggle = Toggle("_AF", 7, 98, 64, 70, 20, EXPORT_ANIMATION, 
		"Export animations (CAF/XAF)")
	_MF_toggle = Toggle("_MF", 8, 168, 64, 70, 20, EXPORT_MESH, 
		"Export mesh (CMF/XMF)")
	_RF_toggle = Toggle("_RF", 9, 238, 64, 70, 20, EXPORT_MATERIAL, 
		"Export materials (CRF/XRF)")

	_XML_toggle = Toggle("Export to XML", 2, 8, 84, 150, 20, EXPORT_TO_XML, 
		"Export to Cal3D XML or binary fileformat")
	
	_RTZ_toggle = Toggle("Root to (0,0,0)", CHANGE_RTZ_EVENT_ID, \
	                     158, 84, 150, 20,
	                     ROOT_TO_ZERO,
		"Translate model & skeleton so that root bone will be at (0,0,0)")

	_imagepath_toggle = Toggle("X imagepath", 11, 8, 104, 150, 20, 
		REMOVE_PATH_FROM_IMAGE, "Remove path from imagename")
	_lods_toggle = Toggle("Calculate LODS", 12, 158, 104, 150, 20, 
		LODS, "Calculate LODS, quit slow and not optimal")

	_scale = Number("Scale:", CHANGE_SCALE_EVENT_ID, \
		            8, 155, 300, 20, \
		            SCALE, -100.0, 100.0, \
	                "Sets the scale")

	_rot_x = Number("RotX:", CHANGE_ROT_X_EVENT_ID, \
		            8, 175, 100, 20, \
		            ROT_X, -360.0, 360.0, \
	                "Sets the rotation around X axis (degrees)")

	_rot_y = Number("RotY:", CHANGE_ROT_Y_EVENT_ID, \
		            108, 175, 100, 20, \
		            ROT_Y, -360.0, 360.0, \
	                "Sets the rotation around Y axis (degrees)")

	_rot_z = Number("RotZ:", CHANGE_ROT_Z_EVENT_ID, \
		            208, 175, 100, 20, \
		            ROT_Z, -360.0, 360.0, \
	                "Sets the rotation around Z axis (degrees)")

	_framepsec = Slider("F:", 16, 8, 132, 300, 20, FPS, 0.00, 100.0, 0, \
		"Sets the export framerate (FPS)")

	_image_prefix = String("Image prefix: ", 13, 8, 200, 300, 20, IMAGE_PREFIX, \
		256, "Prefix used for imagename (if you have the " + \
		"textures in a subdirectory called textures, " + \
		"the prefix would be \"textures\\\\\")")

	_file_prefix = String("File prefix: ", 14, 8, 220, 300, 20, FILE_PREFIX, \
		256, "Prefix to all exported Cal3D files "+ \
		"(f.e. \"model_\")")

	_save_dir = String("Export to: ", 3, 8, 240, 300, 20, SAVE_TO_DIR, 256, \
		"Directory to save files to")



def event(evt, val):
	global STATUS

	if (evt == QKEY or evt == ESCKEY):
		update_reg()
		Exit()
		return
	if evt == EKEY:
		update_reg()
		export()

def bevent(evt):
	global EXPORT_TO_XML, EXPORT_SKELETON, EXPORT_ANIMATION, EXPORT_MESH, \
		EXPORT_MATERIAL, _save_dir, SAVE_TO_DIR, \
		REMOVE_PATH_FROM_IMAGE, LODS, _file_prefix, \
		FILE_PREFIX, _image_prefix, IMAGE_PREFIX, DELETE_ALL_FILES, STATUS, \
		_framepsec, FPS, \
		ROT_X, ROT_Y, ROT_Z, SCALE, ROOT_TO_ZERO, \
		_rot_x, _rot_y, _rot_z, _scale, \
		CHANGE_SCALE_EVENT_ID, CHANGE_ROT_X_EVENT_ID, \
		CHANGE_ROT_Y_EVENT_ID, CHANGE_ROT_Z_EVENT_ID, \
		CHANGE_RTZ_EVENT_ID

	update_reg()

	if evt == 1:
		export()
	if evt == 2:
		EXPORT_TO_XML = 1 - EXPORT_TO_XML
	if evt == 3:
		SAVE_TO_DIR = _save_dir.val
	if evt == 5:
		Exit()
		return
	if evt == 6:
		EXPORT_SKELETON = 1 - EXPORT_SKELETON
	if evt == 7:
		EXPORT_ANIMATION = 1 - EXPORT_ANIMATION
	if evt == 8:
		EXPORT_MESH = 1 - EXPORT_MESH
	if evt == 9:
		EXPORT_MATERIAL = 1 - EXPORT_MATERIAL
	if evt == 11:
		REMOVE_PATH_FROM_IMAGE = 1 - REMOVE_PATH_FROM_IMAGE
	if evt == 12:
		LODS = 1 - LODS
	if evt == 13:
		IMAGE_PREFIX = _image_prefix.val
	if evt == 14:
		FILE_PREFIX = _file_prefix.val
	if evt == 15:
		DELETE_ALL_FILES = 1 - DELETE_ALL_FILES
	if evt == 16:
		FPS = _framepsec.val
	if evt == CHANGE_ROT_X_EVENT_ID:
		ROT_X = _rot_x.val
	if evt == CHANGE_ROT_Y_EVENT_ID:
		ROT_Y = _rot_y.val
	if evt == CHANGE_ROT_Z_EVENT_ID:
		ROT_Z = _rot_z.val
	if evt == CHANGE_SCALE_EVENT_ID:
		SCALE = _scale.val
	if evt == CHANGE_RTZ_EVENT_ID:
		ROOT_TO_ZERO = 1 - ROOT_TO_ZERO
	Draw()

def update_reg():
	global SAVE_TO_DIR, DELETE_ALL_FILES, EXPORT_SKELETON,               \
	       EXPORT_ANIMATION, EXPORT_MESH, EXPORT_MATERIAL, FILE_PREFIX,  \
	       REMOVE_PATH_FROM_IMAGE, IMAGE_PREFIX, EXPORT_TO_XML,          \
	       FPS, LODS, ROT_X, ROT_Y, ROT_Z, SCALE, ROOT_TO_ZERO
	
	x = {}
	x['sd'] = SAVE_TO_DIR
	x['da'] = DELETE_ALL_FILES
	x['es'] = EXPORT_SKELETON
	x['ea'] = EXPORT_ANIMATION
	x['em'] = EXPORT_MESH
	x['emat'] = EXPORT_MATERIAL
	x['fp'] = FILE_PREFIX
	x['rp'] = REMOVE_PATH_FROM_IMAGE
	x['ip'] = IMAGE_PREFIX
	x['ex'] = EXPORT_TO_XML
	x['fps'] = FPS
	x['lod'] = LODS
	x['rotx'] = ROT_X
	x['roty'] = ROT_Y
	x['rotz'] = ROT_Z
	x['scale'] = SCALE
	x['rtz'] = ROOT_TO_ZERO

	Blender.Registry.SetKey('Cal3dExporter', x)

def get_from_reg():
	global SAVE_TO_DIR, DELETE_ALL_FILES, EXPORT_SKELETON,               \
	       EXPORT_ANIMATION, EXPORT_MESH, EXPORT_MATERIAL, FILE_PREFIX,  \
	       REMOVE_PATH_FROM_IMAGE, IMAGE_PREFIX, EXPORT_TO_XML,          \
	       FPS, LODS, ROT_X, ROT_Y, ROT_Z, SCALE, ROOT_TO_ZERO

	tmp = Blender.Registry.GetKey("Cal3dExporter")
	if tmp: 
		SAVE_TO_DIR = tmp['sd']
		DELETE_ALL_FILES = tmp['da']
		EXPORT_SKELETON = tmp['es']
		EXPORT_ANIMATION = tmp['ea']
		EXPORT_MESH = tmp['em']
		EXPORT_MATERIAL = tmp['emat']
		FILE_PREFIX = tmp['fp']
		REMOVE_PATH_FROM_IMAGE = tmp['rp']
		IMAGE_PREFIX = tmp['ip']
		EXPORT_TO_XML = tmp['ex']
		FPS = tmp['fps']
		LODS = tmp['lod']
		ROT_X = tmp['rotx']
		ROT_Y = tmp['roty'] 
		ROT_Z = tmp['rotz'] 
		SCALE = tmp['scale']
		ROOT_TO_ZERO = tmp['rtz']

get_from_reg()
Register(gui, event, bevent)

