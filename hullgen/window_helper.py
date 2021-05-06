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
from math import radians

from ..hullgen import geometry_helper
from ..hullgen import material_helper
from ..hullgen import curve_helper
from ..bpyutils import bpy_helper


def calc_arc_point_ellipse(centerpoint,angle,distance):
	x= (distance[0]/2) * math.sin(math.radians(angle))
	y= (distance[1]/2) * math.cos(math.radians(angle))

	return (x,y)

def calc_arc_point_circle(centerpoint,angle,distance):
	x= (distance/2) * math.sin(math.radians(angle))
	y= (distance/2) * math.cos(math.radians(angle))

	return (x,y)

def make_circle(name,centerpoint,diameter,circle_depth):
	bpy.ops.mesh.primitive_cylinder_add(radius=diameter, depth=circle_depth, enter_editmode=False, location=centerpoint)
	new_object=bpy.context.view_layer.objects.active
	new_object.name=name
	return new_object


class window:
	bolts=None
	windows=None

	def __init__(self):
		self.bolts=[]
		self.windows=[]



		
	def make_window(self,name="window",centerpoint=(0,0,0),diameter=1,depth=0.4):

		material_bolts=material_helper.get_material_bolts()
		material_window=material_helper.get_material_window()

		view_collection_windows=bpy_helper.make_collection("windows",bpy.context.scene.collection.children)

		ellipse_ratio=2

		window_name="window_%s"%name

		main_circle=make_circle(window_name,centerpoint,diameter,depth)

		self.windows.append(main_circle)

		bpy_helper.move_object_to_collection(view_collection_windows,main_circle)

		material_helper.assign_material(main_circle,material_window)

		bpy.ops.transform.resize(value=(ellipse_ratio, 1, 1), 
			constraint_axis=(True, True, False))

		bpy.ops.object.transform_apply(rotation=False,scale=True,location=False)
		
		bolt_diameter=diameter*0.1

		bolt_margin=diameter*0.4
		
		for a in range(0,360,30):

			arc_point=calc_arc_point_ellipse(centerpoint,a,
				[diameter*2*ellipse_ratio+bolt_margin,diameter*2+bolt_margin]
				)
			bolt_hole=make_circle("bolt",(arc_point[0],arc_point[1],centerpoint[2]),bolt_diameter,depth)
			bolt_hole.parent=main_circle

			self.bolts.append(bolt_hole)

			material_helper.assign_material(bolt_hole,material_bolts)

			bpy_helper.move_object_to_collection(view_collection_windows,bolt_hole)


		return main_circle

	def make_window_on_chine(new_chine,offset_x,offset_z,opposite_side=False):
		
		# disabled temporarily for new curve functionality integration

		curve_L=None
		curve_R=None

		for curve in new_chine.curve_objects:

			if curve.name.endswith(".L"):
				curve_L=curve
			elif curve.name.endswith(".R"):
				curve_R=curve

		window_thickness=0.1
			
		new_window=self.make_window(curve_L.name,(0,0,0),0.18,window_thickness)
		new_window.parent=curve_L

		if opposite_side==True:
			new_window.location.y=new_chine.curve_width+window_thickness
		else:
			new_window.location.y=-new_chine.curve_width #-window_thickness

		new_window.location.z=offset_z
		new_window.location.x=offset_x
		new_window.rotation_euler[0]=radians(90)

		new_window=self.make_window(curve_R.name,(0,0,0),0.18,window_thickness)
		new_window.parent=curve_R

		if opposite_side==True:
			new_window.location.y=-new_chine.curve_width-window_thickness
		else:
			new_window.location.y=new_chine.curve_width #-window_thickness

		new_window.location.z=offset_z
		new_window.location.x=offset_x
		new_window.rotation_euler[0]=radians(90)

	def make_window_on_object(self,obj,position,angle,symmetrical=True):

		window_name_postfix=""

		if symmetrical==True:
			
			name="_%s_L"%obj.name
			new_window=self.make_window(name,(0,0,0),0.18,0.1)
			new_window.parent=obj

			new_window.location.x=position[0]
			new_window.location.y=position[1]
			new_window.location.z=position[2]

			new_window.rotation_euler[0]=radians(-angle[0])
			new_window.rotation_euler[1]=radians(-angle[1])
			new_window.rotation_euler[2]=radians(-angle[2])

			window_name_postfix="_R"

		name="_%s%s"%(obj.name,window_name_postfix)
		new_window=self.make_window(name,(0,0,0),0.18,0.1)
		new_window.parent=obj

		new_window.location.x=position[0]
		new_window.location.y=-position[1]
		new_window.location.z=position[2]

		new_window.rotation_euler[0]=radians(angle[0])
		new_window.rotation_euler[1]=radians(angle[1])
		new_window.rotation_euler[2]=radians(angle[2])

	def cut_windows(self):

		view_collection_windows=bpy_helper.make_collection("windows",bpy.context.scene.collection.children)

		hull_walls=[]

		for o in bpy.data.objects:
			if o.type=="MESH":
				if o.name.startswith("hull_object_slicer"):
					hull_walls.append(o)
					print("window cut: %s"%o.name)

		for hull_wall in hull_walls:
			for window_object in view_collection_windows.objects:
				if geometry_helper.check_intersect(hull_wall,window_object):
					print("%s intersects %s"%(window_object.name,hull_wall.name))

					bool_new = hull_wall.modifiers.new(type="BOOLEAN", name="hull_cut")
					bool_new.object = window_object
					bool_new.operation = 'DIFFERENCE'

					bpy.context.view_layer.objects.active = hull_wall
					bpy.ops.object.modifier_apply(modifier=bool_new.name)

					bpy.context.view_layer.objects.active = window_object
					window_object.select_set(True)
					bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
					window_object.select_set(False)
					window_object.scale=(0.999,0.999,0.999)
