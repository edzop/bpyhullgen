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

from ..hullgen import bpy_helper

def cleanup_shape(ob):
	if bpy.context.active_object.mode=="OBJECT":
		bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

	bpy.ops.mesh.tris_convert_to_quads(seam=False, sharp=False, materials=True)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	
	bpy.ops.object.mode_set(mode='OBJECT')


def make_rounded(ob,width):

	bpy.context.view_layer.objects.active=ob

	if bpy.context.active_object.mode=="OBJECT":
		bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.editmode_toggle()

	bevel = ob.modifiers.new(type="BEVEL",name="bevel")
	bevel.width = width
	bevel.segments = 2
	bevel.limit_method="ANGLE"
	
	bpy.ops.object.modifier_add(type='SUBSURF')

	bpy.ops.object.mode_set(mode='OBJECT')



class Curve_Helper:

	coordinates = []

	curve_length=5
	curve_width=1.5
	curve_resolution=5
	curve_height=1
	curvedata=None
	curve_object=None
	curve_angle=35

	make_backup=False

	curve_backup=None

	asymmetry=[0,0]

	curve_twist=[ 0,0,0 ]

	def __init__(self,curve_resolution=5):
		curvedata=None
		curve_object=None
		self.curve_resolution=curve_resolution

	def define_curve(self,length,width):

		self.coordinates.clear()

		self.curve_length=length
		self.curve_width=width

		handle_width=self.curve_length/6
		half_length=self.curve_length/2
		angle=radians(self.curve_angle)

		# Curve handle = point, handle_left of point, handle right of point

		# Left handle
		asymetric_width=-(self.asymmetry[0]*self.curve_width)
		x=handle_width*math.cos(radians(self.curve_angle*(1-self.asymmetry[0])))
		y=handle_width*math.sin(radians(self.curve_angle*(1-self.asymmetry[0])))

		self.coordinates.append([	(-half_length, asymetric_width, 0), 	
									(-half_length-x, asymetric_width+y, 0),	
									(-half_length+x, asymetric_width-y, 0)
								])

		# Center handle
		self.coordinates.append([	
										(0,-self.curve_width, 0),
										(-handle_width, -self.curve_width, 0),  
										(handle_width,-self.curve_width, 0)
								]) 


		asymetric_width=-(self.asymmetry[1]*self.curve_width)
		x=handle_width*math.cos(radians(self.curve_angle*(1-self.asymmetry[1])))
		y=handle_width*math.sin(radians(self.curve_angle*(1-self.asymmetry[1])))

		# Right handle
		self.coordinates.append([	
									(half_length, asymetric_width, 0),  
									(half_length-x, asymetric_width-y, 0),
									(half_length+x, asymetric_width+y, 0)
								])

	# generates the basic curve
	def generate_curve(self,curvename):

		# delete it if it already exists
		bpy_helper.find_and_remove_object_by_name(curvename)
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
		
		if self.make_backup:
			bpy_helper.select_object(self.curve_object,True)
			bpy.ops.object.duplicate_move()
			self.curve_backup=bpy.context.active_object
			self.curve_backup.name=self.curve_object.name+"_backup"
			self.curve_backup.parent=self.curve_object

		bpy_helper.select_object(self.curve_object,True)
		bpy.ops.object.convert(target='MESH', keep_original=False)
		bpy.ops.object.shade_flat()
		

	def extrude_curve(self,extrude_width):

		bpy.ops.object.select_all(action='DESELECT')

		self.curve_object.display_type="WIRE"
		
		bpy_helper.select_object(self.curve_object,True)
	
		bpy.ops.object.mode_set(mode='EDIT')
			
		bpy.ops.mesh.select_all(action='SELECT')

#		print("%d %d"%(self.curve_width,extrude_width))
		
		bpy.ops.mesh.extrude_region_move( 
			TRANSFORM_OT_translate={"value":(0,-self.curve_width*extrude_width,0)})

		bpy.ops.transform.resize(value=(1, 0, 1),
			constraint_axis=(True, False, False))

		bpy.ops.mesh.select_all(action='SELECT')
		bpy.ops.mesh.normals_make_consistent(inside=False)

		bpy.ops.mesh.select_all(action='DESELECT')

		bpy.ops.object.mode_set(mode='OBJECT')


	def move_curve(self,space):
		#bpy.ops.transform.translate(value=(0, 0, 0.5))
		bpy.ops.transform.translate(value=space)


