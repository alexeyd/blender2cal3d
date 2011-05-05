import bpy
import mathutils
from . import mesh_classes


def create_cal3d_mesh(mesh_obj, mesh_data,   \
                      base_matrix_orig,      \
                      base_translation_orig, \
                      xml_version):

	base_translation = base_translation_orig.copy()

	base_matrix = base_matrix_orig.copy()
	base_matrix.invert()

	cal3d_mesh = mesh_classes.Mesh(mesh_obj.name, xml_version)

	matrix = mesh_obj.matrix_world.copy()
	matrix = matrix.to_4x4()

	faces = mesh_data.faces

	# for each material of the mesh a separate submesh should be created
	# as there're no materials, one submesh will do for now
	cal3d_submesh = mesh_classes.SubMesh(cal3d_mesh, len(cal3d_mesh.submeshes), -1)
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
				normal = mesh_data.vertices[vertex_index].normal.copy()
				normal = normal * matrix.to_3x3()
				normal = normal * base_matrix

				coord = mesh_data.vertices[vertex_index].co.copy()
				coord = coord * matrix
				coord += base_translation
				coord = coord * base_matrix

				cal3d_vertex = mesh_classes.Vertex(cal3d_submesh, vertex_index, \
				                                   coord, normal)
				cal3d_submesh.vertices.append(cal3d_vertex)

			if not cal3d_vertex1:
				cal3d_vertex1 = cal3d_vertex
			elif not cal3d_vertex2:
				cal3d_vertex2 = cal3d_vertex
			elif not cal3d_vertex3:
				cal3d_vertex3 = cal3d_vertex
			elif not cal3d_vertex4:
				cal3d_vertex4 = cal3d_vertex

		cal3d_face = mesh_classes.Face(cal3d_submesh, cal3d_vertex1, \
		                               cal3d_vertex2, cal3d_vertex3, \
									   cal3d_vertex4)
		cal3d_submesh.faces.append(cal3d_face)

	return cal3d_mesh

