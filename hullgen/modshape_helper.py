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

from ..hullgen import curve_helper
from ..hullgen import bpy_helper
from ..hullgen import geometry_helper  
from ..hullgen import window_helper  

class modshape:
	mod_objects=None

	# inert objects are created but do not affect hull (non boolean participating)
	inert_objects=None

	name=None
	rotation=[0,0,0]
	location=[0,0,0]
	deform=[0,0,0]
	size=[1,1,1]
	mod_mode="add"
	mod_type="cube"
	symmetrical=False

	def __init__(self,name,location,rotation,size,mod_mode="add",deform=[0,0,0],mod_shape="trapezoid",symmetrical=False):
		self.name=name
		self.rotation=rotation
		self.location=location
		self.size=size
		self.mod_mode=mod_mode
		self.mod_shape=mod_shape
		self.deform=deform
		self.mod_objects=[]
		self.inert_objects=[]
		self.symmetrical=symmetrical

	def make_window(self,the_hull):

		new_window=window_helper.window()

		new_window.make_window_on_object(obj=the_hull.hull_object,
			position=self.location,
			angle=self.rotation,
			symmetrical=True)

		for obj in new_window.windows:
			self.mod_objects.append(obj)

		for obj in new_window.bolts:
			self.mod_objects.append(obj)


	def make_wallbox(self,the_hull):

#        bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')

		# When viewed from top

		
		# Length


		# < --- Length --- > Length = size.X (no adjustments from input)
		# ================  - Top
		# |              |  - Sides
		# |              |
		# ================  - Bottom

		# Sides = size.Y - material thickness * 2 

		bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=self.location)
		left_side = bpy.context.active_object
		left_side.name="%s_wall_left"%self.name

		bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=self.location)
		right_side = bpy.context.active_object
		right_side.name="%s_wall_right"%self.name

		left_side.select_set(state=True)
		right_side.select_set(state=True)

		bpy.ops.transform.resize(value=[self.size[1]-(the_hull.structural_thickness*2),self.size[2],1])

		geometry_helper.set_rotation_degrees(left_side,[90,0,90])
		geometry_helper.set_rotation_degrees(right_side,[90,0,90])

		bpy.ops.object.select_all(action='DESELECT')
		
		# Make Top and Bottom

		bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=self.location)
		top_side = bpy.context.active_object
		top_side.name="%s_wall_top"%self.name

		bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=self.location)
		bottom_side = bpy.context.active_object
		bottom_side.name="%s_wall_bottom"%self.name
		
		left_side.select_set(state=False)
		right_side.select_set(state=False)

		top_side.select_set(state=True)
		bottom_side.select_set(state=True)
		
		bpy.ops.transform.resize(value=[self.size[0],self.size[2],1])

		geometry_helper.set_rotation_degrees(top_side,[90,0,0])
		geometry_helper.set_rotation_degrees(bottom_side,[90,0,0])
		
		left_side.location.x=left_side.location.x-(self.size[0]/2)
		right_side.location.x=right_side.location.x+(self.size[0]/2)
		
		top_side.location.y=top_side.location.y+(self.size[1]/2)
		bottom_side.location.y=bottom_side.location.y-(self.size[1]/2)
		
		left_side.select_set(state=True)
		right_side.select_set(state=True)
		
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
		
		
		# Make volume cube
		
		bpy.ops.object.select_all(action='DESELECT')
		
		bpy.ops.mesh.primitive_cube_add(size=1.0, 
			enter_editmode=False, 
			location=self.location)
			
		bpy.ops.transform.resize(value=self.size)
		
		bpy.ops.object.transform_apply(scale=True,location=False)
			
		volume_cube = bpy.context.active_object
		volume_cube.name="%s_volume_cube"%self.name

		bool_name="mod_%s"%self.name
		bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name=bool_name)
		bool_new.object = volume_cube
		
		volume_cube.hide_viewport=True
		volume_cube.hide_render=True
		
		# TODO add rotation code for all the objects

		self.mod_objects.append(left_side)
		self.mod_objects.append(right_side)
		self.mod_objects.append(top_side)
		self.mod_objects.append(bottom_side)

		self.mod_objects.append(volume_cube)

		

	def make_trapezoid(self,the_hull):


		mod_object=geometry_helper.make_cube(
			name=self.name,
			size=self.size,
			location=self.location,
			rotation=self.rotation)

		bool_name="mod_%s"%self.name
		bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name=bool_name)
		bool_new.object = mod_object

		if self.deform!=[0,0,0]:

			bpy_helper.select_object(mod_object,True)
			#bpy.ops.object.mode_set(mode='EDIT')
			geometry_helper.select_going_up(mod_object)
			
			bpy.ops.object.mode_set(mode='EDIT')
			
			bpy.ops.transform.translate(value=(self.deform[0], 0, 0))

			bpy.ops.transform.resize(value=(self.deform[1], self.deform[2], 1))

			bpy.ops.object.mode_set(mode='OBJECT')

		if self.mod_mode=="add":
			bool_new.operation = 'UNION'
		else:
			bool_new.operation = 'DIFFERENCE'

		mod_object.hide_render=True
		mod_object.hide_viewport=True

		self.mod_objects.append(mod_object)


	def generate_modshape(self,the_hull):

		if self.mod_shape=="trapezoid":
			self.make_trapezoid(the_hull)
		elif self.mod_shape=="wallbox":
			self.make_wallbox(the_hull)
		elif self.mod_shape=="window_o":
			self.make_window(the_hull)




		

		
