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

class modshape:
	mod_object=None

	name=None
	rotation=[0,0,0]
	location=[0,0,0]
	deform=[0,0,0]
	size=[1,1,1]
	mod_mode="add"
	mod_type="cube"

	def __init__(self,name,location,rotation,size,mod_mode="add",deform=[0,0,0]):
		self.name=name
		self.rotation=rotation
		self.location=location
		self.size=size
		self.mod_mode=mod_mode
		self.deform=deform

	def generate_modshape(self,the_hull):

		self.mod_object=geometry_helper.make_cube(
			name=self.name,
			size=self.size,
			location=self.location,
			rotation=self.rotation)

		bool_name="mod_%s"%self.name
		bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name=bool_name)
		bool_new.object = self.mod_object

		if self.deform!=[0,0,0]:

			bpy_helper.select_object(self.mod_object,True)
			#bpy.ops.object.mode_set(mode='EDIT')
			geometry_helper.select_going_up(self.mod_object)
			
			bpy.ops.object.mode_set(mode='EDIT')
			
			bpy.ops.transform.translate(value=(self.deform[0], 0, 0))

			bpy.ops.transform.resize(value=(self.deform[1], self.deform[2], 1))

			bpy.ops.object.mode_set(mode='OBJECT')

		if self.mod_mode=="add":
			bool_new.operation = 'UNION'
		else:
			bool_new.operation = 'DIFFERENCE'

		self.mod_object.hide_render=True
		self.mod_object.hide_viewport=True




		

		
