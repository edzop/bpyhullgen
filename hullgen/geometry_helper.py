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
import hashlib
from math import radians, degrees
from mathutils import Vector, Matrix
import bmesh
from mathutils.bvhtree import BVHTree

from ..hullgen import curve_helper
from ..hullgen import material_helper
from ..hullgen import measure_helper
from ..bpyutils import bpy_helper

def separate_active_by_material():
	selected_object=bpy.context.view_layer.objects.active

	if selected_object==None:
		return

	object_name=selected_object.name

	view_collection_separated=bpy_helper.make_collection(object_name,bpy.context.scene.collection.children)

	bpy.ops.mesh.separate(type='MATERIAL')

	for obj in bpy.data.objects:
		if obj.type=="MESH":
			if obj.name.startswith(object_name):
				bpy_helper.move_object_to_collection(view_collection_separated,obj)

				if len(obj.data.materials)>0:
					first_material_name=obj.data.materials[0].name
					obj.name="%s_%s"%(object_name,first_material_name)


def solidify_selected_objects(thickness=-0.003):
	for obj in bpy.context.selected_objects:
		if obj.type=="MESH":
			has_solidify_modifier=False

			for modifier in obj.modifiers:
				if modifier.type=='SOLIDIFY':
					has_solidify_modifier=True

			if has_solidify_modifier==False:
				modifier=obj.modifiers.new(name="solidify", type='SOLIDIFY')
				modifier.thickness=thickness

				bpy.context.view_layer.objects.active = obj
				bpy.ops.object.modifier_apply(modifier=modifier.name)


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
	bpy.ops.mesh.select_mode(type="EDGE")
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

def add_info_text(info_text):
	bpy.ops.object.text_add(enter_editmode=False, location=(0, 0, 0))
	new_txt=bpy.context.view_layer.objects.active
	new_txt.data.body=info_text
	new_txt.data.size=0.7
	new_txt.data.extrude=0.01
	new_txt.data.text_boxes[0].width = 11
	new_txt.location.x=-5.5
	new_txt.location.y=-3
	new_txt.location.z=-1
	return new_txt

def set_rotation_degrees(ob,degrees):
	ob.rotation_euler.x=radians(degrees[0])
	ob.rotation_euler.y=radians(degrees[1])
	ob.rotation_euler.z=radians(degrees[2])

def cleanup():

	hidden_objects=[]

	# unhide all objects
	for obj in bpy.data.objects:
		if obj.hide_viewport==True:
			obj.hide_viewport=False
			hidden_objects.append(obj)

	for obj in bpy.data.objects:
		if obj.type=="MESH":
			bpy_helper.select_object(obj,True)
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.delete_loose()
			bpy.ops.mesh.normals_make_consistent(inside=False)
			bpy.ops.object.mode_set(mode='OBJECT')
	
	# rehide previously hidden objects
	for obj in hidden_objects:
		obj.hide_viewport=True

	


def apply_object_bools(obj):
	bpy_helper.select_object(obj,True)

	for modifier in obj.modifiers:
		if modifier.type=='BOOLEAN':
			#print("%s Apply: %s - %s"%(obj.name,modifier.name,modifier.object.name))
			bpy.ops.object.modifier_apply(modifier=modifier.name)


def apply_all_bool_modifiers():

	# faster implementation maybe in future instead of bpy.ops operations?
	#mesh = your_object.to_mesh(scene = bpy.context.scene, apply_modifiers = True, settings = 'PREVIEW')

	if bpy.context.active_object!=None:
		if bpy.context.active_object.mode!="OBJECT":
			bpy.ops.object.mode_set(mode='OBJECT')

	

	hidden_objects=[]

	# unhide all objects
	for obj in bpy.data.objects:
		if obj.hide_viewport==True:
			obj.hide_viewport=False
			hidden_objects.append(obj)


	for obj in bpy.data.objects:
		if obj.type=="MESH":
			has_boolean=False
			
			for modifier in obj.modifiers:
				if modifier.type=='BOOLEAN':
					boolean_target_object=modifier.object
					if boolean_target_object!=None:
						color_value_list=get_color_from_hash_string(boolean_target_object.name)
						new_material_name="slicer_%s"%boolean_target_object.name

						slicer_material=None

						if new_material_name in bpy.data.materials:
							slicer_material=bpy.data.materials[new_material_name]
						else:
							slicer_material=material_helper.make_subsurf_material(new_material_name,color_value_list)

						obj.data.materials.append(slicer_material)

						# Material index of new material should be last in list
						new_material_index=len(obj.data.materials)-1

						bpy.context.view_layer.objects.active = boolean_target_object

						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.select_mode(type="FACE")
						bpy.ops.mesh.select_all(action='SELECT')
						bpy.ops.object.mode_set(mode='OBJECT')

						# select all faces for material assignment to occur
						#for face in obj.data.polygons:
						#	face.select=True

						bpy.context.view_layer.objects.active = obj
						
						print("Applying object: %s"%obj.name)

						bpy.ops.object.mode_set(mode='EDIT')
						bpy.ops.mesh.select_mode(type="FACE")
						bpy.ops.mesh.select_all(action='DESELECT')
						bpy.ops.object.mode_set(mode='OBJECT')

						#for face in obj.data.polygons:
						#	face.select=False

						bpy.ops.object.modifier_apply(modifier=modifier.name)

						for f in obj.data.polygons:
							if f.select:
								f.material_index=new_material_index

						has_boolean=True

	# rehide previously hidden objects
	for obj in hidden_objects:
		obj.hide_viewport=True

	print("Finished!")


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

def select_going_left(ob):
	old_mode=bpy.context.active_object.mode

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='DESELECT')

	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingLeft( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)
	

def select_going_right(ob):
	old_mode=bpy.context.active_object.mode

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='DESELECT')
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingRight( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)

def select_going_up(ob):
	old_mode=bpy.context.active_object.mode

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='DESELECT')

	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingUp( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def select_going_front(ob):
	old_mode=bpy.context.active_object.mode

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='DESELECT')
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingFront( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)

def select_going_back(ob):
	old_mode=bpy.context.active_object.mode

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='DESELECT')
	
	bpy.ops.object.mode_set(mode='OBJECT')
	for face in ob.data.polygons:
		face.select = GoingBack( face.normal)

	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def delete_non_aligned_faces(ob,func):

	old_mode=bpy.context.active_object.mode
	
	#bpy.ops.object.select_all(action='DESELECT')
	bpy_helper.select_object(ob,True)

	
	func(ob)

	bpy.ops.object.mode_set(mode='EDIT')
	#bpy.ops.mesh.select_mode(type="FACE")
	bpy.ops.mesh.select_all(action='INVERT')

	bpy.ops.mesh.delete(type='FACE')
	
	if bpy.context.active_object.mode!=old_mode:
		bpy.ops.object.mode_set(mode=old_mode)


def import_object(path,target_object,location,view_collection=None,rotation=None,parent=None):
	nob = bpy.ops.wm.link(directory=path,link=True,files=[{'name': target_object}], relative_path=False)
	ob = bpy.context.active_object
	ob.location=location
	if view_collection!=None:
		bpy_helper.move_object_to_collection(view_collection,ob)

	if rotation!=None:
		geometry_helper.set_rotation_degrees(ob,rotation)

	if parent!=None:
		ob.parent=parent

	return ob



def check_intersect(the_object,the_other_object):

	BMESH_1 = bmesh.new()
	BMESH_1.from_mesh(bpy.context.scene.objects[the_object.name].data)
	BMESH_1.transform(the_object.matrix_world)
	BVHtree_1 = BVHTree.FromBMesh(BMESH_1)

	BMESH_2 = bmesh.new()
	BMESH_2.from_mesh(bpy.context.scene.objects[the_other_object.name].data)
	BMESH_2.transform(the_other_object.matrix_world)
	BVHtree_2 = BVHTree.FromBMesh(BMESH_2)

	inter = BVHtree_1.overlap(BVHtree_2)

	touching=False

	if inter != []:
		#print(the_object.name + " and " + the_other_object.name + " are touching!")
		touching=True
	#else:
		#print(the_object.name + " and " + the_other_object.name + " NOT touching!")  
	
	return touching
		
	#print(inter)

def inside_shrink(amount=0.1):

	context = bpy.context

	ob = context.object
	me = ob.data
	bm = bmesh.from_edit_mesh(me)


	for f in bm.faces:
		
		forwardback=GoingBack(f.normal) or GoingFront(f.normal)
		print("%s %d"%(f.normal,forwardback))
		if forwardback==False:
			bmesh.ops.translate(bm,
					verts=f.verts,
					vec=-0.025 * f.normal)


	#verts = set(v for f in bm.faces if f.select for v in f.verts)
	#for v in verts:
#		norms  = [f.normal for f in v.link_faces if f.select]
		
#		n = sum(norms, Vector()) / len(norms)
#		v.co += -0.1 * n

	bmesh.update_edit_mesh(me)


def inside_shrink_OLD(amount=0.1):
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.mesh.select_mode(type="FACE")
	ob=bpy.context.view_layer.objects.active

	face_indexes=[]

	polygoncount=len(ob.data.polygons)
	print("Poly count %d"%polygoncount)

	bpy.ops.object.mode_set(mode='OBJECT')

	for i in range(0,polygoncount):
		face=ob.data.polygons[i]
		if GoingBack(face.normal) or GoingFront( face.normal):
			print("not added: %d %s"%(i,str(face.normal)))
		else:
			face_indexes.append(i)
			print("added: %d %s"%(i,str(face.normal)))

	print("Face Indexes: %s"%face_indexes)


	


	for i in face_indexes:
		face=ob.data.polygons[i]
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')
		bpy.ops.object.mode_set(mode='OBJECT')
		face=ob.data.polygons[i]
		face.select=True
		bpy.ops.object.mode_set(mode='EDIT')
		face_normal=face.normal
	
		matrix=((0, -1, 0), (face_normal[2], 0, -face_normal[0]), (face_normal[0], 0, face_normal[2]))

		print("Identitymatrix: %s"%str(matrix))

		bpy.ops.transform.translate(value=(0, 0, -amount),
			orient_type='NORMAL', 
			orient_matrix=matrix, 
			orient_matrix_type='NORMAL',
			constraint_axis=(False, False, True))



# doesn't seem to work if executed from command line
def collapse_outliner_hiearchy():
	context = bpy.context
	screen = context.screen
	collection = context.collection
	#collection = bpy.data.collections["scene"]
	view_layer = context.view_layer

	outliners = [a for a in screen.areas if a.type == 'OUTLINER']
	c = context.copy()

	c["collection"] = collection
	for ol in outliners:
		c["area"] = ol

		bpy.ops.outliner.show_one_level(c, open=False)
		ol.tag_redraw()


def create_bilgetank(the_hull,top,x1,x2,y_offset,name):

	length=x2-x1
	width=the_hull.hull_width/2
	height=the_hull.hull_height/2

	centerY=0

	if y_offset>0:
		centerY=y_offset+(width/2)
	else:
		centerY=y_offset-(width/2)

	centerX=x1+(length/2)
	centerZ=top-height/2

	bpy.ops.mesh.primitive_cube_add(size=1, 
		enter_editmode=False, 
		location=(centerX, centerY, centerZ) 
	)

	bilgetank_object=bpy.context.view_layer.objects.active
	bilgetank_object.name=name

	bpy.ops.transform.resize(value=[length,width,height])
	bpy.ops.object.transform_apply(scale=True,location=False)

	modifier=bilgetank_object.modifiers.new(name="bilge_hull", type='BOOLEAN')
	modifier.object=the_hull.hull_object
	modifier.operation="INTERSECT"
	modifier.double_threshold=0

	bpy.ops.object.modifier_apply(modifier="bilge_hull")
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.object.mode_set(mode='OBJECT')

	#volume in m3
	volume=measure_helper.measure_object_volume(bilgetank_object)

	liters=volume*1000

	# convert liters to gallons
	gallons=liters*0.264172

	dieselweight=liters*0.832

	# diesel density about 0.832kg/litre

	print("Tank: '%s' Volume: %0.04fm3 Liters: %0.01f Gallons: %0.01f (Diesel %0.01fkg) "%(name,volume,liters,gallons,dieselweight))

	material_helper.assign_material(bilgetank_object,material_helper.get_material_fueltank())

	measure_helper.assign_weight(bilgetank_object,dieselweight)

	bilgetank_object.parent=the_hull.hull_object

	return bilgetank_object


def make_cube(name,location=[0,0,0],size=[1,1,1],rotation=[0,0,0]):

	bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=location)

	new_object=bpy.context.view_layer.objects.active

	bpy.ops.transform.resize(value=size)
	bpy.ops.object.transform_apply(scale=True,location=False)

	if rotation!=[0,0,0]:
		new_object.rotation_euler.x=radians(rotation[0])
		new_object.rotation_euler.y=radians(rotation[1])
		new_object.rotation_euler.z=radians(rotation[2])

	new_object.name=name

	return new_object	

def find_object_by_name(name):
	ob = bpy.data.objects.get(name)
	return ob