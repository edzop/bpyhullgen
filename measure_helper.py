# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh
import csv
import imp

curve_helper = imp.load_source('curve_helper','curve_helper.py')
material_helper = imp.load_source('material_helper','material_helper.py')



# =======================================================================================
# This bmesh_copy_from_object function was borrowed from the object_print3d_utils addon.
# I found it in the default blender 2.8 installation under the file:
# addons/object_print3d_utils/mesh_helpers.py
# Credit due to whoever the author is. 
# =======================================================================================
def bmesh_copy_from_object(obj, transform=True, triangulate=True, apply_modifiers=False):
	"""
	Returns a transformed, triangulated copy of the mesh
	"""

	assert obj.type == 'MESH'

	if apply_modifiers and obj.modifiers:
		import bpy
		depsgraph = bpy.context.evaluated_depsgraph_get()
		obj_eval = obj.evaluated_get(depsgraph)
		me = obj_eval.to_mesh()
		bm = bmesh.new()
		bm.from_mesh(me)
		obj_eval.to_mesh_clear()
		del bpy
	else:
		me = obj.data
		if obj.mode == 'EDIT':
			bm_orig = bmesh.from_edit_mesh(me)
			bm = bm_orig.copy()
		else:
			bm = bmesh.new()
			bm.from_mesh(me)

	# TODO. remove all customdata layers.
	# would save ram

	if transform:
		bm.transform(obj.matrix_world)

	if triangulate:
		bmesh.ops.triangulate(bm, faces=bm.faces)

	return bm


def measure_object_volume(obj):

	bm = bmesh_copy_from_object(obj, apply_modifiers=True)
	volume = bm.calc_volume()
	bm.free()

	return volume

def measure_selected_faces_area(obj,SelectAll=False):

	selected_face_count=0
	total_area=0

	print(obj.name)

	if SelectAll==True:
		curve_helper.select_object(obj,True)
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

	for f in obj.data.polygons:
		if f.select:
			selected_face_count+=1
			total_area+=f.area
			#print(f.area)

	face_data=[selected_face_count,total_area]

	return face_data

def import_plates(filename):

	bpy.ops.import_curve.svg(filepath=filename)

#	bpy.ops.object.select_all(action='SELECT')

	found_curve=False

	for obj in bpy.data.objects:
		if obj.type=="CURVE":
			if obj.name.startswith("Curve"):

				if found_curve==False:
					bpy.context.view_layer.objects.active = obj
					found_curve=True
				
				obj.select_set(state=True)

	if found_curve==True:
		obj = bpy.context.view_layer.objects.active
		print("found curve: %s"%obj.name)
		bpy.ops.object.join()
		bpy.ops.object.convert(target='MESH')

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.remove_doubles()
		bpy.ops.mesh.select_mode(type="EDGE")
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

		
		print("SS:"+obj.name)
		obj.data.edges[0].select=True
		bpy.ops.object.mode_set(mode='EDIT')
		#bpy.ops.mesh.select_similar(type='FACE', compare='LESS', threshold=1)
		bpy.ops.mesh.select_similar(type='FACE', threshold=1)
		
		bpy.ops.mesh.select_all(action='INVERT')
		bpy.ops.mesh.delete(type='EDGE')
		
		bpy.ops.mesh.select_mode(type="VERT")
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.mesh.select_loose()
		bpy.ops.mesh.delete(type='VERT')

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.separate(type='LOOSE')
		bpy.ops.mesh.select_mode(type="EDGE")

		bpy.ops.object.mode_set(mode='OBJECT')

def export_dxf(filename):

	# For some reason it doens't work if there is no material in slot 0
	# even when you specify entitycolor from obj.layer 

	default_material=material_helper.make_diffuse_material("export_default",(1,1,1,1))

	for obj in bpy.data.objects:
		if obj.type=="MESH":
			print(obj.name + " slots: %s"%len(obj.material_slots))
			if obj.data.materials[0]==None:
				material_helper.assign_material(obj,default_material)
	
	bpy.ops.export.dxf(filepath="test.dxf", 
		projectionThrough='NO', 
		onlySelected=False, 
		apply_modifiers=True, 
		mesh_as='3DFACEs', 
		entitylayer_from='obj.data.name', 
		entitycolor_from='obj.layer', 
		entityltype_from='CONTINUOUS', 
		layerName_from='LAYERNAME_DEF', 
		verbose=True)
		


def export_plates(filename):
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')

	#bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
	#bpy.ops.uv.export_layout(filepath="plates1.svg", mode='SVG', size=(1024, 1024))

	bpy.ops.uv.smart_project(stretch_to_bounds=False,island_margin=0.3)
	bpy.ops.uv.export_layout(filepath=filename, mode='SVG', size=(10000, 10000))

	bpy.ops.object.mode_set(mode='OBJECT')


def exportCSV():

	# aluminum 5083 density 2650 KG / M3

	with open('hull_export.csv', 'w', newline='') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)

		csv_row = []

		csv_row.append("name")
		csv_row.append("X")
		csv_row.append("Y")
		csv_row.append("Z")

		csv_row.append("volume")

		csv_row.append("face_count")
		csv_row.append("surface_area")

		csvWriter.writerow(csv_row)

		#for obj in bpy.context.selected_objects:
		for obj in bpy.data.objects:

			if obj.type=="MESH":

				if obj.hide_viewport==False:

					csv_row = []
					csv_row.append(obj.name)
					csv_row.append(obj.location.x)
					csv_row.append(obj.location.y)
					csv_row.append(obj.location.z)

					vol=measure_object_volume(obj)
					csv_row.append(vol)

					face_data=measure_selected_faces_area(obj,True)
					csv_row.append(face_data[0])
					csv_row.append(face_data[1])

					csvWriter.writerow(csv_row)
