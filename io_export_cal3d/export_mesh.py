import bpy
import mathutils

from . import mesh_classes
from . import armature_classes
from .mesh_classes import *
from .armature_classes import *

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


def create_cal3d_mesh(mesh_obj, mesh_data,
                      cal3d_skeleton,
                      base_rotation_orig,
                      base_translation_orig,
                      base_scale,
                      xml_version):

	base_translation = base_translation_orig.copy()
	base_rotation = base_rotation_orig.copy()

	mesh_matrix = mesh_obj.matrix_world.copy()
	mesh_rotation = mesh_matrix.to_3x3().copy()
	mesh_translation = mesh_matrix.to_translation().copy()

	total_rotation = mesh_rotation.copy()
	total_rotation.rotate(base_rotation)

	total_translation = base_translation + mesh_translation

	cal3d_mesh = Mesh(mesh_obj.name, xml_version)

	faces = mesh_data.faces

	# for each material of the mesh a separate submesh should be created
	# as there're no materials, one submesh will do for now
	cal3d_submesh = SubMesh(cal3d_mesh, len(cal3d_mesh.submeshes), -1)
	cal3d_mesh.submeshes.append(cal3d_submesh)

	for face in mesh_data.faces:
		cal3d_vertex1 = None
		cal3d_vertex2 = None
		cal3d_vertex3 = None
		cal3d_vertex4 = None

		for vertex_index in face.vertices:
			cal3d_vertex = None
			for cal3d_vertex_iter in cal3d_submesh.vertices:
				if cal3d_vertex_iter.index == vertex_index:
					cal3d_vertex = cal3d_vertex_iter
					break

			if not cal3d_vertex:
				vertex = mesh_data.vertices[vertex_index]

				normal = vertex.normal.copy()
				normal.rotate(total_rotation)

				coord = vertex.co.copy()
				coord = (coord + total_translation) * base_scale
				coord.rotate(total_rotation)

				cal3d_vertex = Vertex(cal3d_submesh, vertex_index,
				                      coord, normal)

				cal3d_vertex.influences = get_vertex_influences(vertex,
						                                        mesh_obj,
				                                                cal3d_skeleton)
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

	return cal3d_mesh

