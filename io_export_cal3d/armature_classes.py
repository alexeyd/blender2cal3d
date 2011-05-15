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
		self.quat = rot.inverted().to_quaternion()

		# calculate absolute rotation matrix
		self.matrix = rot.copy()
		if parent:
			self.matrix.rotate(parent.matrix)
			parent.children.append(self)

		# calculate absolute translaton vector
		self.abs_trans = loc.copy()
		if parent:
			self.abs_trans.rotate(parent.matrix)
			self.abs_trans = self.abs_trans + parent.abs_trans
		
		# lloc and lquat are the model => bone space transformation 
		self.lquat = self.matrix.to_quaternion()
		self.lloc = -self.abs_trans
		
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

		s += "	<ROTATION>{0} {1} {2} {3}</ROTATION>\n".format(self.quat.x,
		                                                       self.quat.y,
		                                                       self.quat.z,
		                                                       self.quat.w)

		s += "	<LOCALTRANSLATION>{0} {1} {2}</LOCALTRANSLATION>\n".format(self.lloc[0],
		                                                                   self.lloc[1],
		                                                                   self.lloc[2])

		s += "	<LOCALROTATION>{0} {1} {2} {3}</LOCALROTATION>\n".format(self.lquat.x, 
		                                                                 self.lquat.y,
		                                                                 self.lquat.z,
		                                                                 self.lquat.w)
		if self.parent:
			s += "	<PARENTID>{0}</PARENTID>\n".format(self.parent.index)
		else:
			s += "	<PARENTID>{0}</PARENTID>\n".format(-1)
		s += "".join(map(lambda bone: "	<CHILDID>{0}</CHILDID>\n".format(bone.index),
		             self.children))
		s += "  </BONE>\n"
		return s


