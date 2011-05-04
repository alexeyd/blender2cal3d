import os
from math import *

import bpy
from mathutils import *

from . import armature_classes


def treat_bone(b, base_matrix, arm_matrix, parent, skeleton):
	# skip bones that start with _
	# also skips children of that bone so be careful
	if len(b.name) == 0:
		return

	if b.name[0] == '_':
		return

	name = b.name

	bone_head = b.head.copy() # XXX b.head['BONESPACE'].copy()
	bone_tail = b.tail.copy() # XXX b.tail['BONESPACE'].copy()

#alexeyd: will port later
#	if not ROOT_TO_ZERO and not parent:
#		bone_tail = bone_tail - bone_head
#		bone_head = bone_head + \
#					arm_matrix.to_quaternion()*get_armature_translation(scene)
#		bone_tail = bone_tail + bone_head

	if bone_head.length != 0: 
#		if not ROOT_TO_ZERO and not parent:
#			if base_matrix and arm_matrix:
#				dummy_arm_matrix = arm_matrix.copy()
#				dummy_arm_matrix.invert()
#				dummy_base_matrix = base_matrix.copy()
#				dummy_base_matrix.invert()
#				result_matrix = dummy_base_matrix * dummy_arm_matrix
#				tmp_quat = result_matrix.to_quaternion()
#			else:
#				tmp_quat = Quaternion()
#
#			tmp_loc = Vector([0.0,0.0,0.0])
#			parent = Bone(skeleton, None, "service_root",
#			              tmp_loc.copy(), tmp_quat.copy())
#			parent.child_loc = Vector([0.0,0.0,0.0])

		# in this case create a service 
		# bone between child and parent
		if parent:
			interm_loc = parent.child_loc.copy()

#			interm_loc *= SCALE
			interm_quat = Quaternion()
			interm_bone = armature_classes.Bone(skeleton, parent, name+"_interm",
			                                    interm_loc, interm_quat)
			interm_bone.child_loc = bone_head
			parent = interm_bone
		else:
			bone_tail -= bone_head
			bone_head -= bone_head


	local_rot_mat = b.matrix # XXX b.matrix['BONESPACE'].to_quaternion()

	# convert to cal3d rotation
	local_rot_mat.invert()

	if base_matrix and arm_matrix and not parent:
		dummy_arm_matrix = arm_matrix.copy()
		dummy_arm_matrix.invert()
		dummy_base_matrix = base_matrix.copy()
		dummy_base_matrix.invert()
		dummy_base_matrix = dummy_base_matrix.to_4x4()
		cal3d_base_matrix = dummy_base_matrix * dummy_arm_matrix
		local_rot_mat = cal3d_base_matrix.to_3x3() * local_rot_mat

	if parent:
		loc = parent.child_loc.copy()
	else:
		loc = Vector([0.0,0.0,0.0])


#	loc *= SCALE
	quat = local_rot_mat.to_quaternion()
	bone = armature_classes.Bone(skeleton, parent, name, loc, quat)

	# if I got it right, root bone
	# shouldn't have translation =>
	# moving all translations one 
	# bone forward
	bone.child_loc = bone_tail - bone_head
	bone_matrix = b.matrix.to_quaternion() # XXX b.matrix['BONESPACE'].to_quaternion()
	bone.child_loc = bone.child_loc * bone_matrix # XXX bone_matrix * bone.child_loc

	has_children = False
	if len(b.children):
		for child in b.children:
			if len(child.name):
				if child.name[0] != '_':
					has_children = True
					break
	
	if has_children:
		for child in b.children:
			treat_bone(child, base_matrix.copy(), arm_matrix.copy(), 
			           bone, skeleton)
	else:
		# service bone for skeletons to look the 
		# same both in Blender and cal3d
		ender_loc = bone.child_loc.copy()
#		ender_loc *= SCALE
		ender_quat = Quaternion()
		armature_classes.Bone(skeleton, bone, name+"_ender", ender_loc, ender_quat)


def create_cal3d_skeleton(arm_obj, arm_data,     \
                          base_matrix_orig,      \
                          base_translation_orig, \
                          xml_version):
	skeleton = armature_classes.Skeleton(arm_obj.name, xml_version)

	arm_matrix = arm_obj.matrix_world.copy() # XXX obj.getMatrix().copy()

	base_translation = base_translation_orig.copy()
	base_matrix = base_matrix_orig.copy()

	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			treat_bone(bone, base_matrix.copy(), arm_matrix.copy(),
			           None, skeleton)
			break

	return skeleton

