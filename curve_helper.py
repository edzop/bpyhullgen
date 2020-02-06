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
from mathutils import Vector 
import math

from math import radians, degrees


def cleanup_shape(ob):
	if(bpy.context.active_object.mode=="OBJECT"):
		bpy.ops.object.editmode_toggle()

	bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
	#bpy.ops.mesh._convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
	bpy.ops.mesh.tris_convert_to_quads(seam=False, sharp=False, materials=True)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	
	bpy.ops.object.editmode_toggle()


def make_rounded(ob,width):

	bpy.context.view_layer.objects.active=ob

	if(bpy.context.active_object.mode=="OBJECT"):
		bpy.ops.object.editmode_toggle()

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.editmode_toggle()

	bevel = ob.modifiers.new(type="BEVEL",name="bevel")
	bevel.width = width
	bevel.segments = 2
	bevel.limit_method="ANGLE"
	
	bpy.ops.object.modifier_add(type='SUBSURF')

# works on object or collection
def hide_object(ob):
	ob.hide_viewport = True
	ob.hide_render = True


def make_collection(collection_name, parent_collection):
	if collection_name in bpy.data.collections:
		return bpy.data.collections[collection_name]
	else:
		new_collection = bpy.data.collections.new(collection_name)
		bpy.context.scene.collection.children.link(new_collection)
		return new_collection

def find_collection(context, item):
	collections = item.users_collection
	if len(collections) > 0:
		return collections[0]
	return context.scene.collection

def is_object_hidden_from_view(the_object):
	if the_object.hide_viewport==True:
		return True

	C_collection = find_collection(bpy, the_object)
	if C_collection.hide_viewport==True:
		return True

	return False

def move_object_to_collection(new_collection,the_object):

	C_collection = find_collection(bpy, the_object)
	C_collection.objects.unlink(the_object)
	#print(the_object)
	#print(C_collection)

	new_collection.objects.link(the_object)


def find_and_remove_object_by_name(objname):
	for obj in bpy.data.objects:
	#	print(obj.name)
		if(obj.name==objname):
	#		print("found")
	#        bpy.context.scene.collection.objects.unlink(obj)
			bpy.data.objects.remove(obj)

def select_object(theObject,selected):
	if selected==True:
		bpy.context.view_layer.objects.active = theObject
		theObject.select_set(state=True)
	else:
		bpy.context.view_layer.objects.active = None
		theObject.select_set(state=False)

def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step
		

class Curve_Helper:

	coordinates = []

	#	((0, -1, 0), (0, -1.5, 0), (0, -0.5, 0)),
	#	((-1, 0, 0), (-1, -0.5, 0), (-1, 0.5, 0)),   
	#	((0, 1, 0), (0, 0.5, 0), (0, 1.5, 0)),
	#]

	curve_length=5
	curve_width=1.5
	curve_resolution=64
	curve_height=1
	curvedata=None
	curve_object=None
	curve_angle=35

	#extrude_multiplier=1

	asymmetry=[0,0]

	curve_twist=[ 0,0,0 ]

	def __init__(self):
		curvedata=None
		curve_object=None

	def deselect_curve(self):
		self.curve_object.select_set(state=False)


	def define_curve(self,length,width):

		self.coordinates.clear()

		self.curve_length=length
		self.curve_width=width

		handle_width=self.curve_length/6
		half_length=self.curve_length/2
		angle=radians(self.curve_angle)

		x=handle_width*math.cos(angle)
		y=handle_width*math.sin(angle)

		# Curve handle = point, handle_left of point, handle right of point

		# Left handle
		# TODO - variable assymetry ratio
		if self.asymmetry[0]==0:
			self.coordinates.append([(-half_length, 0, 0), (-half_length-x, y, 0),(-half_length+x, -y, 0)])
		else:
			self.coordinates.append([(-half_length, -self.curve_width, 0), (-half_length-handle_width, -self.curve_width, 0),(-half_length+handle_width, -self.curve_width, 0)])

		# Center handle
		self.coordinates.append([(0,-self.curve_width, 0),(-handle_width, -self.curve_width, 0),  (handle_width,-self.curve_width, 0)]) 

		# Right handle
		# TODO - variable assymetry ratio
		if self.asymmetry[1]==0:
			self.coordinates.append([(half_length, 0, 0),  (half_length-x, -y, 0),(half_length+x, y, 0)])
		else:
			self.coordinates.append([(half_length, -self.curve_width, 0),  (half_length-handle_width, -self.curve_width, 0),(half_length+handle_width, -self.curve_width, 0)])



		#print(self.coordinates)

	# generates the basic curve
	def generate_curve(self,curvename):

		# delete it if it already exists
		find_and_remove_object_by_name(curvename)
		origin=(0,0,0)
  
		self.curvedata = bpy.data.curves.new(name=curvename, type='CURVE')

		has_twist=False

		for t in self.curve_twist:
			if t!=0:
				has_twist=True

		if has_twist==True: 
			self.curvedata.dimensions = '3D'
		else:
			self.curvedata.dimensions = '2D'

		self.curvedata.resolution_u=self.curve_resolution  
		self.curvedata.extrude=self.curve_height
		
		self.curve_object = bpy.data.objects.new(curvename, self.curvedata)    
		self.curve_object.location = origin
		
		bpy.context.scene.collection.objects.link(self.curve_object)    
		
		polyline = self.curvedata.splines.new('BEZIER')    
		polyline.bezier_points.add(len(self.coordinates)-1)
		polyline.resolution_u=self.curve_resolution

		for idx, (knot, h1, h2) in enumerate(self.coordinates):
			point = polyline.bezier_points[idx]
			point.co = knot
			point.handle_left = h1
			point.handle_right = h2
			point.handle_left_type = 'FREE'
			point.handle_right_type = 'FREE'
			
			if has_twist:
				point.tilt=math.radians(self.curve_twist[idx])		

		polyline.use_cyclic_u = False

		select_object(self.curve_object,True)

		

		bpy.ops.object.convert(target='MESH', keep_original=False)
		bpy.ops.object.shade_flat()
		

	def add_boolean(self,hull_object):
		select_object(hull_object,True)

		slicename="slice.%s"%self.curve_object.name

		bool_new = hull_object.modifiers.new(type="BOOLEAN", name=slicename)
		bool_new.object = self.curve_object
		bool_new.operation = 'DIFFERENCE'

		select_object(hull_object,False)

	def extrude_curve(self,extrude_width):

		self.curve_object.display_type="WIRE"

		select_object(self.curve_object,True)
	
		bpy.ops.object.mode_set(mode='EDIT')
			
		bpy.ops.mesh.select_all(action='SELECT')

#		print("%d %d"%(self.curve_width,extrude_width))
		
		bpy.ops.mesh.extrude_region_move( 
			TRANSFORM_OT_translate={"value":(0,-self.curve_width*extrude_width,0)})

		bpy.ops.transform.resize(value=(1, 0, 1),
			constraint_axis=(True, False, False))

		bpy.ops.mesh.select_all(action='DESELECT')

		bpy.ops.object.mode_set(mode='OBJECT')


	def move_curve(self,space):
		#bpy.ops.transform.translate(value=(0, 0, 0.5))
		bpy.ops.transform.translate(value=space)

	def rotate_curve(self,rotation,flip_z=False):
		bpy.ops.transform.rotate(value=radians(rotation[0]),orient_axis='X')
		bpy.ops.transform.rotate(value=radians(rotation[1]),orient_axis='Y')

		if flip_z==True:
			bpy.ops.transform.rotate(value=radians(-rotation[2]),orient_axis='Z')
		else:
			bpy.ops.transform.rotate(value=radians(rotation[2]),orient_axis='Z')
