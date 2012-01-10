import os
from math import *

import bpy
from mathutils import *

from . import armature_classes
from .armature_classes import *


def treat_bone(b, scale, parent, skeleton, world_matrix):
	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0:
		return

	if b.name[0] == '_':
		return

	name = b.name
	
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
	
	oneBone = True
	if oneBone:
		bone = Bone(skeleton, parent, name,
							 bone_trans,
							 b.matrix.to_quaternion().inverted(),
							 local_trans,
							 local_quat)
	else:
		# this works but doubling the number of bones is very undesirable
		bone = Bone(skeleton, parent, name,
							 (scale * b.head),
							 b.matrix.to_quaternion().inverted(),
							 local_trans,
							 local_quat)
		                     
		bone = Bone(skeleton, bone, name + "_tail",
							 b.matrix.inverted() * (scale * b.tail),
							 Quaternion((1, 0, 0, 0)),
							 Vector(),
							 Quaternion((1, 0, 0, 0)))

	for child in b.children:
		treat_bone(child, scale, bone, skeleton, world_matrix)
	
	if len(b.children) == 0 and oneBone:
		bone = Bone(skeleton, bone, name + "_leaf",
					b.matrix.inverted() * (scale * b.tail),
					Quaternion((1, 0, 0, 0)),
					Vector(),
					Quaternion((1, 0, 0, 0)))

def create_cal3d_skeleton(arm_obj, arm_data,
                          base_rotation,
                          base_translation,
                          base_scale,
                          xml_version):
	skeleton = Skeleton(arm_obj.name, xml_version)
	
	(arm_translation, arm_quat, arm_scale) = arm_obj.matrix_world.decompose()

	total_translation = (base_scale * arm_translation) + base_translation

	total_rotation = base_rotation * arm_quat.to_matrix()

	total_scaling = Matrix(((base_scale * arm_scale.x, 0, 0),
							(0, base_scale * arm_scale.y, 0),
							(0, 0, base_scale * arm_scale.z)))

	service_root = Bone(skeleton, None, "service_root",
	                    total_translation.copy(), 
	                    total_rotation.to_quaternion().inverted(),
	                    Vector(), 
	                    Quaternion((1, 0, 0, 0)))

	root_bone = None

	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			if root_bone:
				raise RuntimeError("Only one root bone is supported")
			else:
				root_bone = bone

	#arm_world_noscale = Matrix.Translation(-arm_translation) * arm_quat.inverted().to_matrix().to_4x4()
	arm_world_noscale = Matrix.Translation(arm_translation) * arm_quat.to_matrix().to_4x4()

	treat_bone(root_bone, total_scaling, service_root, skeleton, 
				arm_world_noscale)

	return skeleton

