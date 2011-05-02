import bpy
import mathutils
from . import mesh_classes

def create_cal3d_mesh(mesh_obj, mesh_data,   \
                      base_matrix_orig,      \
                      base_translation_orig, \
                      xml_version):
	bad_vgs = []

	base_translation = base_translation_orig.copy()

	base_matrix = base_matrix_orig.copy()
	base_matrix.invert()

	cal3d_mesh = Mesh(mesh_obj.name)

	matrix = mesh_obj.mat.copy()
	matrix.resize4x4()

	data.transform(matrix)

	faces = mesh_data.faces

	# for each material of the mesh a separate submesh should be created
	# as there're no materials, one submesh will do for now
	cal3d_submesh = SubMesh(cal3d_mesh, len(cal3d_mesh.submeshes), -1)
	cal3d_mesh.submeshes.append(cal3d_submesh)

	for face in mesh_data.faces:
		cal3d_vertex1 = None
		cal3d_vertex2 = None
		cal3d_vertex3 = None

		for vertex_index in face.vertices:
			cal3d_vertex = None
			for cal3d_vertex_iter in cal3d_submesh.vertices:
				if cal3d_vertex_iter.index == vertex_index:
					cal3d_vertex = cal3d_vertex_iter
					break

			if not cal3d_vertex:
				normal = mesh_data.vertices[vertex_index].normal.copy()
				normal = base_matrix * normal

				coord = mesh_data.vertices[vertex_index].co.copy()
				coord += base_translation
				coord = base_matrix * coord

				cal3d_vertex = Vertex(cal3d_submesh, vertex_index, \
				                      coord, normal)
				cal3d_submesh.vertices.append(cal3d_vertex)

				if not cal3d_vertex1:
					cal3d_vertex1 = cal3d_vertex
				elif not cal3d_vertex2:
					cal3d_vertex2 = cal3d_vertex
				elif not cal3d_vertex3:
					cal3d_vertex3 = cal3d_vertex

		cal3d_face = Face(cal3d_submesh, cal3d_vertex1, \
		                  cal3d_vertex2, cal3d_vertex3)
		cal3d_submesh.faces.append(cal3d_face)

	return cal3d_mesh

