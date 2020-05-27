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

import queue

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

	water_material=material_helper.make_subsurf_material("water",(0,0,0.8,0))

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

	water_displaced_material=material_helper.make_subsurf_material("water",(1,0,0.8,0))

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

	bouyancy_text_object.data.body="Displacement: %0.02fkg"%(weight)
	
def register_text_update_callback():
	if frame_change_handler not in bpy.app.handlers.render_complete:
		bpy.app.handlers.frame_change_post.append(frame_change_handler)

#def unregister():
#    bpy.app.handlers.frame_change_post.remove(my_handler)


# calculates amount to rotate (around X or Y axis) to solve simulation
# larger arm = more movement (faster rotation)
# arm = weight X moment
def calculate_rotate_step(rotate_arm):

	rotate_step=0.05

	if rotate_arm<0.1:
		rotate_step=0.01
	elif rotate_arm<0.5:
		rotate_step=0.05
	elif rotate_arm<1:
		rotate_step=0.1
	else:
		rotate_step=0.25

	return rotate_step

def calculate_movement_step(move_arm):

	move_step=move_arm

	if move_step<10:
		move_step=0.0001
	elif move_arm<50:
		move_step=0.001
	elif move_arm<100:
		move_step=0.008
	else:
		move_step=0.01

	return move_step
		
def submerge_boat(hull_object,weight,
			simulate_depth,
			simulate_pitch,
			simulate_roll,
			force_roll_max,
			csv_output_file):


	weightQueueSize=5
	weightQueue = queue.Queue(weightQueueSize)

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
		bouyancy_text_object.data.size=0.6

	csvWriter=None
	csvfile=None

	if csv_output_file!=None:

		csvfile = open(csv_output_file, 'w', newline='')
		csvWriter = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)

		csv_row = []

		csv_row.append("frame")

		csv_row.append("displacement_diff")
		csv_row.append("displaced_weight")
		csv_row.append("Z_step")
		csv_row.append("hullZ")
		
		csv_row.append("rotation_Y")
		csv_row.append("pitch_arm")
		csv_row.append("pitch_step")

		csv_row.append("rotation_X")
		csv_row.append("roll_arm")
		csv_row.append("roll_step")

		csvWriter.writerow(csv_row)

	hull_object.animation_data_clear()

	bpy.context.scene.frame_set(bpy.context.scene.frame_start)

	cg_empty=calculate_cg([hull_object])
	displacement_data=[]

	continueSolving=True

	hull_weight=weight

	simulation_step=0

	force_roll_current=0

	#water_volume_phantom=None

	# start hull off above water - start at the height of the hull
	hull_object.location.z=hull_object.dimensions[2]

	while continueSolving==True:

		# =======================================================
		# Create water volume and booleans for calculating displacement
		# =======================================================

		# It's slower to recreate volume each time but we need to APPLY the bool modifier to calculate the center of mass...
		water_volumes=make_water_volume()

		water_displaced_volume=water_volumes[1]
		water_displaced_volume.show_axis = True

		water_volume=water_volumes[0]

		displacement_modifier_name="water_displaced"
		bool_water_displaced = water_displaced_volume.modifiers.new(type="BOOLEAN", name=displacement_modifier_name)
		bool_water_displaced.object = hull_object
		bool_water_displaced.operation = 'INTERSECT'

		#if water_volume_phantom==None:
			# Create a copy "the phantom object" of the water displaced volume because we need to apply bool modifier each time...
			# Keep a copy that will be used during rendering
		#	curve_helper.select_object(water_displaced_volume,True)
		#	bpy.ops.object.duplicate_move()
		#	water_displaced_volume_phantom=bpy.context.view_layer.objects.active

		#bpy.ops.object.select_all(action='DESELECT')

		curve_helper.select_object(water_displaced_volume,True)

		# Calculate center of mass for displaced water
		# I tried to calculate mass without applying boolean modifier and it doesn't used the post bool modifier data so we have to do it the slow way
		# It's much slower to apply modifier each part of the simulation but I can't find any other way to solve this problem. 
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier=displacement_modifier_name)
		bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

		simulation_step+=1


		# =======================================================
		# Calculate hydro physics status of current state
		# =======================================================

		displaced_volume=measure_object_volume(water_displaced_volume)

		# displaced water 1 cubic meter =1000kg (Aprox - not factoring for temp or saltwater ect..)
		displaced_weight=displaced_volume*1000

		displacement_diff=abs(displaced_weight-hull_weight)
		pitch_arm=water_displaced_volume.location.x-hull_object.location.x
		roll_arm=water_displaced_volume.location.y-hull_object.location.y
		
		abs_pitch_arm=abs(pitch_arm)
		abs_roll_arm=abs(roll_arm)

		# Arm solve threshold for finish solving (pitch and roll)
		arm_solve_threshold=0.005 # Solve rotation within 5mm arm
		weight_solve_threshold=5 # solve bouyancy displacement within 5kg

		# =======================================================
		# Maintain a history (queue) of displacement weights to detect velocity trend... 
		# =======================================================	
		queueSum=0

		for i in range(0,weightQueue.qsize()):
			#print("weight: %f average: %f"%(weightQueue.queue[i][0],weightQueue.queue[i][1]))
			queueSum+=weightQueue.queue[i][0]

		# calculate average displacement for last simulation steps
		# If current displacement is same or similar to queue Average - our velocity is stable
		# If current displacement is less than queue average - we bounced up
		# If current displacement is more than queue average - we are sinking
		queueAverage=queueSum/weightQueueSize

		if weightQueue.full():
			weightQueue.get()

		weightQueue.put([displaced_weight,queueAverage])

		# Cache last roll angle to detect roll movement
		last_roll_y=degrees(hull_object.rotation_euler.y)


		# =======================================================
		# Detect if we should abort or continue simulation
		# =======================================================		


		# Abort if hull deeper than water volume... something went wrong
		if hull_object.location.z>water_volume.dimensions.z:
			print("Aborting... Hull Z: %f > water height: %f"%(hull_object.location.z,water_volume.dimensions.z))
			continueSolving=False

		# Abort if runaway...
		if simulation_step>6000:
			continueSolving=False

		#print("submerge frame: %d HullZ: %0.03f displaced_weight/hull: %0.3f/%0.3f BouyancyZ: %0.03f"%(
		#	simulation_step,
		#	hull_object.location.z,
		#	displaced_weight,
		#	hull_weight,
		#	water_displaced_volume.location.z
		#	))

		if force_roll_max==0:

			# If we aren't doing a forced rollover test - detect if simulation is complete

			if ( (simulate_pitch and abs_pitch_arm<arm_solve_threshold) or simulate_pitch==False) and \
				( (simulate_roll and abs_roll_arm<arm_solve_threshold) or simulate_roll==False) and \
				( (simulate_depth and displacement_diff<weight_solve_threshold) or simulate_depth==False):
				continueSolving=False
		else:

			# Abort forced rollover test when we reach the max rollover angle

			if force_roll_current>=force_roll_max:
					continueSolving=False


		curve_helper.select_object(hull_object,True)

		# =======================================================
		# Adjust pitch part of simulation
		# =======================================================
		pitch_step=0

		if simulate_pitch==True:
			# Only rotate once object hits the water
			if displaced_weight>0:

				pitch_step=calculate_rotate_step(abs_pitch_arm)

				if pitch_arm>arm_solve_threshold:
					bpy.ops.transform.rotate(value=radians(pitch_step),orient_axis='Y')
				elif pitch_arm<arm_solve_threshold:
					bpy.ops.transform.rotate(value=radians(-pitch_step),orient_axis='Y')

		# =======================================================
		# Adjust roll part of simulation
		# =======================================================
		roll_step=0
		degrees_rolled=0

		if force_roll_max>0:
			# If we are doing a forced rollover test - only roll over one degree if bouyancy displacement has reached equilibrium 

			if ( (simulate_depth and displacement_diff<weight_solve_threshold) or simulate_depth==False):
				degrees_rolled=1
				force_roll_current+=degrees_rolled
				hull_object.rotation_euler.x=radians(force_roll_current)

		elif simulate_roll==True:
			# Only rotate once object hits the water
			if displaced_weight>0:

				roll_step=calculate_rotate_step(abs_roll_arm)

				if roll_arm>arm_solve_threshold:
					bpy.ops.transform.rotate(value=radians(-roll_step),orient_axis='X')
				elif pitch_arm<arm_solve_threshold:
					bpy.ops.transform.rotate(value=radians(roll_step),orient_axis='X')

		# =======================================================
		# Adjust water submersion depth (Z position) part of simulation
		# =======================================================
		z_step=calculate_movement_step(displacement_diff)

		average_threshold=5

		if (queueAverage+average_threshold)<hull_weight:
			hull_object.location.z-=z_step
		elif (queueAverage-average_threshold)>hull_weight:
			hull_object.location.z+=z_step


		# =======================================================
		# Bake simulation steps into keyframes
		# =======================================================

		# To make the resulting output animation smoother we should skip some keyframes frames that are considered subframes in the simulation.
		# Subframes are not rendered but used for the calculation...

		if force_roll_max==0 or (force_roll_max>0 and degrees_rolled>0):

			# If a forced roll test - only log steps when roll degrees change
			# If not force roll test - log all frames of simulation

			current_frame=bpy.context.scene.frame_current
			hull_object.keyframe_insert(data_path="location", frame=current_frame) #, index=0)
			hull_object.keyframe_insert(data_path="rotation_euler", frame=current_frame) #, index=0)
			bpy.context.scene.frame_set(current_frame+1)

			# =======================================================
			# Log results and reporting part of simulation
			# =======================================================

			# Cache weight for frame (used in frame_change_handler function)
			displacement_data.append(displaced_weight)

			if csvWriter!=None:

				# only log once it's reached equilibrium if doing roll test
				#if force_roll_max==0 or (simulate_depth and displacement_diff<weight_solve_threshold):

				print("Log CSV")

				csv_row = []

				csv_row.append(simulation_step) #1

				csv_row.append("%f"%displacement_diff) #2
				csv_row.append("%f"%displaced_weight) #3
				csv_row.append("%f"%z_step) #4

				csv_row.append("%f"%hull_object.location.z) #5

				csv_row.append("%f"%degrees(hull_object.rotation_euler.y))  #6 pitch
				csv_row.append("%f"%pitch_arm) #7
				csv_row.append("%f"%pitch_step) #8

				csv_row.append("%f"%degrees(hull_object.rotation_euler.x)) #9 roll
				csv_row.append("%f"%roll_arm) #10
				csv_row.append("%f"%roll_step) #11

				csvWriter.writerow(csv_row)

		statusText=("step:%d queue(sum:%f average:%f) dispdiff:%f zstep:%f yRot:%f Yarm:%f xRot:%f Xarm:%f forceroll(%f/%f)"%(
						simulation_step,
						queueSum,
						queueAverage,
						displacement_diff,
						z_step,
						degrees(hull_object.rotation_euler.y),
						pitch_arm,
						degrees(hull_object.rotation_euler.x),
						roll_arm,
						force_roll_current,
						force_roll_max
						))

		print(statusText)
		
		bpy.context.workspace.status_text_set(statusText)	

		# Update viewport
		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		#bpy.context.view_layer.update()
	

	if csvfile!=None:
		csvfile.close()	

	cg_empty["displacement_data"]=displacement_data

	# mark end of submersion animation
	bpy.context.scene.frame_end=bpy.context.scene.frame_current

# returns empty object representing center of gravity location
def calculate_cg(influence_objects):

	title_object=influence_objects[0]
	CG_object_name

	curve_helper.find_and_remove_object_by_name(CG_object_name)

	bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
	cg_empty = bpy.context.active_object
	cg_empty.name=CG_object_name
	cg_empty.empty_display_type = 'SPHERE'


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

		print("Object: %s Weight: %f KG Total weight: %d KG"%(obj.name,object_weight,total_weight))

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

	default_material=material_helper.get_material_default()

	# First make 
	for obj in bpy.data.objects:
		if obj.type=="MESH":
			if len(obj.data.materials)==0:
				material_helper.assign_material(obj,default_material)

			if obj.data.materials[0]==None:
				material_helper.assign_material(obj,default_material)

	try:
		bpy.ops.export.dxf(filepath="bpyhullgen.dxf", 
		projectionThrough='NO', 
		onlySelected=True, 
		apply_modifiers=True, 
		mesh_as='3DFACEs', 
		entitylayer_from='obj.data.name', 
		entitycolor_from='obj.layer', 
		entityltype_from='CONTINUOUS', 
		layerName_from='LAYERNAME_DEF', 
		verbose=True)
	except Exception as e:
			print("DXF export failed - check export DXF addon is installed?")
			return False
	
	
		


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
					"max":100000.0,
					"soft_min":0.0,
					"soft_max":10000.0,
					"is_overridable_library":False
					}

	obj["weight"]=weight

def scale_to_size(scale_to_size):

	distance=get_distance_between_two_selected_points()
	print("Scale to: %f %f"%(scale_to_size,distance))

	if distance==0:
		print("Invalid points (Please select 2 points)")
		return

	scale_factor=1/(distance/scale_to_size)

	print("Distance: %f Scale to: %f Scale factor: %f"%(distance,scale_to_size,scale_factor))

	bpy.ops.object.mode_set(mode='OBJECT')

	for obj in bpy.data.objects:

		if obj.type=="MESH":
			curve_helper.select_object(obj,True)

			bpy.ops.transform.resize(value=(scale_factor,scale_factor,scale_factor))




# Gets the distance between two selected vertices on selected object
# Assumes you are in edit mode and have only 2 vertices selected
def get_distance_between_two_selected_points():

	obj = bpy.context.object
	
	selected_vertices=[]
	
	if obj==None:
		print("No Object Selected")
		return 0
	
	# cycle between edit mode and object mode to ensure selections are propogated
	# from temporary copy
	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.mode_set(mode='EDIT')


	for v in bpy.context.active_object.data.vertices:
		if v.select:
			print(str(v.select))
			co_final =  obj.matrix_world @ v.co
			print(co_final)
			selected_vertices.append(co_final)
			
	print(len(selected_vertices))
		
	if len(selected_vertices)>2:
		print("Please select only 2 vertices")
		return 0
	
	distance=(selected_vertices[0]-selected_vertices[1]).length
	
	print("Distance: %f"%(distance))

	return distance
		


