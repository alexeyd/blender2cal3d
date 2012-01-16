import os
from array import array
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

		
	def to_cal3d_binary(self, file):
		s = b'CSF\0'
		ar = array('b', list(s))
		ar.tofile(file)
		
		ar = array('L', [1200,
						 len(self.bones)])
		ar.tofile(file)
		
		for bn in self.bones:
			bn.to_cal3d_binary(file)



class Bone:
	def __init__(self, skeleton, parent, name, loc, rot):
		'''
		loc is the translation from the parent coordinate frame to the tail of the bone
		rot is the rotation from the parent coordinate frame to the tail of the bone
		'''
		
		self.parent = parent
		self.name = name
		self.children = []
		self.xml_version = skeleton.xml_version

		self.loc = loc.copy()
		self.quat = rot.copy()
		
		# Cal3d does the vertex deform calculation by:
		#   translationBoneSpace = coreBoneTranslationBoneSpace * boneAbsRotInAnimPose + boneAbsPosInAnimPose
		#   transformMatrix = coreBoneRotBoneSpace * boneAbsRotInAnimPose
		#   v = mesh * transformMatrix + translationBoneSpace
		# To calculate "coreBoneTranslationBoneSpace" (ltrans) and "coreBoneRotBoneSpace" (lquat)
		# we invert the absolute rotation and translation.
		
		# These calculations may look easy, but it took me three days to get it right.
		
		if parent != None:
			parent.children.append(self)
			self.translationAbsolute = (parent.rotationAbsolute.inverted() * self.loc) + parent.translationAbsolute
			self.rotationAbsolute = self.quat * parent.rotationAbsolute
		else:
			self.translationAbsolute = self.loc
			self.rotationAbsolute = self.quat
	
		self.lquat = self.rotationAbsolute.inverted()
		self.lloc = -(self.rotationAbsolute * self.translationAbsolute)
		
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

		
	def to_cal3d_binary(self, file):
		name = self.name
		name += '\0'
		ar = array('L', [len(name)])
		ar.tofile(file)
		
		ar = array('b', list(name.encode("utf8")))
		ar.tofile(file)
		
		ar = array('f', [self.loc[0],
						 self.loc[1],
						 self.loc[2],
						 self.quat.x,
						 self.quat.y,
						 self.quat.z,
						 self.quat.w,
						 self.lloc[0],
						 self.lloc[1],
						 self.lloc[2],
						 self.lquat.x, 
						 self.lquat.y,
						 self.lquat.z,
						 self.lquat.w])
		ar.tofile(file)
		
		if self.parent:
			ar = array('L', [self.parent.index])
		else:
			ar = array('l', [-1])
		if self.children:
			ar.append(len(self.children))
			for ch in self.children:
				ar.append(ch.index)
		else:
			ar.append(0)
		ar.tofile(file)