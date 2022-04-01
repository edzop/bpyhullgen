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
import math
from math import radians, degrees

from ..hullgen import curve_helper
from ..bpyutils import material_helper
from ..bpyutils import bpy_helper
from ..hullgen import geometry_helper
from ..bpyutils import bpy_helper

class longitudinal_definition:
	z_offset=0
	width=0.1
	thickness=0.1

	# ratio of longitudinal to slicer means how high the slicers are in relation to longitudinals
	# If it's 0.5 it will be half - it affects the notches height for bulkheads 
	slicer_ratio=0.3

	bend_radius=0
	curve_angle=0

	limit_x_min=0
	limit_x_max=0

	def set_limit_x_length(self,min,max):
		self.limit_x_max=max
		self.limit_x_min=min

	def set_curve(self,radius,angle):
		self.curve_angle=angle
		self.bend_radius=radius

	def __init__(self,z_offset=0,width=0.1,thickness=0.1,slicer_ratio=0.7):
		self.z_offset=z_offset
		self.width=width
		self.thickness=thickness
		self.slicer_ratio=slicer_ratio


class chine_instance:
	curve_object=None
	curve_backup=None
	inverted=True

	longitudinal_objects=None
	longitudinal_slicers=None

	longitudinal_slicers_slot_gap_objects=None
	longitudinal_slicers_end_cut_objects=None

	def __init__(self,curve_object,curve_backup,inverted):
		self.curve_object=curve_object
		self.curve_backup=curve_backup
		self.inverted=inverted
		self.longitudinal_objects=[]
		self.longitudinal_slicers=[]
		self.longitudinal_slicers_slot_gap_objects=[]
		self.longitudinal_slicers_end_cut_objects=[]

	def add_longitudinal_instance(self,longitudinal_object,longitudinal_slicer):
		self.longitudinal_objects.append(longitudinal_object)
		self.longitudinal_slicers.append(longitudinal_slicer)



class chine_definition:

	rotation=[0,0,0]
	offset=[0,0,0]
	name="chine_"

	the_hull=None
	symmetrical=True

	longitudinal_elements_enabled=True

	curve_length=12
	curve_width=1.2

	curve_height=1

	extrude_width=1

	asymmetry=[0,0]

	# amount of distance slicer is poking through skin to ensure clean geometry
	skin_pokethrough=0.01

	longitudinal_definitions=None

	chine_instances=None

	chine_core_instances=None
	chine_core_offset=0.1

	longitudinal_screw_positions=None
 

	# view collections
	view_collection_chines=None
	view_collection_longitudinals=None

	# how big to make screws in computer model so they output correctly when scaled output
	# hull object has hull_scale object for scale models...
	scaled_screw_size=10 

	def add_chine_instance(self,new_instance):
		self.chine_instances.append(new_instance)

	def add_chine_core_instance(self,new_instance):
		self.chine_core_instances.append(new_instance)

	def add_longitudinal_definition(self,new_element):
		self.longitudinal_definitions.append(new_element)


	
	def __init__(self,the_hull,name,length,width,rotation=[0,0,0],offset=[0,0,0],asymmetry=[0,0],symmetrical=True):
		self.the_hull=the_hull

		self.longitudinal_screw_positions=[]
		self.longitudinal_definitions=[]
		self.chine_instances=[]
		self.chine_core_instances=[]

		self.name=name
		self.curve_length=length
		self.curve_width=width

		self.offset=offset
		self.asymmetry=asymmetry
		self.rotation=rotation
		self.symmetrical=symmetrical

		self.longitudinal_thickness=the_hull.structural_thickness
		
		self.curve_height=the_hull.hull_height


		self.extrude_width=the_hull.hull_height*3

		self.view_collection_chines=bpy_helper.make_collection("chines",bpy.context.scene.collection.children)
		self.view_collection_longitudinals=bpy_helper.make_collection("longitudinals",bpy.context.scene.collection.children)


	def delete_all_vertex_group(self,ob,vertex_group_name):
		ob.select_set(state=True)

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_set_active(group=vertex_group_name)
		bpy.ops.object.vertex_group_select()
		bpy.ops.mesh.delete(type='VERT')

 
	# After the boolean operation is complete the vertices can be removed that are on the other side
	# of the plane used for the boolean operation. 
	def delete_all_except_vertex_group(self,ob,vertex_group_name):
		ob.select_set(state=True)

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_set_active(group=vertex_group_name)
		bpy.ops.object.vertex_group_select()
		bpy.ops.mesh.select_all(action='INVERT')
		bpy.ops.mesh.delete(type='VERT')

		# Old implementation fails because new exact boolean modifier inherits vertex groups
		# Hopefully this can be fixed... Previous fast implementation did not inherit vertex groups

		#bpy.ops.object.mode_set(mode='EDIT')
		#bpy.ops.mesh.select_all(action='DESELECT')
		#bpy.ops.object.vertex_group_set_active(group="back")
		#bpy.ops.object.vertex_group_select()
		#bpy.ops.mesh.delete(type='VERT')

		#bpy.ops.mesh.select_all(action='DESELECT')
		#bpy.ops.object.vertex_group_set_active(group="front")
		#bpy.ops.object.vertex_group_select()
		#bpy.ops.mesh.delete(type='VERT')

	
	# Creates a new secondary plane that will intersect the primary plane. This new secondary plane will act as the slicer
	# It marks the front and back vertex groups for reference later after boolean operation
	def create_slicer_plane_mesh(self,name,height,longitudinal_element,inverted_curves):
		
		bpy_helper.deselect_all_objects()

		theCurveHelper = curve_helper.Curve_Helper(curve_resolution=self.the_hull.curve_resolution)

		curve_angle=longitudinal_element.curve_angle
		bend_radius=longitudinal_element.bend_radius
	
		theCurveHelper.curve_angle=curve_angle

		theCurveHelper.define_curve(length=self.curve_length,width=bend_radius)
		theCurveHelper.curve_height=0

		theCurveHelper.generate_curve(name)
		newCurve=theCurveHelper.curve_object
		bpy_helper.select_object(newCurve,True)

		

		geometry_helper.set_rotation_degrees(newCurve,[90,0,0])

		bpy.ops.object.transform_apply(rotation=True,scale=False,location=False)


		bpy.ops.object.mode_set(mode='EDIT')
		
		# extrude thicknes along Y axis
		bpy.ops.mesh.select_all(action='SELECT')

		
		overlap_factor=self.curve_width*4
		
		#bpy.ops.mesh.normals_make_consistent(inside=False)
		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,self.curve_width*overlap_factor,0), 
										"constraint_axis":(False, False,True)})

		
		bpy.ops.mesh.select_all(action='DESELECT')

		bpy.ops.object.mode_set(mode='OBJECT')

		base_group = newCurve.vertex_groups.new()
		base_group.name = "base"
		base_verts=[]

		for vert in newCurve.data.vertices:
			base_verts.append(vert.index)
			
		base_group.add(base_verts, 1.0, 'ADD')
	
		newCurve.location.z=height

		y_shift=self.curve_width*overlap_factor/2

		bpy.ops.object.select_all(action='DESELECT')

		bpy.ops.object.mode_set(mode='EDIT')

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.transform.translate(value=(0, -y_shift, 0))

		bpy.ops.object.mode_set(mode='OBJECT')

		return newCurve
			
	# =====================================

	def select_and_extrude_slicer(self,slicer,amount):
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = slicer
		slicer.select_set(True)
				
		bpy.ops.object.mode_set(mode='EDIT')

		# extrude thicknes along Y axis
		bpy.ops.mesh.select_all(action='SELECT')

		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, amount, 0), 
										"constraint_axis":(False, True, False)})
		bpy.ops.object.mode_set(mode='OBJECT')

		bpy_helper.bmesh_recalculate_normals(slicer)
		

	# for symmetrical chines - if there is any curve in slicer plane - it needs to be inverted for opposite side (symmetrical)
	def make_slicer_plane(self,wall_curve,name,thickness,longitudinal_element,inverted_curves=False):

		name_prefix="cutter"

		# Add first plane
		slicer1=self.create_slicer_plane_mesh(name_prefix+name+".a",longitudinal_element.z_offset,longitudinal_element,inverted_curves)

		
		slicer1.select_set(True)
		bpy.context.view_layer.objects.active=slicer1

		
		bool_cut = slicer1.modifiers.new(type="BOOLEAN", name=name_prefix)
		bool_cut.object = wall_curve
		bool_cut.operation = 'DIFFERENCE'

		bpy.ops.object.modifier_apply(modifier=name_prefix)
				
		self.delete_all_vertex_group(slicer1,"base")
		
		slicer1.select_set(False)
		
		# Add second plane
		slicer2=self.create_slicer_plane_mesh(name_prefix+name+".b",longitudinal_element.z_offset-thickness,longitudinal_element,inverted_curves)
   
		slicer2.select_set(True)		
		bpy.context.view_layer.objects.active=slicer2
		
		
		bool_cut = slicer2.modifiers.new(type="BOOLEAN", name=name_prefix)
		bool_cut.object = wall_curve
		bool_cut.operation = 'DIFFERENCE'

	
		bpy.context.view_layer.objects.active=slicer2

		bpy.ops.object.modifier_apply(modifier=name_prefix)
   
		#self.delete_all_except_vertex_group(slicer2,"back")
		self.delete_all_vertex_group(slicer1,"base")

		bpy.ops.object.mode_set(mode='OBJECT')

		slicer1.select_set(True)
		slicer2.select_set(True)

		bpy.ops.object.join()
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')

		bpy.ops.mesh.bridge_edge_loops()

		bpy.ops.object.mode_set(mode='OBJECT')

		# joining 2 objects sets the origin to the last selected object
		# so shift the object down so origin is at center of object (thickness/2)
		bpy.ops.transform.translate(value=(0, 0, -(thickness/2)))
		

		slicer2.location.z+=thickness

		# second object selected is left over after join
		slicer2.name=name_prefix+name
		
		return slicer2
	

	def make_longitudinal_element(self,chine_instance,longitudinal_element,index):
		longitudinal_plane=None

		longitudinal_name="%s.longitudinal.%02d"%(chine_instance.curve_object.name,index)
		slicer_name="%s.slicer.%02d"%(chine_instance.curve_object.name,index)
		slicer_stop_gap_name="%s.slicer_stop_gap.%02d"%(chine_instance.curve_object.name,index)

		# longitudinal Plane

		longitudinal_plane=self.make_slicer_plane(
			wall_curve=chine_instance.curve_object,
			name=longitudinal_name,
			longitudinal_element=longitudinal_element,
			thickness=longitudinal_element.thickness,

			inverted_curves=chine_instance.inverted)

		material_helper.assign_material(longitudinal_plane,material_helper.get_material_stringer())

		

		extrude_amount=-longitudinal_element.width
		slicer_extrude_amount=-longitudinal_element.width*longitudinal_element.slicer_ratio

		if chine_instance.inverted:
			extrude_amount=longitudinal_element.width
			slicer_extrude_amount=longitudinal_element.width*longitudinal_element.slicer_ratio
							
		self.select_and_extrude_slicer(longitudinal_plane,extrude_amount)



		# Slicer Plane
			
		slicer_plane=None

		slicer_thickness=longitudinal_element.thickness*self.the_hull.slicer_overcut_ratio
	
		slicer_plane=self.make_slicer_plane(
			wall_curve=chine_instance.curve_object,
			name=slicer_name,
			longitudinal_element=longitudinal_element,
			thickness=slicer_thickness,
			inverted_curves=chine_instance.inverted)

		
		material_helper.assign_material(slicer_plane,material_helper.get_material_support())
		
			
		self.select_and_extrude_slicer(slicer_plane,slicer_extrude_amount)
		
		slicer_plane.parent=longitudinal_plane

		slicer_plane.location.z=0-((slicer_thickness-longitudinal_element.thickness)/2)

		longitudinal_plane.parent=chine_instance.curve_object
		longitudinal_plane.matrix_parent_inverse = chine_instance.curve_object.matrix_world.inverted()

		if chine_instance.inverted:

			if self.curve_width<0:
				slicer_plane.location.y=-self.skin_pokethrough
			else:
				slicer_plane.location.y=self.skin_pokethrough
		
		else:

			if self.curve_width<0:
				slicer_plane.location.y=self.skin_pokethrough
			else:
				slicer_plane.location.y=-self.skin_pokethrough

		
		chine_instance.add_longitudinal_instance(longitudinal_plane,slicer_plane)

		# chop ends off if needed (based on X limits)
		if longitudinal_element.limit_x_max!=0 and longitudinal_element.limit_x_min!=0:

			block_width=self.the_hull.hull_length

			adjusted_min_location=longitudinal_element.limit_x_min
			adjusted_min_location-=block_width/2

			adjusted_max_location=longitudinal_element.limit_x_max
			adjusted_max_location+=block_width/2

			end_clean_min_name="end_clean_min_%f"%(adjusted_min_location)
			end_clean_max_name="end_clean_max_%f"%(adjusted_max_location)

			object_end_clean_min = bpy.data.objects.get(end_clean_min_name)
			object_end_clean_max = bpy.data.objects.get(end_clean_max_name)

			if object_end_clean_min is None:
				object_end_clean_min = geometry_helper.make_cube(end_clean_min_name,location=[adjusted_min_location,0,0],size=(block_width,block_width,self.the_hull.hull_height))
				bpy_helper.move_object_to_collection(self.view_collection_longitudinals,object_end_clean_min)
				object_end_clean_min.hide_viewport=True
				object_end_clean_min.hide_render=True

			if object_end_clean_max is None:
				object_end_clean_max = geometry_helper.make_cube(end_clean_max_name,location=[adjusted_max_location,0,0],size=(block_width,block_width,self.the_hull.hull_height))
				bpy_helper.move_object_to_collection(self.view_collection_longitudinals,object_end_clean_max)
				object_end_clean_max.hide_viewport=True
				object_end_clean_max.hide_render=True

			bool_new = longitudinal_plane.modifiers.new(type="BOOLEAN", name="Lm")
			bool_new.object = object_end_clean_min
			bool_new.operation = 'DIFFERENCE'

			bool_new = longitudinal_plane.modifiers.new(type="BOOLEAN", name="Lx")
			bool_new.object = object_end_clean_max
			bool_new.operation = 'DIFFERENCE'

			bool_new = slicer_plane.modifiers.new(type="BOOLEAN", name="Sm")
			bool_new.object = object_end_clean_min
			bool_new.operation = 'DIFFERENCE'

			bool_new = slicer_plane.modifiers.new(type="BOOLEAN", name="Sx")
			bool_new.object = object_end_clean_max
			bool_new.operation = 'DIFFERENCE'

			chine_instance.longitudinal_slicers_end_cut_objects.append(object_end_clean_max)
			chine_instance.longitudinal_slicers_end_cut_objects.append(object_end_clean_min)


		if self.the_hull.slot_gap>0:
			
			bpy_helper.select_object(slicer_plane,True)

			y_offset=self.the_hull.slot_gap

			if chine_instance.inverted:
				y_offset=-y_offset

			bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, 
				TRANSFORM_OT_translate={"value":(0, 0, 0)})

			slicer_stop_gap_object=bpy.context.view_layer.objects.active

			slicer_stop_gap_object.parent=longitudinal_plane

			slicer_stop_gap_object.location.y=y_offset
			
			#chine_instance.longitudinal_slicers_slot_gap_objects.append(slicer_stop_gap_object)
			
			chine_instance.longitudinal_slicers_slot_gap_objects.append(slicer_stop_gap_object)
			bpy_helper.move_object_to_collection(self.view_collection_longitudinals,slicer_stop_gap_object)
			bpy_helper.hide_object(slicer_stop_gap_object)
			

		bpy_helper.move_object_to_collection(self.view_collection_longitudinals,slicer_plane)
		bpy_helper.hide_object(slicer_plane)

		bpy_helper.move_object_to_collection(self.view_collection_longitudinals,longitudinal_plane)


	

	def make_single_chine(self,twist=None,inverted=False,name_prefix="chine_",core_offset=0):

		theCurveHelper = curve_helper.Curve_Helper(curve_resolution=self.the_hull.curve_resolution)

		theCurveHelper.asymmetry=self.asymmetry

		bpy.ops.object.select_all(action='DESELECT')

		curve_name=name_prefix+self.name

		if self.symmetrical:
		   if inverted:
			   curve_name+=".R"
		   else:
			   curve_name+=".L"

		if twist!=None:
			if inverted:
				theCurveHelper.curve_twist[0]=-twist[0]
				theCurveHelper.curve_twist[1]=-twist[1]
				theCurveHelper.curve_twist[2]=-twist[2]
			else:
				theCurveHelper.curve_twist[0]=twist[0]
				theCurveHelper.curve_twist[1]=twist[1]
				theCurveHelper.curve_twist[2]=twist[2]

		theCurveHelper.make_backup=True
		theCurveHelper.define_curve(length=self.curve_length,width=self.curve_width)
		theCurveHelper.curve_height=self.curve_height
		theCurveHelper.generate_curve(curve_name)

		curve_object=theCurveHelper.curve_object

		material_helper.assign_material(curve_object,material_helper.get_material_bool())

		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
		theCurveHelper.extrude_curve(self.extrude_width)

		bpy_helper.select_object(curve_object,True)

		if inverted:
			geometry_helper.set_rotation_degrees(curve_object,[180,0,0])
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
					
		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
		bpy_helper.hide_object(curve_object)

		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_backup)
		bpy_helper.hide_object(theCurveHelper.curve_backup)


		new_chine_instance=chine_instance(curve_object,theCurveHelper.curve_backup,inverted)

		if core_offset==0:
			self.add_chine_instance(new_chine_instance)

			for i in range(len(self.longitudinal_definitions)):
				if self.longitudinal_elements_enabled==True:
					self.make_longitudinal_element(new_chine_instance,self.longitudinal_definitions[i],i)

		else:
			self.add_chine_core_instance(new_chine_instance)

		# Can only do rotation after we generate the longitudinal elements because the slicers
		# depend on zero rotation 

		if inverted:
			rotation_opposite=[-self.rotation[0],
							self.rotation[1],
							self.rotation[2],
							]

			if core_offset==0:
				geometry_helper.set_rotation_degrees(curve_object,rotation_opposite)
			curve_object.location.x=self.offset[0]
			curve_object.location.y=-self.offset[1]+core_offset
			curve_object.location.z=self.offset[2]
		else:
			if core_offset==0:
				geometry_helper.set_rotation_degrees(curve_object,self.rotation)

			curve_object.location=self.offset
			curve_object.location.y=-self.offset[1]-core_offset



		return curve_object

	def make_chine(self,twist=None):

		# ================================================================================================ 
		# First curve is Left Side or non-symmetrical "single side"
		# ================================================================================================
		base_curve=self.make_single_chine(twist=twist,inverted=False,name_prefix="chine_",core_offset=0)
		
		core_curve=self.make_single_chine(twist=twist,inverted=False,name_prefix="chine_bh_",core_offset=-self.chine_core_offset)

		core_curve.parent=base_curve


		# ================================================================================================ 
		# Second curve is Right Side
		# ================================================================================================
		if self.symmetrical:
			base_curve=self.make_single_chine(twist=twist,inverted=True,name_prefix="chine_",core_offset=0)

			core_curve=self.make_single_chine(twist=twist,inverted=True,name_prefix="chine_bh_",core_offset=-self.chine_core_offset)
			#self.curve_objects.append(newcurve)

			core_curve.parent=base_curve


	def make_segmented_longitudinals(self,z_offset,radius=0,angle=0,start_bulkhead=1,end_bulkhead=4,double_thick=True):

		#print("startb: %d endb: %d"%(start_bulkhead,end_bulkhead))

		total_bulkhead_distance=self.the_hull.bulkhead_count*self.the_hull.bulkhead_spacing
		eval_bulkhead_distance=(end_bulkhead*self.the_hull.bulkhead_spacing)-(start_bulkhead*self.the_hull.bulkhead_spacing)

		half_total_bulkhead_distance=total_bulkhead_distance/2

		print("total_distance: %f eval: %f half: %f"%(total_bulkhead_distance,
			eval_bulkhead_distance,
			half_total_bulkhead_distance))

		current_eval_location=self.the_hull.start_bulkhead_location+(self.the_hull.bulkhead_spacing*start_bulkhead)
		finish_eval_location=self.the_hull.start_bulkhead_location+(self.the_hull.bulkhead_spacing*end_bulkhead)

		current_eval_location-=self.the_hull.bulkhead_thickness
		finish_eval_location+=self.the_hull.bulkhead_thickness

		print("current_eval: %f finish eval: %f"%(current_eval_location,finish_eval_location))
		
		odd_spacing=True

		segment_thickness=0.1
		segment_index=0

		overlap_factor=0.2  # 20% overlap

		overlap_distance=self.the_hull.bulkhead_spacing*overlap_factor #actual overlap distance
		half_overlap_distance=overlap_distance/2
		end_segment_length=self.the_hull.bulkhead_spacing*1.5+half_overlap_distance
		full_segment_length=self.the_hull.bulkhead_spacing*2+overlap_distance

		print("chine end segment: %f full segment: %f"%(end_segment_length,full_segment_length))

		# check for < 50 to prevent runaway
		while current_eval_location<finish_eval_location and segment_index<50:

			if odd_spacing==True:
				adjusted_z_offset=z_offset
				odd_spacing=False
			else:
				adjusted_z_offset=z_offset-segment_thickness
				odd_spacing=True

			if (current_eval_location+full_segment_length<=finish_eval_location) and segment_index!=0:
				print("currenteval: %f full length"%current_eval_location)

				if double_thick==True:
					new_longitudinal=longitudinal_element(z_offset=adjusted_z_offset,width=-0.13,thickness=segment_thickness)
					new_longitudinal.set_limit_x_length(current_eval_location,current_eval_location+full_segment_length)
					new_longitudinal.set_curve(radius,angle)
					self.add_longitudinal_definition(new_longitudinal)
				
				
				new_longitudinal=longitudinal_element(z_offset=adjusted_z_offset-0.2,width=-0.13,thickness=segment_thickness)
				new_longitudinal.set_limit_x_length(current_eval_location,current_eval_location+full_segment_length)
				new_longitudinal.set_curve(radius,angle)
				self.add_longitudinal_definition(new_longitudinal)
					
				current_eval_location+=full_segment_length-overlap_distance
				self.longitudinal_screw_positions.append(current_eval_location-half_overlap_distance)

			else: # current_eval_location+end_segment_length<=finish_eval_location: # try end segment
				print("currenteval: %f remainder"%current_eval_location)

				station_end=finish_eval_location

				if segment_index==0:
					station_end=current_eval_location+end_segment_length+self.the_hull.bulkhead_thickness

				if station_end>finish_eval_location:
					station_end=finish_eval_location

				if double_thick==True:
					new_longitudinal=longitudinal_element(z_offset=adjusted_z_offset-0.2,width=-0.13,thickness=segment_thickness)
					new_longitudinal.set_limit_x_length(current_eval_location,station_end)
					new_longitudinal.set_curve(radius,angle)
					self.add_longitudinal_definition(new_longitudinal)
				
				new_longitudinal=longitudinal_element(z_offset=adjusted_z_offset,width=-0.13,thickness=segment_thickness)
				new_longitudinal.set_limit_x_length(current_eval_location,station_end)
				new_longitudinal.set_curve(radius,angle)
				self.add_longitudinal_definition(new_longitudinal)

				current_eval_location=station_end

				if current_eval_location<finish_eval_location:

					current_eval_location-=overlap_distance

				#if segment_index==0:
					#current_eval_location+=end_segment_length-overlap_distance
					self.longitudinal_screw_positions.append(current_eval_location)
				#else:
					#current_eval_location=finish_eval_location

				#if current_eval_location+end_segment_length>=finish_eval_location:
					
				#else:
	

			segment_index+=1
			print("currenteval: %f finishval: %f segindex: %d"%(current_eval_location,finish_eval_location,segment_index))

	def make_screws(self):

		scaleup_factor=1/self.the_hull.hull_output_scale
		self.scaled_screw_size=self.the_hull.target_screw_size*scaleup_factor/1000

		#print("target screw: %f scaleup factor: %f scaled_screw size: %f hull output scale: %f"%(self.target_screw_size,scaleup_factor,self.scaled_screw_size,self.the_hull.hull_output_scale))

		screw_objects=[]

		for chine_curve in self.curve_backups:
			for screw_position in self.longitudinal_screw_positions:
				bpy.ops.mesh.primitive_cylinder_add(radius=self.scaled_screw_size/2, depth=5, enter_editmode=False, location=[0,0,0])
				screw_object=bpy.context.view_layer.objects.active
				screw_object.name="screw_object_%d_%s"%(screw_position,self.name)
				
				screw_object.location.y=0.065
				screw_object.hide_viewport=True
				screw_objects.append(screw_object)

				bpy_helper.move_object_to_collection(self.view_collection_longitudinals,screw_object)

				path_follow = screw_object.constraints.new(type='FOLLOW_PATH')
				path_follow.target=chine_curve
				path_follow.use_fixed_location=True

				#curve_overlap=new_chine.curve_length-the_hull.hull_length

				
				curve_length=self.curve_length
				curve_hull_ratio=curve_length/self.the_hull.hull_length
				
				translated_screw_position=(curve_length/2)+(screw_position*curve_hull_ratio)
				translated_hull_start=curve_length*(curve_hull_ratio-1)/2
				offset_translated_position=translated_screw_position+translated_hull_start

				#print("curve length: %f curve extra ratio: %f"%(curve_length,curve_hull_ratio))
				#print("screw position: %f tr_screw_pos: %f tr hull start: %f offset tr screw: %f"%(
				#										screw_position,
				#										translated_screw_position,
				#										translated_hull_start,												
				#										offset_translated_position))

				offset_factor=offset_translated_position/curve_length
				
				path_follow.offset_factor=offset_factor

		for longitudinal_element_object in self.longitudinal_element_objects:

			for screw_object in screw_objects:
				modifier_name="screwhole_%s"%screw_object.name

				bool_new = longitudinal_element_object.modifiers.new(type="BOOLEAN", name=modifier_name)
				bool_new.object = screw_object
				bool_new.operation = 'DIFFERENCE'
