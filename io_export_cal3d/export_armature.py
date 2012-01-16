import os
from math import *

import bpy
from mathutils import *

from . import armature_classes
from .armature_classes import *


def treat_bone(b, scale, parent, skeleton):
	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0:
		return

	if b.name[0] == '_':
		return

	name = b.name
	
	if False:
		# Scale the translation part of the armature -> bone matrix
		scaled_matrix_local = (Matrix.Translation(scale * b.head_local)
								* b.matrix_local.to_quaternion().to_matrix().to_4x4())
								
		# Calculate the transform from model space to joint space.
		joint_coordinate_frame = world_matrix * scaled_matrix_local
		
		local_quat = joint_coordinate_frame.to_quaternion()
		local_trans = local_quat.inverted() * (-joint_coordinate_frame.to_translation())
		
		if b.parent:
			if b.parent.parent:
				bone_trans = b.parent.matrix.inverted() * (scale * (b.parent.tail + b.head))
			else:
				bone_trans = b.parent.matrix_local.inverted() * (scale * (b.parent.tail + b.head))
		else:
			bone_trans = (scale * b.head)
			
		b_inv_quat = b.matrix.to_quaternion().inverted()
	else:
		bone_matrix = b.matrix_local.copy()
		if b.parent != None:
			# isolate the parent -> child transform
			bone_matrix = b.parent.matrix_local.inverted() * bone_matrix
		bone_trans = bone_matrix.to_translation() * scale
		b_inv_quat = bone_matrix.to_quaternion().inverted()
		
	oneBone = True
	if oneBone:
		bone = Bone(skeleton, parent, name, bone_trans, b_inv_quat)
	else:
		# this works but doubling the number of bones is very undesirable
		bone = Bone(skeleton, parent, name,
							 (scale * b.head),
							 b_inv_quat,
							 local_trans,
							 local_quat)
		                     
		bone = Bone(skeleton, bone, name + "_tail",
							 b.matrix.inverted() * (scale * b.tail),
							 Quaternion(),
							 Vector(),
							 Quaternion())

	for child in b.children:
		treat_bone(child, scale, bone, skeleton)
	
	if len(b.children) == 0 and oneBone:
		tail = scale * (b.tail - b.head)
		#print("b.tail {} leaf trans {} tail {}".format(b.matrix.inverted() * b.tail, b.matrix.inverted() * (scale * b.tail), tail))
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

