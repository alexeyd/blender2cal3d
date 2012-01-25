import bpy
import mathutils

from . import armature_classes
from .armature_classes import *

from . import action_classes
from .action_classes import *

def get_action_group_fcurve(action_group, data_path, array_index):
    for fcu in action_group.channels:
        if fcu.data_path.find(data_path) != -1 and \
		   fcu.array_index == array_index:
            return fcu
    return None


def get_keyframes_list(fcu):
	keyframes_list = []
	if fcu:
		for keyframe in fcu.keyframe_points:
			keyframes_list.append(keyframe.co[0])
	return keyframes_list


def evaluate_loc(loc_x_fcu, loc_y_fcu, loc_z_fcu, keyframe):
	loc_x = 0.0
	loc_y = 0.0
	loc_z = 0.0

	if loc_x_fcu:
		loc_x = loc_x_fcu.evaluate(keyframe)

	if loc_y_fcu:
		loc_y = loc_y_fcu.evaluate(keyframe)

	if loc_z_fcu:
		loc_z = loc_z_fcu.evaluate(keyframe)

	return mathutils.Vector([loc_x, loc_y, loc_z])


def evaluate_quat(quat_x_fcu, quat_y_fcu, quat_z_fcu, quat_w_fcu, keyframe):
	quat_x = 0.0
	quat_y = 0.0
	quat_z = 0.0
	quat_w = 0.0

	if quat_x_fcu:
		quat_x = quat_x_fcu.evaluate(keyframe)

	if quat_y_fcu:
		quat_y = quat_y_fcu.evaluate(keyframe)

	if quat_z_fcu:
		quat_z = quat_z_fcu.evaluate(keyframe)

	if quat_w_fcu:
		quat_w = quat_w_fcu.evaluate(keyframe)


	return mathutils.Quaternion([quat_x, quat_y, quat_z, quat_w])





def track_sort_key(track):
	return track.bone_index


def keyframe_sort_key(keyframe):
	return keyframe.time


def merge_rotations(track, rot_track):
	for rot_keyframe in rot_track.keyframes:
		
		found_keyframe = False

		for keyframe in track.keyframes:
			if (abs(keyframe.time - rot_keyframe.time) < 1e-5):
				found_keyframe = True
				keyframe.quat = rot_keyframe.quat.copy()
				break

		if not found_keyframe:
			track.keyframes.append(rot_keyframe)

	track.keyframes.sort(key=keyframe_sort_key)


def merge_tracks(loc_tracks, rot_tracks):
	tracks = []
	tracks.extend(loc_tracks)

	for rot_track in rot_tracks:
		found_track = False

		for track in tracks:
			if track.bone_index == rot_track.bone_index:
				found_track = True
				merge_rotations(track, rot_track)
				break

		if not found_track:
			tracks.append(rot_track)
	
	tracks.sort(key=track_sort_key)

	return tracks



def create_cal3d_animation(cal3d_skeleton, action, fps, 
                           base_scale, xml_version):
	cal3d_animation = Animation(action.name, xml_version)
	rot_tracks = []
	loc_tracks = []

	for action_group in action.groups:
		cal3d_bone = None

		for bone in cal3d_skeleton.bones:
			if bone.name == action_group.name:
				cal3d_bone = bone
				break

		if not cal3d_bone:
			continue


		# service root ensures that animated bone
		# will always have parent
		cal3d_rot_bone = cal3d_bone
		cal3d_loc_bone = cal3d_bone.parent

		cal3d_rot_track = Track(cal3d_rot_bone.index)
		cal3d_loc_track = Track(cal3d_loc_bone.parent.index)

		loc_x_fcu = get_action_group_fcurve(action_group, "location", 0)
		loc_y_fcu = get_action_group_fcurve(action_group, "location", 1)
		loc_z_fcu = get_action_group_fcurve(action_group, "location", 2)

		quat_x_fcu = get_action_group_fcurve(action_group, 
				                             "rotation_quaternion", 0)
		quat_y_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 1)
		quat_z_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 2)
		quat_w_fcu = get_action_group_fcurve(action_group,
				                             "rotation_quaternion", 3)

		keyframes_list = []

		keyframes_list.extend(get_keyframes_list(loc_x_fcu))
		keyframes_list.extend(get_keyframes_list(loc_y_fcu))
		keyframes_list.extend(get_keyframes_list(loc_z_fcu))

		keyframes_list.extend(get_keyframes_list(quat_x_fcu))
		keyframes_list.extend(get_keyframes_list(quat_y_fcu))
		keyframes_list.extend(get_keyframes_list(quat_z_fcu))
		keyframes_list.extend(get_keyframes_list(quat_w_fcu))

		# remove duplicates
		keyframes_set = set(keyframes_list)
		keyframes_list = list(keyframes_set)
		keyframes_list.sort()
		
		if len(keyframes_list) == 0:
			continue

		first_keyframe = keyframes_list[0]
		last_keyframe = keyframes_list[len(keyframes_list) - 1]

		rot_keyframes = []
		loc_keyframes = []

		for keyframe in keyframes_list:
			dloc = evaluate_loc(loc_x_fcu, loc_y_fcu, loc_z_fcu, keyframe)
			dquat = evaluate_quat(quat_x_fcu, quat_y_fcu, 
			                      quat_z_fcu, quat_w_fcu, keyframe)

			dloc = dloc * base_scale
			dloc.rotate(cal3d_loc_bone.quat)
			loc = cal3d_bone.parent.loc + dloc

			quat = dquat.copy()
			quat.rotate(cal3d_rot_bone.quat)
			quat.normalize()

			cal3d_rot_keyframe = KeyFrame((keyframe - first_keyframe) / fps,
			                              cal3d_rot_bone.loc, quat)
			rot_keyframes.append(cal3d_rot_keyframe)

			cal3d_loc_keyframe = KeyFrame((keyframe - first_keyframe) / fps,
			                              loc, cal3d_loc_bone.quat)
			loc_keyframes.append(cal3d_loc_keyframe)

		cal3d_rot_track.keyframes = rot_keyframes
		cal3d_loc_track.keyframes = loc_keyframes

		if len(cal3d_rot_track.keyframes) > 0:
			rot_tracks.append(cal3d_rot_track)

		if len(cal3d_loc_track.keyframes) > 0:
			loc_tracks.append(cal3d_loc_track)

	if len(rot_tracks) > 0 or len(loc_tracks) > 0:
		cal3d_animation.duration = ((last_keyframe - first_keyframe) / fps)
		cal3d_animation.tracks = merge_tracks(loc_tracks, rot_tracks)
		return cal3d_animation

	return None

