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
from math import radians, degrees
from bpy.props import *
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty


from ..hullgen import curve_helper
from ..hullgen import material_helper

bouyancy_text_object=None
bouyancy_text_object_name="bouyancy_text"
CG_object_name="CG"

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

	face_data=[selected_face_count,total_area]

	return face_data


def make_water_volume():


	# Water volume
	water_object_name="water_volume"

	curve_helper.find_and_remove_object_by_name(water_object_name)

	depth=5
	width=5
	length=15

	bpy.ops.mesh.primitive_cube_add(size=1, 
		enter_editmode=False, 
		location=(0,0,-depth/2))

	water_volume=bpy.context.view_layer.objects.active

	bpy.ops.transform.resize(value=(length,width,depth))

	bpy.ops.object.transform_apply(scale=True,location=False)

	water_volume.name=water_object_name
	water_volume.display_type="WIRE"

	water_material=material_helper.make_glass_material("water",(0,0,0.8,0))

	material_helper.assign_material(water_volume,water_material)

	# Displacement area
	water_displaced_name="water_displaced"

	curve_helper.find_and_remove_object_by_name(water_displaced_name)

	displace_depth=depth-0.5
	displace_width=width-0.5
	displace_length=length=length-0.5

	bpy.ops.mesh.primitive_cube_add(size=1, 
		enter_editmode=False, 
		location=(0,0,-displace_depth/2))

	water_displaced_volume=bpy.context.view_layer.objects.active

	bpy.ops.transform.resize(value=(displace_length,displace_width,displace_depth))

	bpy.ops.object.transform_apply(scale=True,location=False)

	water_displaced_volume.name=water_displaced_name
	water_displaced_volume.display_type="WIRE"

	water_displaced_material=material_helper.make_glass_material("water",(1,0,0.8,0))

	material_helper.assign_material(water_displaced_volume,water_displaced_material)

	return (water_volume,water_displaced_volume)


def frame_change_handler(scene):
	current_frame=bpy.context.scene.frame_current
	
	weight=0

	if CG_object_name in bpy.data.objects:
		CG_object=bpy.data.objects[CG_object_name]
		if "displacement_data" in CG_object:
			displacement_data=CG_object["displacement_data"]

			if current_frame > 0:
				if current_frame-1 < len(displacement_data):	
					weight=displacement_data[current_frame-1]
				else:
					# if you scroll past last frame - use last weight (heaviest)
					weight=displacement_data[len(displacement_data)-1]

	if bouyancy_text_object_name in bpy.data.objects:
		bouyancy_text_object=bpy.data.objects[bouyancy_text_object_name]

	bouyancy_text_object.data.body="Weight: %0.02fkg"%(weight)
	
def register_text_update_callback():
	if frame_change_handler not in bpy.app.handlers.render_complete:
		bpy.app.handlers.frame_change_post.append(frame_change_handler)

#def unregister():
#    bpy.app.handlers.frame_change_post.remove(my_handler)

# Submerge until is a cutoff - solve until this number
# hull should float before this number but just in case this prevents endless solving
def submerge_boat(hull_object,weight,submerge_until=-3):

	bpy.context.scene.frame_set(1)

	register_text_update_callback()

	if bouyancy_text_object_name in bpy.data.objects:
		bouyancy_text_object=bpy.context.scene.objects[bouyancy_text_object_name]
	else:
		bpy.ops.object.text_add(enter_editmode=False, location=(0, 0, hull_object.dimensions[2]+1))
		bouyancy_text_object=bpy.context.view_layer.objects.active
		bouyancy_text_object.name=bouyancy_text_object_name
		bpy.ops.transform.rotate(value=radians(-90),orient_axis='X')
		bouyancy_text_object.data.extrude = 0.05

	cg_empty=calculate_cg([hull_object])
	displacement_data=[]

	continueSolving=True

	hull_weight=weight

	frames_solved=0

	# start hull off above water
	hull_object.location.z=hull_object.dimensions[2]

	while continueSolving==True:

		water_volumes=make_water_volume()

		water_displaced_volume=water_volumes[1]
		water_volume=water_volumes[0]

		displacement_modifier_name="water_displaced"
		bool_water_displaced = water_displaced_volume.modifiers.new(type="BOOLEAN", name=displacement_modifier_name)
		bool_water_displaced.object = hull_object
		bool_water_displaced.operation = 'INTERSECT'
		curve_helper.select_object(water_displaced_volume,True)
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier=displacement_modifier_name)
		bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

		current_frame=bpy.context.scene.frame_current
		frames_solved+=1

		displaced_volume=measure_object_volume(water_displaced_volume)

		# displaced water 1 cubic meter =1000kg
		displaced_weight=displaced_volume*1000

		hull_object.keyframe_insert(data_path="location", frame=current_frame) #, index=0)
		bpy.context.scene.frame_set(current_frame+1)

		# Abort if hull more than 3m under water... something went wrong
		if hull_object.location.z<submerge_until:
			continueSolving=False

		print("submerge frame: %d HullZ: %0.03f displaced_weight/hull: %0.3f/%0.3f BouyancyZ: %0.03f"%(
			frames_solved,
			hull_object.location.z,
			displaced_weight,
			hull_weight,
			water_displaced_volume.location.z
			))

		displacement_data.append(displaced_weight)

		if displaced_weight<hull_weight:
			hull_object.location.z-=0.01
		else:
			continueSolving=False

	cg_empty["displacement_data"]=displacement_data

	# mark end of submersion animation
	bpy.context.scene.frame_end=bpy.context.scene.frame_current

# returns empty object representing center of gravity location
def calculate_cg(influence_objects):

	curve_helper.find_and_remove_object_by_name(CG_object_name)

	bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
	cg_empty = bpy.context.active_object
	cg_empty.name=CG_object_name

	# Moment = weight * arm

	total_weight=0
	total_moment=[0,0,0]
	cg_pos=[0,0,0]

	for obj in influence_objects:

		bpy.ops.object.select_all(action='DESELECT')
		curve_helper.select_object(obj,True)
		bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

		object_volume=measure_object_volume(obj)

		face_data=measure_selected_faces_area(obj,True)

		# object surface area in m2
		object_face_area=face_data[1]

		# hard coded to 5083 aluminum for now
		# expressed as KG per m3
		material_weight=2653

		# hdpe 970 KG per m3

		# hard coded 3mm for now
		material_thickness=0.003

		object_weight=material_thickness*material_weight*object_face_area

		total_weight=total_weight+object_weight

		# Calculate 3D moment tuple for this influence object
		object_moment=[	object_weight*obj.location.x,
						object_weight*obj.location.y,
						object_weight*obj.location.z ]

		total_moment[0]=total_moment[0]+object_moment[0]
		total_moment[1]=total_moment[1]+object_moment[1]
		total_moment[2]=total_moment[2]+object_moment[2]

		assign_weight(obj,object_weight)



	if total_weight>0:
		# offset center of gravity by moment
		cg_pos[0]=total_moment[0]/total_weight
		cg_pos[1]=total_moment[1]/total_weight
		cg_pos[2]=total_moment[2]/total_weight

		print("Total weight: %d KG CG: %f %f %f"%(total_weight,cg_pos[0],cg_pos[1],cg_pos[2]))

		
		cg_empty.location[0]=cg_pos[0]
		cg_empty.location[1]=cg_pos[1]
		cg_empty.location[2]=cg_pos[2]
	else:
		# prevent divide by zero
		print("Something went wrong... no total weight calculated")

	assign_weight(cg_empty,total_weight)
	
	return cg_empty
	

def import_plates(filename):

	bpy.ops.import_curve.svg(filepath=filename)

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
		bpy.ops.object.convert(target='MESH')
		bpy.ops.object.join()
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.remove_doubles()
		bpy.ops.mesh.select_mode(type="EDGE")
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')

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
	bpy.ops.uv.export_layout(filepath=filename, mode='SVG', size=(2400, 2400),opacity=1)

	bpy.ops.object.mode_set(mode='OBJECT')


def exportCSV():

	with open('hull_export.csv', 'w', newline='') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)

		csv_row = []

		csv_row.append("name")
		csv_row.append("posX")
		csv_row.append("posY")
		csv_row.append("posZ")

		csv_row.append("volume")

		csv_row.append("face_count")
		csv_row.append("surface_area")

		csv_row.append("sizeX")
		csv_row.append("sizeY")
		csv_row.append("sizeZ")

		csvWriter.writerow(csv_row)

		#for obj in bpy.context.selected_objects:
		#for obj in bpy.data.objects:
		for obj in bpy.context.view_layer.objects:

			if obj.type=="MESH":

				print("export: %s %s"%(obj.name,obj.type))

				if curve_helper.is_object_hidden_from_view(obj)==False:
				#if obj.hide_viewport==False:

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

					csv_row.append(obj.dimensions.x)
					csv_row.append(obj.dimensions.y)
					csv_row.append(obj.dimensions.z)

					csvWriter.writerow(csv_row)

		csv_row = [" "]
		csvWriter.writerow(csv_row)

		csv_row = ["mm","0.001"]
		csvWriter.writerow(csv_row)

		csv_row = ["5083 aluminum","2653","KG per M3"]
		csvWriter.writerow(csv_row)

		csv_row = ["steel","7900","KG per M3"]
		csvWriter.writerow(csv_row)

		csv_row = ["wood","400","KG per M3"]
		csvWriter.writerow(csv_row)


def assign_weight(obj,weight):

	rna_ui = obj.get('_RNA_UI')
	if rna_ui is None:
		rna_ui = obj['_RNA_UI'] = {}

	rna_ui = obj.get('_RNA_UI')

	# property attributes.for UI 
	rna_ui["weight"] = {"description":"Multiplier for Scale",
					"default": 1.0,
					"min":0.0,
					"max":10.0,
					"soft_min":0.0,
					"soft_max":10.0,
					"is_overridable_library":False
					}

	obj["weight"]=weight




