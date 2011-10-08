import os
from math import *

import bpy
from mathutils import *

class Skeleton:
	def __init__(self, name, xml_version):
		self.name = name
		self.xml_version = xml_version
		self.bones = []
		self.next_bone_id = 0

	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XSF\" VERSION=\"{0}\"/>\n".format(self.xml_version)
		s += "<SKELETON NUMBONES=\"{0}\">\n".format(len(self.bones))
		s += "".join(map(Bone.to_cal3d_xml, self.bones))
		s += "</SKELETON>\n"
		return s


class Bone:
	def __init__(self, skeleton, parent, name, loc, rot):
		self.parent = parent
		self.name = name
		self.children = []
		self.xml_version = skeleton.xml_version

		self.loc = loc.copy()
		self.quat = rot.to_quaternion()

		self.matrix = Matrix.Translation(self.loc) * self.quat.to_matrix().to_4x4()
		self.inv_abs_matrix = self.matrix.inverted()

		if parent:
			parent.children.append(self)
			self.inv_abs_matrix = self.inv_abs_matrix * parent.inv_abs_matrix

		# lloc and lquat are the model => bone space transformation 
		(inv_loc, inv_rot, inv_scale) = self.inv_abs_matrix.decompose()
		self.lquat = inv_rot.copy()
		self.lloc = inv_loc.copy()
		
		self.skeleton = skeleton
		self.index = skeleton.next_bone_id
		skeleton.next_bone_id += 1
		skeleton.bones.append(self)
 

	def to_cal3d_xml(self):
		s = "  <BONE ID=\"{0}\" NAME=\"{1}\" NUMCHILDS=\"{2}\">\n".format(self.index,
		                                                                  self.name, 
		                                                                  len(self.children))

		s += "	<TRANSLATION>{0} {1} {2}</TRANSLATION>\n".format(self.loc[0],
		                                                         self.loc[1],
		                                                         self.loc[2])

		s += "	<ROTATION>{0} {1} {2} {3}</ROTATION>\n".format(self.quat.inverted().x,
		                                                       self.quat.inverted().y,
		                                                       self.quat.inverted().z,
		                                                       self.quat.inverted().w)

		s += "	<LOCALTRANSLATION>{0} {1} {2}</LOCALTRANSLATION>\n".format(self.lloc[0],
		                                                                   self.lloc[1],
		                                                                   self.lloc[2])

		s += "	<LOCALROTATION>{0} {1} {2} {3}</LOCALROTATION>\n".format(self.lquat.inverted().x, 
		                                                                 self.lquat.inverted().y,
		                                                                 self.lquat.inverted().z,
		                                                                 self.lquat.inverted().w)
		if self.parent:
			s += "	<PARENTID>{0}</PARENTID>\n".format(self.parent.index)
		else:
			s += "	<PARENTID>{0}</PARENTID>\n".format(-1)
		s += "".join(map(lambda bone: "	<CHILDID>{0}</CHILDID>\n".format(bone.index),
		             self.children))
		s += "  </BONE>\n"
		return s


