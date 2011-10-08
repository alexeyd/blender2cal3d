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

	# convert head translation to bone if needed
	if bone_head.length != 0: 
		head_bone_loc = bone_head.copy()
		head_bone_loc.x *= scale.x
		head_bone_loc.y *= scale.y
		head_bone_loc.z *= scale.z
		head_bone_rot = Matrix().to_3x3()
		head_bone_rot.identity()
		head_bone = Bone(skeleton, parent, name+"_head",
		                 head_bone_loc, head_bone_rot)

		parent = head_bone


	# each blender bone is mapped to 2 cal3d bones:
	# rotator and translator
	rotator_rot = b.matrix.copy()
	rotator_loc = Vector([0.0, 0.0, 0.0])
	rotator_bone = Bone(skeleton, parent, name+"_rotator",
	                    rotator_loc, rotator_rot)
	parent = rotator_bone


	translator_loc = (bone_tail - bone_head)
	translator_loc.x *= scale.x
	translator_loc.y *= scale.y
	translator_loc.z *= scale.z
	translator_loc.rotate(b.matrix.inverted())
	translator_rot = Matrix().to_3x3()
	translator_rot.identity()
	bone = Bone(skeleton, parent, name, translator_loc, translator_rot)

	for child in b.children:
		treat_bone(child, scale, bone, skeleton)


def create_cal3d_skeleton(arm_obj, arm_data,
                          base_rotation_orig,
                          base_translation_orig,
                          base_scale_orig,
                          xml_version):
	skeleton = Skeleton(arm_obj.name, xml_version)

	base_translation = base_translation_orig.copy()
	base_rotation = base_rotation_orig.copy()
	base_scale = base_scale_orig.copy()

	base_matrix = base_scale                            * \
	              Matrix.Translation(base_translation)  * \
	              base_rotation.to_4x4()                * \
	              arm_obj.matrix_world.copy()

	(loc, rot, scale) = base_matrix.decompose()

	total_translation = loc.copy()
	total_rotation = rot.to_matrix().to_3x3()
	total_scale = scale.copy()


	service_root = Bone(skeleton, None, "_service_root",
	                    total_translation.copy(), total_rotation.copy())

	for bone in arm_data.bones.values():
		if not bone.parent and bone.name[0] != "_":
			treat_bone(bone, total_scale, service_root, skeleton)

	return skeleton

