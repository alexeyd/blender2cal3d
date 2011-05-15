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

	bone_head = b.head.copy()
	bone_tail = b.tail.copy()

	if bone_head.length != 0: 
		interm_loc = bone_head.copy() * scale
		interm_rot = Matrix.Rotation(0.0, 3, "X")
		interm_rot.identity()

		interm_bone = Bone(skeleton, parent, name+"_interm",
		                   interm_loc, interm_rot)
		parent = interm_bone


	loc = (bone_tail - bone_head) * scale
	rot = b.matrix.copy()
	bone = Bone(skeleton, parent, name, loc, rot)

	for child in b.children:
		treat_bone(child, scale, bone, skeleton)


def create_cal3d_skeleton(arm_obj, arm_data,     \
                          base_rotation_orig,    \
                          base_translation_orig, \
                          base_scale,            \
                          xml_version):
	skeleton = Skeleton(arm_obj.name, xml_version)

	arm_matrix = arm_obj.matrix_world.copy()
	arm_translation = arm_matrix.to_translation()
	arm_rotation = arm_matrix.to_3x3()

	base_translation = base_translation_orig.copy()
	base_rotation = base_rotation_orig.copy()

	total_rotation = arm_rotation.copy()
	total_rotation.rotate(base_rotation)

	total_translation = (base_translation + arm_translation) * base_scale

	service_root = Bone(skeleton, None, "service_root",                 \
	                    total_translation.copy(), total_rotation.copy())

	root_bone = None

	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			if root_bone:
				raise RuntimeError("Only one root bone is supported")
			else:
				root_bone = bone

	treat_bone(root_bone, base_scale, service_root, skeleton)

	return skeleton

