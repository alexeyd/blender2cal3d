import os
from math import *

import bpy
from mathutils import *

from . import armature_classes
from .armature_classes import *


def treat_bone(b, scale, parent, skeleton):
	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0 or  b.name[0] == '_':
		return

	name = b.name

	bone_matrix = b.matrix_local.copy()
	if b.parent != None:
		# isolate the parent -> child transform
		bone_matrix = b.parent.matrix_local.inverted() * bone_matrix
	bone_trans = bone_matrix.to_translation() * scale
	b_inv_quat = bone_matrix.to_quaternion().inverted()
		
	bone = Bone(skeleton, parent, name, bone_trans, b_inv_quat)

	for child in b.children:
		treat_bone(child, scale, bone, skeleton)
	
	# This adds an extra bone to extremities; this is
	# purely a hack to make these bones show up in the Cal3D viewer 
	# for debugging.  These "leaf" bones otherwise have
	# no effect so they are not added by default.
	add_leaf_bones = False
	if len(b.children) == 0 and add_leaf_bones:
		tail = scale * (b.tail - b.head)
		bone = Bone(skeleton, bone, name + "_leaf",
					b.matrix.inverted() * tail,
					Quaternion())

def create_cal3d_skeleton(arm_obj, arm_data,
						  base_rotation,
						  base_translation,
						  base_scale,
						  xml_version):
	
	prevpose = arm_data.pose_position		  
	arm_data.pose_position = 'REST'
						  
	skeleton = Skeleton(arm_obj.name, xml_version)
	
	base_matrix =   Matrix.Scale(base_scale, 4) \
				  * base_rotation.to_4x4() \
				  * Matrix.Translation(base_translation) \
				  * arm_obj.matrix_world

	(total_translation, total_rotation, total_scale) = base_matrix.decompose()
	
	service_root = Bone(skeleton, None, "_root",
						total_translation.copy(), 
						total_rotation.inverted())

	scalematrix = Matrix()
	scalematrix[0][0] = total_scale.x
	scalematrix[1][1] = total_scale.y
	scalematrix[2][2] = total_scale.z
	
	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			treat_bone(bone, scalematrix, service_root, skeleton)
			
	arm_data.pose_position = prevpose

	return skeleton

