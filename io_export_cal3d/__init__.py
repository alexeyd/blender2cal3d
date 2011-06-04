bl_info = \
{
  "name": "Cal3D format",
  "author": "Jean-Baptiste Lamy (Jiba), " \
            "Chris Montijin, "            \
            "Damien McGinnes, "           \
            "David Young, "               \
            "Alexey Dorokhov, "           \
			"Matthias Ferch",
  "blender": (2, 5, 7),
  "api": 35622,
  "location": "File > Export > Cal3D (.cfg)",
  "description": "Export mesh geometry, armature, "   \
                 "materials and animations to Cal3D",
  "warning": "",
  "wiki_url": "",
  "tracker_url": "",
  "category": "Import-Export"
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
	import imp

	if "mesh_classes" in locals():
		imp.reload(mesh_classes)

	if "export_mesh" in locals():
		imp.reload(export_mesh)


import bpy
from bpy.props import BoolProperty,        \
                      FloatProperty,       \
                      StringProperty,      \
                      FloatVectorProperty, \
                      IntProperty
import io_utils
from io_utils import ExportHelper, ImportHelper

import mathutils

import os.path


class ExportCal3D(bpy.types.Operator, ExportHelper):
	'''Save Cal3d Files'''

	bl_idname = "cal3d_model.cfg"
	bl_label = 'Export Cal3D'
	bl_options = {'PRESET'}

	filename_ext = ".cfg"
	filter_glob = StringProperty(default="*.cfg;*.xsf;*.xaf;*.xmf;*.xrf",
	                             options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    # context group
	shall_export_meshes = BoolProperty(name="Export Meshes",
	                                   description="",
	                                   default=True)

	shall_export_materials = BoolProperty(name="Export Materials",
	                                      description="",
	                                      default=False)

	shall_export_armature = BoolProperty(name="Export Armature/Animations",
	                                     description="",
	                                     default=True)

	
	filename_prefix = StringProperty(name="Filename Prefix", 
	                                 default="model_")
	imagepath_prefix = StringProperty(name="Image Path Prefix",
	                                  default="model_")

	base_rotation = FloatVectorProperty(name="Base Rotation", 
	                                    default = (0.0, 0.0, 0.0),
	                                    subtype="EULER")

	base_scale = FloatProperty(name="Base Scale",
	                           default=1.0)

	fps = FloatProperty(name="FPS", default=25.0)

	path_mode = io_utils.path_reference_mode

	def execute(self, context):
		from . import export_mesh
		from . import export_armature
		from . import export_action
		from .export_armature import create_cal3d_skeleton
		from .export_mesh import create_cal3d_mesh
		from .export_action import create_cal3d_animation

		cal3d_dirname = os.path.dirname(self.filepath)

		cal3d_skeleton = None
		cal3d_meshes = []
		cal3d_animations = []

		# make some adjustments so that exported model won't be mirrored
		base_translation = mathutils.Vector([0.0, 0.0, 0.0])
		base_rotation = mathutils.Euler([self.base_rotation[0],
		                                 self.base_rotation[1]+3.14159,
		                                 self.base_rotation[2]+3.14159]).to_matrix()
		base_scale = -self.base_scale
		fps = self.fps

		# Export armatures
		try:
			if self.shall_export_armature:
				for obj in context.selected_objects:
					if obj.type == "ARMATURE":
						if cal3d_skeleton:
							raise RuntimeError("Only one armature is supported")

						base_translation = obj.matrix_world.to_translation().copy()
						base_translation = -base_translation
						cal3d_skeleton = create_cal3d_skeleton(obj, obj.data,
						                                       base_rotation,
						                                       base_translation,
						                                       base_scale, 900)
		except RuntimeError as e:
			print("###### ERROR DURING ARMATURE EXPORT ######")
			print(e)
			return {"FINISHED"}

		# Export meshes
		try:
			if self.shall_export_meshes:
				for obj in context.selected_objects:
					if obj.type == "MESH":
						cal3d_meshes.append(create_cal3d_mesh(obj, obj.data,
						                                      cal3d_skeleton,
						                                      base_rotation,
						                                      base_translation,
						                                      base_scale, 900))
		except RuntimeError as e:
			print("###### ERROR DURING MESH EXPORT ######")
			print(e)
			return {"FINISHED"}


		# Export animations
		try:
			if self.shall_export_armature:
				for action in bpy.data.actions:
					cal3d_animation = create_cal3d_animation(cal3d_skeleton,
					                                         action, fps,
					                                         base_scale, 900)
					if cal3d_animation:
						cal3d_animations.append(cal3d_animation)
						
		except RuntimeError as e:
			print("###### ERROR DURING ACTION EXPORT ######")
			print(e)
			return {"FINISHED"}



		if cal3d_skeleton:
			skeleton_filename = self.filename_prefix + cal3d_skeleton.name + ".xsf"
			skeleton_filepath = os.path.join(cal3d_dirname, skeleton_filename)

			cal3d_skeleton_file = open(skeleton_filepath, "wt")
			cal3d_skeleton_file.write(cal3d_skeleton.to_cal3d_xml())
			cal3d_skeleton_file.close()

		for cal3d_mesh in cal3d_meshes:
			mesh_filename = self.filename_prefix + cal3d_mesh.name + ".xmf"
			mesh_filepath = os.path.join(cal3d_dirname, mesh_filename)

			cal3d_mesh_file = open(mesh_filepath, "wt")
			cal3d_mesh_file.write(cal3d_mesh.to_cal3d_xml())
			cal3d_mesh_file.close()

		for cal3d_animation in cal3d_animations:
			animation_filename = self.filename_prefix + cal3d_animation.name + ".xaf"
			animation_filepath = os.path.join(cal3d_dirname, animation_filename)

			cal3d_animation_file = open(animation_filepath, "wt")
			cal3d_animation_file.write(cal3d_animation.to_cal3d_xml())
			cal3d_animation_file.close()


		cal3d_cfg_file = open(self.filepath, "wt")

		if cal3d_skeleton:
			skeleton_filename = self.filename_prefix + cal3d_skeleton.name + ".xsf"
			cal3d_cfg_file.write("skeleton={0}\n".format(skeleton_filename))

		for cal3d_animation in cal3d_animations:
			animation_filename = self.filename_prefix + cal3d_animation.name + ".xaf"
			cal3d_cfg_file.write("animation={0}\n".format(animation_filename))

		for cal3d_mesh in cal3d_meshes:
			mesh_filename = self.filename_prefix + cal3d_mesh.name + ".xmf"
			cal3d_cfg_file.write("mesh={0}\n".format(mesh_filename))

		cal3d_cfg_file.close()

		return {"FINISHED"}


def menu_func_export(self, context):
	self.layout.operator(ExportCal3D.bl_idname, text="Cal3D (.cfg)")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()

