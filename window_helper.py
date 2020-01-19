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

import imp

import math
from math import radians

material_helper = imp.load_source('material_helper','material_helper.py')
curve_helper = imp.load_source('curve_helper','curve_helper.py')

material_bolts=material_helper.get_material_bolts()
material_window=material_helper.get_material_window()


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

	
def make_window(name="window",centerpoint=(0,0,0),diameter=1,depth=0.4):

	view_collection_windows=curve_helper.make_collection("windows",bpy.context.scene.collection.children)

	ellipse_ratio=2

	window_name="window_%s"%name

	main_circle=make_circle(window_name,centerpoint,diameter,depth)

	curve_helper.move_object_to_collection(view_collection_windows,main_circle)

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

		material_helper.assign_material(bolt_hole,material_bolts)

		curve_helper.move_object_to_collection(view_collection_windows,bolt_hole)


	return main_circle

def make_window_on_chine(new_chine,offset_x,offset_z):
	
	curve_upper_L=new_chine.curve_object_1
	curve_upper_R=new_chine.curve_object_2

	new_window=make_window(curve_upper_L.name,(0,0,0),0.18,0.1)
	new_window.parent=curve_upper_L
	new_window.location.y=-new_chine.curve_width
	new_window.location.z=offset_z
	new_window.location.x=offset_x
	new_window.rotation_euler[0]=radians(90)

	new_window=make_window(curve_upper_R.name,(0,0,0),0.18,0.1)
	new_window.parent=curve_upper_R
	new_window.location.y=-new_chine.curve_width
	new_window.location.z=-offset_z
	new_window.location.x=offset_x
	new_window.rotation_euler[0]=radians(90)



def make_window_on_object(obj,position,angle):
	
	name="%s_L"%obj.name
	new_window=make_window(name,(0,0,0),0.18,0.1)
	new_window.parent=obj

	new_window.location.x=position[0]
	new_window.location.y=position[1]
	new_window.location.z=position[2]

	new_window.rotation_euler[0]=radians(-angle)

	name="%s_R"%obj.name
	new_window=make_window(name,(0,0,0),0.18,0.1)
	new_window.parent=obj

	new_window.location.x=position[0]
	new_window.location.y=-position[1]
	new_window.location.z=position[2]

	new_window.rotation_euler[0]=radians(angle)

