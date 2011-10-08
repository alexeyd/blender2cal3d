import bpy
from mathutils import *

from . import mesh_classes
from . import armature_classes
from .mesh_classes import *
from .armature_classes import *


def create_cal3d_materials(xml_version):
	cal3d_materials = []
	for material in bpy.data.materials:
		material_index = len(cal3d_materials)
		material_name = material.name
		maps_filenames = []
		for texture_slot in material.texture_slots:
			if texture_slot and texture_slot.texture:
				if texture_slot.texture.type == "IMAGE" and texture_slot.texture.image:
					if texture_slot.texture.image.filepath:
						maps_filenames.append(texture_slot.texture.image.filepath)
		if len(maps_filenames) > 0:
			cal3d_material = Material(material_name, material_index, xml_version)
			cal3d_material.maps_filenames = maps_filenames
			cal3d_materials.append(cal3d_material)
	return cal3d_materials


def get_vertex_influences(vertex, mesh_obj, cal3d_skeleton):
	if not cal3d_skeleton:
		return []

	influences = []

	for group in vertex.groups:
		group_index = group.group
		group_name = mesh_obj.vertex_groups[group_index].name
		weight = group.weight

		for bone in cal3d_skeleton.bones:
			if bone.name == group_name:
				influence = Influence(bone.index, weight)
				influences.append(influence)
				break

	return influences


def create_cal3d_mesh(scene, mesh_obj,
                      cal3d_skeleton,
                      cal3d_materials,
                      base_rotation_orig,
                      base_translation_orig,
                      base_scale_orig,
                      xml_version):

	base_translation = base_translation_orig.copy()
	base_rotation = base_rotation_orig.copy()
	base_scale = base_scale_orig.copy()

	base_matrix = base_scale                            *   \
	              Matrix.Translation(base_translation)  *   \
	              base_rotation.to_4x4()                *   \
	              mesh_obj.matrix_world.copy()

	mesh_data = mesh_obj.to_mesh(scene, False, "PREVIEW")
	mesh_data.transform(base_matrix)

	cal3d_mesh = Mesh(mesh_obj.name, xml_version)

	faces = mesh_data.faces

	# currently 1 material per mesh

	if len(mesh_data.materials) > 0:
		blender_material = mesh_data.materials[0]
	
	cal3d_material_index = -1
	for cal3d_material in cal3d_materials:
		if cal3d_material.name == blender_material.name:
			cal3d_material_index = cal3d_material.index

	cal3d_submesh = SubMesh(cal3d_mesh, len(cal3d_mesh.submeshes),
	                        cal3d_material_index)
	cal3d_mesh.submeshes.append(cal3d_submesh)

	duplicate_index = len(mesh_data.vertices)

	for face in mesh_data.faces:
		cal3d_vertex1 = None
		cal3d_vertex2 = None
		cal3d_vertex3 = None
		cal3d_vertex4 = None

		for vertex_index in face.vertices:
			duplicate = False
			cal3d_vertex = None
			uvs = []

			for uv_texture in mesh_data.uv_textures:
				if not cal3d_vertex1:
					uvs.append(uv_texture.data[face.index].uv1.copy())
				elif not cal3d_vertex2:
					uvs.append(uv_texture.data[face.index].uv2.copy())
				elif not cal3d_vertex3:
					uvs.append(uv_texture.data[face.index].uv3.copy())
				elif not cal3d_vertex4:
					uvs.append(uv_texture.data[face.index].uv4.copy())

			for uv in uvs:
				uv[1] = 1.0 - uv[1]

			
			for cal3d_vertex_iter in cal3d_submesh.vertices:
				if cal3d_vertex_iter.index == vertex_index:
					duplicate = True
					if len(cal3d_vertex_iter.maps) != len(uvs):
						break
					
					uv_matches = True
					for i in range(len(uvs)):
						if cal3d_vertex_iter.maps[i].u != uvs[i][0]:
							uv_matches = False
							break

						if cal3d_vertex_iter.maps[i].v != uvs[i][1]:
							uv_matches = False
							break
					
					if uv_matches:
						cal3d_vertex = cal3d_vertex_iter

					break


			if not cal3d_vertex:
				vertex = mesh_data.vertices[vertex_index]

				normal = vertex.normal.copy()
				coord = vertex.co.copy()

				if duplicate:
					cal3d_vertex = Vertex(cal3d_submesh, duplicate_index,
					                      coord, normal)
					duplicate_index += 1

				else:
					cal3d_vertex = Vertex(cal3d_submesh, vertex_index,
					                      coord, normal)


				cal3d_vertex.influences = get_vertex_influences(vertex,
						                                        mesh_obj,
				                                                cal3d_skeleton)
				for uv in uvs:
					cal3d_vertex.maps.append(Map(uv[0], uv[1]))

				cal3d_submesh.vertices.append(cal3d_vertex)

			if not cal3d_vertex1:
				cal3d_vertex1 = cal3d_vertex
			elif not cal3d_vertex2:
				cal3d_vertex2 = cal3d_vertex
			elif not cal3d_vertex3:
				cal3d_vertex3 = cal3d_vertex
			elif not cal3d_vertex4:
				cal3d_vertex4 = cal3d_vertex

		cal3d_face = Face(cal3d_submesh, cal3d_vertex1,
		                  cal3d_vertex2, cal3d_vertex3,
		                  cal3d_vertex4)
		cal3d_submesh.faces.append(cal3d_face)

	bpy.data.meshes.remove(mesh_data)

	return cal3d_mesh

