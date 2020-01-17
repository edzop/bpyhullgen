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
import hashlib

from math import radians, degrees
from mathutils import Vector

#from . import (
#		curve_helper,
#		material_helper
#		)

#from . import curve_helper as curve_helper
#from . import material_helper as material_helper

curve_helper = imp.load_source('curve_helper','curve_helper.py')
material_helper = imp.load_source('material_helper','material_helper.py')

def separate_active_by_material():
	selected_object=bpy.context.view_layer.objects.active

	if selected_object==None:
		return

	object_name=selected_object.name

	view_collection_separated=curve_helper.make_collection(object_name,bpy.context.scene.collection.children)

	bpy.ops.mesh.separate(type='MATERIAL')

	for obj in bpy.data.objects:
		if obj.type=="MESH":
			if obj.name.startswith(object_name):
				curve_helper.move_object_to_collection(view_collection_separated,obj)

				if len(obj.data.materials)>0:
					first_material_name=obj.data.materials[0].name
					obj.name="%s_%s"%(object_name,first_material_name)


def solidify_selected_objects():
	for obj in bpy.context.selected_objects:
		if obj.type=="MESH":
			has_solidify_modifier=False

			for modifier in obj.modifiers:
				if modifier.type=='SOLIDIFY':
					has_solidify_modifier=True

			if has_solidify_modifier==False:
				modifier=obj.modifiers.new(name="solidify", type='SOLIDIFY')
				modifier.thickness=-0.1


# Generate unique color RGV values based on input string 
# Returns list of 3 values between 0 and 1
def get_color_from_hash_string(input_string,add_alpha_value=True):
    hash_string=str((hash(input_string) % 10**9))
    m = hashlib.md5()
    m.update(input_string.encode())
    hash_string=m.hexdigest()

    color_value_list=[]
        
    color_value_list.append(int(str(int(hash_string, 16))[0:3])/999)
    color_value_list.append(int(str(int(hash_string, 16))[3:6])/999)
    color_value_list.append(int(str(int(hash_string, 16))[6:9])/999)

    if add_alpha_value==True:
        color_value_list.append(1)
        
    return color_value_list


def make_backdrop():
	bpy.ops.mesh.primitive_plane_add(size=80, enter_editmode=False, location=(0, 0, -2))

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.mode_set(mode='OBJECT')

	ob = bpy.context.active_object
	ob.data.edges[3].select=True
	ob.name="Floor"

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 40)})

	bpy.ops.mesh.select_all(action='DESELECT')

	bpy.ops.object.mode_set(mode='OBJECT')
	ob.data.edges[3].select=True
	bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.bevel(offset=20, offset_pct=0, segments=10, release_confirm=True)

	bpy.ops.object.mode_set(mode='OBJECT')
	bpy.ops.object.shade_smooth()

	mat = material_helper.make_metalic_material("backdrop",[.6,.6,.6,1])
	material_helper.assign_material(ob,mat)

	return ob



def apply_all_bool_modifiers():

	if(bpy.context.active_object.mode!="OBJECT"):
		bpy.ops.object.editmode_toggle()
	
	for obj in bpy.data.objects:
		has_boolean=False
		
		for modifier in obj.modifiers:
			if modifier.type=='BOOLEAN':
				boolean_target_object=modifier.object
				color_value_list=get_color_from_hash_string(boolean_target_object.name)
				new_material_name="slicer_%s"%boolean_target_object.name

				old_hide_viewport=boolean_target_object.hide_viewport

				boolean_target_object.hide_viewport=False

				slicer_material=material_helper.make_subsurf_material(new_material_name,color_value_list)

				obj.data.materials.append(slicer_material)

				# Material index of new material should be last in list
				new_material_index=len(obj.data.materials)-1

				bpy.context.view_layer.objects.active = boolean_target_object

				#if(bpy.context.view_layer.objects.active!="EDIT"):
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

				bpy.context.view_layer.objects.active = obj
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode='OBJECT')

				# restore it to previous visual state (hidden or not hidden)
				boolean_target_object.hide_viewport=old_hide_viewport

				bpy.ops.object.modifier_apply(modifier=modifier.name)

				for f in obj.data.polygons:
					if f.select:
						f.material_index=new_material_index

				has_boolean=True

		if has_boolean:
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.normals_make_consistent(inside=False)
			bpy.ops.object.editmode_toggle()


def mesh_deselect_all():
	old_mode=bpy.context.active_object.mode
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='DESELECT')

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def NormalInDirection( normal, direction, limit = 0.5 ):
	return direction.dot( normal ) > limit

def GoingUp( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (0, 0, 1 ) ), limit )

def GoingDown( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (0, 0, -1 ) ), limit )


def GoingBack( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (-1, 0, 0 ) ), limit )

def GoingFront( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (1, 0, 0 ) ), limit )


def GoingLeft( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (0, 1, 0 ) ), limit )

def GoingRight( normal, limit = 0.5 ):
	return NormalInDirection( normal, Vector( (0, -1, 0 ) ), limit )


def GoingSide( normal, limit = 0.5 ):
	return GoingUp( normal, limit ) == False and GoingDown( normal, limit ) == False

def select_only_going_left(ob):
	old_mode=bpy.context.active_object.mode
	mesh_deselect_all()

	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingLeft( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)
	

def select_only_going_right(ob):
	old_mode=bpy.context.active_object.mode
	mesh_deselect_all()
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingRight( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)

def select_only_going_up(ob):
	old_mode=bpy.context.active_object.mode
	mesh_deselect_all()
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingUp( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def select_only_going_front(ob):
	old_mode=bpy.context.active_object.mode
	mesh_deselect_all()
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingFront( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def delete_non_aligned_faces(ob,func):
	
	bpy.ops.object.select_all(action='DESELECT')
	curve_helper.select_object(ob,True)

	old_mode=bpy.context.active_object.mode

	func(ob)
	#select_only_going_front(ob)

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='INVERT')

	bpy.ops.mesh.delete(type='FACE')
	

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def import_object(path,target_object,location,view_collection=None,rotation=None):
	nob = bpy.ops.wm.link(directory=path,link=True,files=[{'name': target_object}], relative_path=False)
	ob = bpy.context.active_object
	ob.location=location
	if view_collection!=None:
		curve_helper.move_object_to_collection(view_collection,ob)

	if rotation!=None:
		bpy.ops.transform.rotate(value=radians(rotation[0]),orient_axis='X')
		bpy.ops.transform.rotate(value=radians(rotation[1]),orient_axis='Y')
		bpy.ops.transform.rotate(value=radians(rotation[2]),orient_axis='Z')

	return ob

