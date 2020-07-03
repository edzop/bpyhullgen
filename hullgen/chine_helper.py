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
from ..hullgen import material_helper
from ..hullgen import bpy_helper

class longitudal_element:
	z_offset=0
	width=0.1
	thickness=0.1

	# how much wider the slicers will be than the longitudals - value of 1.1 means notches will be 110 percent of longitudal
	slicer_overcut=1.1

	# ratio of longitudal to slicer means how high the slicers are in relation to longitudals
	# If it's 0.5 it will be half - it affects the notches height for bulkheads 
	slicer_ratio=0.5

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

	def __init__(self,z_offset,width=0.1,thickness=0.1):
		self.z_offset=z_offset
		self.width=width
		self.thickness=thickness

class chine_helper:

	rotation=[0,0,0]
	offset=[0,0,0]
	name="chine_"
	#curve_twist1=-20
	#curve_twist2=-20
	the_hull=None
	symmetrical=True

	bool_correction_offset=0

	curve_length=12
	curve_width=1.2

	curve_height=1

	extrude_width=1

	asymmetry=[0,0]

	# amount of distance slicer is poking through skin to ensure clean geometry
	skin_pokethrough=0.01

	curve_objects=None
	curve_backups=None
	longitudal_elements=None

	longitudal_element_objects=None
 

	# view collections
	view_collection_chines=None
	view_collection_longitudals=None
	view_collection_longitudal_slicers=None



	def add_longitudal_element(self,new_element):
#		new_element=longitudal_element(offset,width)
		self.longitudal_elements.append(new_element)

	def clear_longitudal_elements(self):
		self.longitudal_elements.clear()
		

	def __init__(self,the_hull):
		self.the_hull=the_hull

		self.curve_objects=[]
		self.curve_backups=[]
		self.longitudal_elements=[]
		self.longitudal_element_objects=[]

		self.longitudal_thickness=the_hull.structural_thickness
		
		self.bool_correction_offset=the_hull.bool_correction_offset

		self.curve_height=the_hull.hull_height
		self.extrude_width=the_hull.hull_height*3

		self.view_collection_chines=bpy_helper.make_collection("chines",bpy.context.scene.collection.children)
		self.view_collection_longitudals=bpy_helper.make_collection("longitudals",bpy.context.scene.collection.children)
		self.view_collection_longitudal_slicers=bpy_helper.make_collection("longitudal_slicers",bpy.context.scene.collection.children)
 
	# After the boolean operation is complete the vertices can be removed that are on the other side
	# of the plane used for the boolean operation. 
	def delete_back_front(self,ob):
		ob.select_set(state=True)

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_set_active(group="back")
		bpy.ops.object.vertex_group_select()
		bpy.ops.mesh.delete(type='VERT')

		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.vertex_group_set_active(group="front")
		bpy.ops.object.vertex_group_select()
		bpy.ops.mesh.delete(type='VERT')

	
	# Creates a new secondary plane that will intersect the primary plane. This new secondary plane will act as the slicer
	# It marks the front and back vertex groups for reference later after boolean operation
	def create_slicer_plane_mesh(self,name,height,longitudal_element,inverted_curves):
		
		bpy_helper.deselect_all_objects()

		theCurveHelper = curve_helper.Curve_Helper()

		#curve_angle=0
		#bend_radius=0

		#if inverted_curves:
		#	curve_angle=longitudal_element.curve_angle
		#	bend_radius=longitudal_element.bend_radius
		#else:
		curve_angle=longitudal_element.curve_angle
		bend_radius=longitudal_element.bend_radius
	
		theCurveHelper.curve_angle=curve_angle

		theCurveHelper.define_curve(self.curve_length,bend_radius)
		theCurveHelper.curve_height=0

		theCurveHelper.generate_curve(name)

		bpy.ops.transform.rotate(value=radians(90),orient_axis='X')
		bpy.ops.object.transform_apply(rotation=True,scale=False,location=False)

		newCurve=theCurveHelper.curve_object

		bpy_helper.select_object(newCurve,True)

		bpy.ops.object.mode_set(mode='EDIT')

		# extrude thicknes along Y axis
		bpy.ops.mesh.select_all(action='SELECT')
		#bpy.ops.mesh.normals_make_consistent(inside=False)
		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,self.curve_width*5,0), 
										"constraint_axis":(False, False,True)})

		
		bpy.ops.mesh.select_all(action='DESELECT')

		bpy.ops.object.mode_set(mode='OBJECT')

		group = newCurve.vertex_groups.new()
		group.name = "back"

		# for some reason vector math type if vert.co.y==0 equals false negative because of some rounding issue so I'm using -1 as cutoff for comparison

		verts = []
		for vert in newCurve.data.vertices:
			#print("%f %f %f"%(vert.co.x,vert.co.y,vert.co.z))
			if vert.co.y>-1:
				verts.append(vert.index)
			
		group.add(verts, 1.0, 'ADD')

		group = bpy.context.object.vertex_groups.new()
		group.name = "front"

		verts = []
		for vert in newCurve.data.vertices:
			if vert.co[1]<-1:
				verts.append(vert.index)

		group.add(verts, 1.0, 'ADD')

		#bpy.ops.transform.rotate(value=radians(90),orient_axis='X')
		#bpy.ops.object.transform_apply(rotation=True,scale=False,location=False)
		
		newCurve.location.z=height

		y_shift=self.curve_width*5/2

		

		#theCurveHelper.extrude_curve(newCurve)
		#bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})

		bpy.ops.object.select_all(action='DESELECT')


		bpy.ops.object.mode_set(mode='EDIT')

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.transform.translate(value=(0, -y_shift, 0))

		bpy.ops.object.mode_set(mode='OBJECT')
		#newCurve.location.y+=y_shift



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
		#bpy.ops.mesh.normals_make_consistent(inside=False)
		bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, amount, 0), 
										"constraint_axis":(False, True, False)})
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')


	# for symmetrical chines - if there is any curve in slicer plane - it needs to be inverted for opposite side (symmetrical)
	def make_slicer_plane(self,wall_curve,name,thickness,longitudal_element,inverted_curves=False):

		name_prefix="cutter"

		# Add first plane
		slicer1=self.create_slicer_plane_mesh(name_prefix+name+".a",longitudal_element.z_offset,longitudal_element,inverted_curves)
		
		slicer1.select_set(True)
		bpy.context.view_layer.objects.active=slicer1
		
		bool_cut = slicer1.modifiers.new(type="BOOLEAN", name=name_prefix)
		bool_cut.object = wall_curve
		bool_cut.operation = 'DIFFERENCE'
		
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier=name_prefix)
		
		self.delete_back_front(slicer1)

		slicer1.select_set(False)
		
		# Add second plane
		slicer2=self.create_slicer_plane_mesh(name_prefix+name+".b",longitudal_element.z_offset-thickness,longitudal_element,inverted_curves)
   
		slicer2.select_set(True)
		
		bpy.context.view_layer.objects.active=slicer2
		
		bool_cut = slicer2.modifiers.new(type="BOOLEAN", name=name_prefix)
		bool_cut.object = wall_curve
		bool_cut.operation = 'DIFFERENCE'

		bpy.context.view_layer.objects.active=slicer2
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier=name_prefix)
   
		self.delete_back_front(slicer2)

		bpy.ops.object.mode_set(mode='OBJECT')

		slicer1.select_set(True)
		slicer2.select_set(True)

		bpy.ops.object.join()
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')

		bpy.ops.mesh.bridge_edge_loops()

		# joining 2 objects sets the origin to the last selected object
		# so shift the object down so origin is at center of object (thickness/2)
		bpy.ops.transform.translate(value=(0, 0, -(thickness/2)))
		
		bpy.ops.object.mode_set(mode='OBJECT')
		#bpy.ops.mesh.select_all(action='DESELECT')

		slicer2.location.z+=thickness

		# second object selected is left over after join
		slicer2.name=name_prefix+name

		#bpy.ops.object.transform_apply(rotation=False,scale=False,location=True)
		return slicer2

	

	def make_longitudal_element(self,curve_object,longitudal_element,inversed,index):
		longitudal_plane=None

		longitudal_name="%s.longitudal.%02d"%(curve_object.name,index)
		slicer_name="%s.slicer.%02d"%(curve_object.name,index)

		#longitudal_z_offset=longitudal_element.z_offset

		#if inversed==False:
		#	longitudal_z_offset=-longitudal_element.z_offset

		longitudal_plane=self.make_slicer_plane(
			wall_curve=curve_object,
			name=longitudal_name,
			longitudal_element=longitudal_element,
			thickness=longitudal_element.thickness,
			#z_offset=longitudal_z_offset,
			inverted_curves=inversed)

		material_helper.assign_material(longitudal_plane,material_helper.get_material_stringer())
		self.the_hull.longitudal_list.append(longitudal_plane)

		extrude_amount=-longitudal_element.width
		slicer_extrude_amount=-longitudal_element.width*longitudal_element.slicer_ratio

		if inversed:
			extrude_amount=longitudal_element.width
			slicer_extrude_amount=longitudal_element.width*longitudal_element.slicer_ratio
					
		self.select_and_extrude_slicer(longitudal_plane,extrude_amount)

		slicer_plane=None
		
		slicer_plane=self.make_slicer_plane(
			wall_curve=curve_object,
			name=slicer_name,
			longitudal_element=longitudal_element,
			thickness=longitudal_element.thickness*longitudal_element.slicer_overcut,
			#z_offset=longitudal_z_offset,
			inverted_curves=inversed)

		
		material_helper.assign_material(slicer_plane,material_helper.get_material_support())
		self.the_hull.longitudal_slicer_list.append(slicer_plane)

		
		self.select_and_extrude_slicer(slicer_plane,slicer_extrude_amount)

#		bpy_helper.select_object(slicer_plane,True)
#		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

		#bpy_helper.select_object(longitudal_plane,True)
		#bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

		slicer_plane.parent=longitudal_plane

		slicer_plane.location.z=0

		longitudal_plane.parent=curve_object
		longitudal_plane.matrix_parent_inverse = curve_object.matrix_world.inverted()

		if inversed:

			if self.curve_width<0:
				slicer_plane.location.y=-self.skin_pokethrough
			else:
				slicer_plane.location.y=self.skin_pokethrough
		
		else:

			if self.curve_width<0:
				slicer_plane.location.y=self.skin_pokethrough
			else:
				slicer_plane.location.y=-self.skin_pokethrough

		
		# for some reason bool doesn't work if X is 0 on parent object... 
		# blender coplanar surface boolean bug
		slicer_plane.location.x=0.0001
		
		#slicer_plane.location.z=- ( (longitudal_element.thickness*longitudal_element.slicer_overcut)-longitudal_element.thickness ) / 2

		bpy_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)
		bpy_helper.hide_object(slicer_plane)
		bpy_helper.move_object_to_collection(self.view_collection_longitudals,longitudal_plane)

		self.longitudal_element_objects.append(longitudal_plane)

		# chop ends off if needed (based on X limits)
		if longitudal_element.limit_x_max!=0 and longitudal_element.limit_x_min!=0:

			#modifier_min_x_name="slice_min_x"
			#modifier_max_x_name="slice_max_x"

			block_width=self.the_hull.hull_length

			adjusted_min_location=longitudal_element.limit_x_min
			adjusted_min_location-=block_width/2

			adjusted_max_location=longitudal_element.limit_x_max
			adjusted_max_location+=block_width/2

			object_end_clean_min = self.the_hull.make_bool_cube("end_clean_x_min"+longitudal_plane.name,location=[adjusted_min_location,0,0],size=(block_width,block_width,self.the_hull.hull_height))
			object_end_clean_max = self.the_hull.make_bool_cube("end_clean_x_max"+longitudal_plane.name,location=[adjusted_max_location,0,0],size=(block_width,block_width,self.the_hull.hull_height))

			print(object_end_clean_max.name)

			bool_new = longitudal_plane.modifiers.new(type="BOOLEAN", name="Lm")
			bool_new.object = object_end_clean_min
			bool_new.operation = 'DIFFERENCE'

			bool_new = longitudal_plane.modifiers.new(type="BOOLEAN", name="Lx")
			bool_new.object = object_end_clean_max
			bool_new.operation = 'DIFFERENCE'

			bool_new = slicer_plane.modifiers.new(type="BOOLEAN", name="Sm")
			bool_new.object = object_end_clean_min
			bool_new.operation = 'DIFFERENCE'

			bool_new = slicer_plane.modifiers.new(type="BOOLEAN", name="Sx")
			bool_new.object = object_end_clean_max
			bool_new.operation = 'DIFFERENCE'


			bpy_helper.select_object(longitudal_plane,True)
			#bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Lm")
			#bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Lx")

			bpy_helper.select_object(slicer_plane,True)
			#bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Sm")
			#bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Sx")

			#bpy.data.objects.remove(object_end_clean_min)
			object_end_clean_max.hide_viewport=True
			#bpy.data.objects.remove(object_end_clean_max)
			object_end_clean_min.hide_viewport=True

	



	def make_single_chine(self,twist=None,inversed=False):

		theCurveHelper = curve_helper.Curve_Helper()

		theCurveHelper.asymmetry=self.asymmetry

		bpy.ops.object.select_all(action='DESELECT')

		name_prefix="chine_"

		curve_name=name_prefix+self.name

		if self.symmetrical:
		   if inversed:
			   curve_name+=".R"
		   else:
			   curve_name+=".L"

		if twist!=None:
			if inversed:
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

		self.curve_objects.append(curve_object)

		material_helper.assign_material(curve_object,material_helper.get_material_bool())
		bpy.ops.transform.translate(value=(self.bool_correction_offset[0], self.bool_correction_offset[1], self.bool_correction_offset[2]))

		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
		theCurveHelper.extrude_curve(self.extrude_width)

		bpy_helper.select_object(curve_object,True)

		if inversed:
			theCurveHelper.rotate_curve([180,0,0])
			bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		

		for i in range(len(self.longitudal_elements)):
			self.make_longitudal_element(curve_object,self.longitudal_elements[i],inversed,i)


		bpy_helper.select_object(curve_object,True)

		if inversed:
			rotation_opposite=[-self.rotation[0],
							self.rotation[1],
							self.rotation[2],
							]

			theCurveHelper.rotate_curve(rotation_opposite)
			
			bpy.ops.transform.translate(value=(self.offset[0], -self.offset[1], self.offset[2]))
		else:    
			theCurveHelper.rotate_curve(self.rotation)
			bpy.ops.transform.translate(value=(self.offset[0], self.offset[1], self.offset[2]))


		#bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

		theCurveHelper.deselect_curve()
		
		theCurveHelper.add_boolean(self.the_hull.hull_object)

		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
		bpy_helper.hide_object(theCurveHelper.curve_object)

		bpy_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_backup)
		bpy_helper.hide_object(theCurveHelper.curve_backup)
		self.curve_backups.append(theCurveHelper.curve_backup)

		bpy_helper.hide_object(curve_object)

		self.the_hull.chine_list.append(curve_object)

		return curve_object




	def make_chine(self,twist=None):

		# ================================================================================================ 
		# First curve is Left Side or non-symmetrical "single side"
		# ================================================================================================
		newcurve=self.make_single_chine(twist,False)
		self.curve_objects.append(newcurve)


		# ================================================================================================ 
		# Second curve is Right Side
		# ================================================================================================
		if self.symmetrical:
			newcurve=self.make_single_chine(twist,True)
			self.curve_objects.append(newcurve)

