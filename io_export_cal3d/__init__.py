bl_info = \
{
  "name": "Cal3D format",
  "author": "Jean-Baptiste Lamy (Jiba), " \
            "Chris Montijin, "            \
            "Damien McGinnes, "           \
            "David Young, "               \
            "Alexey Dorokhov, "           \
            "Matthias Ferch",
  "blender": (2, 5, 8),
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

	if "armature_classes" in locals():
		imp.reload(armature_classes)

	if "export_armature" in locals():
		imp.reload(export_armature)

	if "action_classes" in locals():
		imp.reload(action_classes)

	if "export_action" in locals():
		imp.reload(export_action)

import bpy
from bpy.props import BoolVectorProperty,  \
                      FloatProperty,       \
                      BoolProperty,       \
                      StringProperty,      \
                      FloatVectorProperty, \
                      IntProperty


import bpy_extras
from bpy_extras.io_utils import ExportHelper, ImportHelper

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
	filename_prefix = StringProperty(name="Filename Prefix", 
	                                 default="model_")
	imagepath_prefix = StringProperty(name="Image Path Prefix",
	                                  default="model_")

	base_translation = FloatVectorProperty(name="Base Translation", 
	                                       default = (0.0, 0.0, 0.0),
	                                       subtype="TRANSLATION")

	base_rotation = FloatVectorProperty(name="Base Rotation", 
	                                    default = (0.0, 0.0, 0.0),
	                                    subtype="EULER")

	base_scale = FloatProperty(name="Base Scale", default=1.0)

	# that would be a cool feature once I finish debugging (=
	mirror_boolvec = BoolVectorProperty(name = "Mirror", 
	                                    default= (False, False, False),
	                                    subtype="XYZ")

	fps = FloatProperty(name="FPS", default=25.0)
	cs_format = BoolProperty(name = ".CFG in CS XML format (experimental)", default= False)

	path_mode = bpy_extras.io_utils.path_reference_mode



	def export_cfg(self, filepath, cal3d_skeleton, cal3d_animations, cal3d_materials, cal3d_meshes):
		cal3d_cfg_file = open(filepath, "wt")

		if cal3d_skeleton:
			skeleton_filename = self.filename_prefix + cal3d_skeleton.name + ".xsf"
			cal3d_cfg_file.write("skeleton={0}\n".format(skeleton_filename))

		for cal3d_animation in cal3d_animations:
			animation_filename = self.filename_prefix + cal3d_animation.name + ".xaf"
			cal3d_cfg_file.write("animation={0}\n".format(animation_filename))

		for cal3d_material in cal3d_materials:
			material_filename = self.filename_prefix + cal3d_material.name + ".xrf"
			cal3d_cfg_file.write("material={0}\n".format(material_filename))

		for cal3d_mesh in cal3d_meshes:
			mesh_filename = self.filename_prefix + cal3d_mesh.name + ".xmf"
			cal3d_cfg_file.write("mesh={0}\n".format(mesh_filename))

		cal3d_cfg_file.close()


	# yes, that function is a fast hack. shame on me (=
	def export_xml_cfg(self, filepath, cal3d_skeleton, cal3d_animations, cal3d_materials, cal3d_meshes):
		cal3d_cfg_file = open(filepath, "wt")
		cal3d_cfg_file.write("<!--\n#\n# CS cal3d model xml file\n#\n# model: {0}\n#\n-->\n".format(filepath))
		cal3d_cfg_file.write("<library>\n")
		cal3d_cfg_file.write("    <shaders><file>/shader/lighting/lighting_character.xml</file></shaders>\n")

		cal3d_cfg_file.write("    <textures>\n")
		for cal3d_material in cal3d_materials:
			cal3d_cfg_file.write("       <texture name=\"{0}\">\n".format(cal3d_material.maps_filenames[0]))
			cal3d_cfg_file.write("           <file>{0}</file>\n".format(cal3d_material.maps_filenames[0]))
			cal3d_cfg_file.write("       </texture>\n")
		cal3d_cfg_file.write("    </textures>\n")

		cal3d_cfg_file.write("    <materials>\n")
		for cal3d_material in cal3d_materials:
			cal3d_cfg_file.write("        <material name=\"{0}\">\n".format(cal3d_material.name))
			cal3d_cfg_file.write("            <shader type=\"depthwrite\">*null</shader>\n")
			cal3d_cfg_file.write("            <shader type=\"base\">lighting_character</shader>\n")
			cal3d_cfg_file.write("            <shader type=\"diffuse\">lighting_character</shader>\n")
			cal3d_cfg_file.write("            <shadervar name=\"tex diffuse\" type=\"texture\">{0}</shadervar>\n".format(cal3d_material.maps_filenames[0]))
			cal3d_cfg_file.write("            <shadervar name=\"color modulation\" type=\"vector4\">1,1,1,1</shadervar>\n")
			cal3d_cfg_file.write("            <shadervar name=\"specular\" type=\"vector3\">0,0,0</shadervar>\n")
			cal3d_cfg_file.write("        </material>\n".format(cal3d_material.name))
		cal3d_cfg_file.write("    </materials>\n")

		cal3d_cfg_file.write("    <meshfact name=\"{0}\">\n".format(filepath))
		cal3d_cfg_file.write("        <plugin>crystalspace.mesh.loader.factory.sprite.cal3d</plugin>\n")
		cal3d_cfg_file.write("        <params>\n")

		skeleton_filename = self.filename_prefix + cal3d_skeleton.name + ".csf"
		cal3d_cfg_file.write("            <skeleton file=\"{0}\" />\n".format(skeleton_filename))

		
		for cal3d_animation in cal3d_animations:
			animation_filename = self.filename_prefix + cal3d_animation.name + ".caf"
			cal3d_cfg_file.write("            <animation file=\"{0}\" name=\"{1}\" type=\"action\"/>\n".format(animation_filename, animation_filename))


		for cal3d_mesh in cal3d_meshes:
			mesh_filename = self.filename_prefix + cal3d_mesh.name + ".cmf"
			mesh_material_name = ""
			submesh = cal3d_mesh.submeshes[0]
			for cal3d_material in cal3d_materials:
				if cal3d_material.index == submesh.material_id:
					mesh_material_name = cal3d_material.name
					break
			cal3d_cfg_file.write("            <mesh file=\"{0}\" material=\"{1}\" name=\"{2}\" />\n".format(mesh_filename, mesh_material_name, cal3d_mesh.name))
		cal3d_cfg_file.write("        </params>\n")
		cal3d_cfg_file.write("    </meshfact>\n")
		cal3d_cfg_file.write("</library>\n")

		cal3d_cfg_file.close()


	def execute(self, context):
		from . import export_mesh
		from . import export_armature
		from . import export_action
		from .export_armature import create_cal3d_skeleton
		from .export_mesh import create_cal3d_materials
		from .export_mesh import create_cal3d_mesh
		from .export_action import create_cal3d_animation

		cal3d_dirname = os.path.dirname(self.filepath)

		cal3d_skeleton = None
		cal3d_materials = []
		cal3d_meshes = []
		cal3d_animations = []

		# model will be transformed during export if needed
		base_translation = mathutils.Vector([self.base_translation[0],
		                                     self.base_translation[1],
		                                     self.base_translation[2]])

		base_rotation = mathutils.Euler([self.base_rotation[0],
		                                 self.base_rotation[1],
		                                 self.base_rotation[2]]).to_matrix()

		base_scale = mathutils.Matrix.Scale(self.base_scale, 4)

		if(self.mirror_boolvec[0]):
			base_scale[0][0] = -base_scale[0][0]

		if(self.mirror_boolvec[1]):
			base_scale[1][1] = -base_scale[1][1]

		if(self.mirror_boolvec[2]):
			base_scale[2][2] = -base_scale[2][2]

		fps = self.fps

		armature_scale = mathutils.Matrix().to_4x4()
		armature_scale.identity()


		# Export armatures
		try:
			for obj in context.selected_objects:
				if obj.type == "ARMATURE":
					if cal3d_skeleton:
						raise RuntimeError("Only one armature is supported")

					cal3d_skeleton = create_cal3d_skeleton(obj, obj.data,
					                                       base_rotation,
					                                       base_translation,
					                                       base_scale, 900)
					(loc, rot, scale) = obj.matrix_world.decompose()
					armature_scale[0][0] = scale.x
					armature_scale[1][1] = scale.y
					armature_scale[2][2] = scale.z

		except RuntimeError as e:
			print("###### ERROR DURING ARMATURE EXPORT ######")
			print(e)
			return {"FINISHED"}

		# Export meshes
		try:
			cal3d_materials = create_cal3d_materials(900)

			for obj in context.selected_objects:
				if obj.type == "MESH":
					cal3d_meshes.append(create_cal3d_mesh(context. scene, obj, 
					                                      cal3d_skeleton,
														  cal3d_materials,
					                                      base_rotation,
					                                      base_translation,
					                                      base_scale, 900))
		except RuntimeError as e:
			print("###### ERROR DURING MESH EXPORT ######")
			print(e)
			return {"FINISHED"}


		# Export animations
		try:
			if cal3d_skeleton:
				for action in bpy.data.actions:
					cal3d_animation = create_cal3d_animation(cal3d_skeleton,
					                                         action, fps,
					                                         900)
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

		for cal3d_material in cal3d_materials:
			material_filename = self.filename_prefix + cal3d_material.name + ".xrf"
			material_filepath = os.path.join(cal3d_dirname, material_filename)

			cal3d_material_file = open(material_filepath, "wt")
			cal3d_material_file.write(cal3d_material.to_cal3d_xml())
			cal3d_material_file.close()


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

		if self.cs_format:
			self.export_xml_cfg(self.filepath, cal3d_skeleton, cal3d_animations, cal3d_materials, cal3d_meshes)
		else:
			self.export_cfg(self.filepath, cal3d_skeleton, cal3d_animations, cal3d_materials, cal3d_meshes)

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

