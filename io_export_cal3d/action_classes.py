import os
from math import *

import bpy
from mathutils import *

class KeyFrame:
	def __init__(self, time, loc, quat):
		self.time = time
		self.loc = loc.copy()
		self.quat = quat.copy()
 
 
	def to_cal3d_xml(self):
		s = "    <KEYFRAME TIME=\"{0}\">\n".format(self.time)
		s += "      <TRANSLATION>{0} {1} {2}</TRANSLATION>\n".format(self.loc[0], self.loc[1], self.loc[2])
		s += "      <ROTATION>{0} {1} {2} {3}</ROTATION>\n".format(self.quat.x, self.quat.y, self.quat.z, self.quat.w)
		s += "    </KEYFRAME>\n"
		return s



class Track:
	def __init__(self, bone_index):
		self.bone_index = bone_index
		self.keyframes = []


	def to_cal3d_xml(self):
		s = "  <TRACK BONEID=\"{0}\" NUMKEYFRAMES=\"{1}\">\n".format(self.bone_index, len(self.keyframes))
		s += "".join(map(KeyFrame.to_cal3d_xml, self.keyframes))
		s += "  </TRACK>\n"
		return s



class Animation:
	def __init__(self, name, xml_version):
		self.name = name
		self.xml_version = xml_version
		self.duration = 0.0
		self.tracks = [] 


	def to_cal3d_xml(self):
		s = "<HEADER MAGIC=\"XAF\" VERSION=\"{0}\"/>\n".format(self.xml_version)
		s += "<ANIMATION DURATION=\"{0}\" NUMTRACKS=\"{1}\">\n".format(self.duration, len(self.tracks))
		s += "".join(map(Track.to_cal3d_xml, self.tracks))
		s += "</ANIMATION>\n"
		return s

