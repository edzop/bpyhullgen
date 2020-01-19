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
from math import radians, degrees
 
curve_helper = imp.load_source('curve_helper','curve_helper.py')
chine_helper = imp.load_source('chine_helper','chine_helper.py')
material_helper = imp.load_source('material_helper','material_helper.py')
geometry_helper = imp.load_source('geometry_helper','geometry_helper.py')
hull_maker = imp.load_source('hull_maker','hull_maker.py')
window_helper = imp.load_source('window_helper','window_helper.py')

the_hull=hull_maker.hull_maker(width=5,length=11,height=3)

the_hull.make_hull_object()

curve_helper.select_object(the_hull.hull_object,False)

new_chine=chine_helper.chine_helper(the_hull)

new_chine.longitudal_thickness=0.05
new_chine.longitudal_width=-0.15
new_chine.curve_width=1.2
new_chine.curve_length=the_hull.hull_length*1.1
new_chine.rotation=[180,0,0]
new_chine.offset=[0,-0.27,-0.5]
new_chine.name="side"
new_chine.longitudal_count=1
new_chine.set_longitudal_curve(0.4,10)
new_chine.longitudal_z_offset=-0.405

#new_chine.curve_twist=[0,25,25]
new_chine.make_chine(twist=[0,0,0])
#new_chine.make_chine()

new_chine.set_longitudal_curve(0,0)
new_chine.curve_length=the_hull.hull_length*1.1
new_chine.curve_width=1.4


new_chine.rotation=[-40,0,0]
new_chine.offset=[0,-0.2,0.45]
new_chine.name="mid"
#new_chine.curve_twist=[0,0,0]
new_chine.longitudal_count=1
new_chine.longitudal_z_offset=-0.7
new_chine.make_chine()
new_chine.longitudal_count=0

new_chine.curve_width=1.1

new_chine.rotation=[36,0,0]
new_chine.offset=[0,0,-0.9]
new_chine.curve_width=1.1
new_chine.name="upper"
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.asymmetry[1]=0
new_chine.make_chine()

window_helper.make_window_on_chine(new_chine,0.5,0.32)
window_helper.make_window_on_chine(new_chine,1.5,0.32)
window_helper.make_window_on_chine(new_chine,-1.5,0.32)

new_chine.rotation=[-75,0,0]
new_chine.offset=[0,0,0.2]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.curve_width=1.6
new_chine.asymmetry[1]=0
new_chine.curve_twist=[0,30,-50]
new_chine.longitudal_count=1
new_chine.longitudal_bend_radius=0.2
new_chine.set_longitudal_curve(0.2,10)
new_chine.longitudal_z_offset=-0.4
new_chine.make_chine()

new_chine.asymmetry[1]=0
new_chine.curve_length=the_hull.hull_length*1.25
new_chine.rotation=[90,1,0]
new_chine.offset=[0,0,-0.51]
new_chine.set_longitudal_curve(0,0)
new_chine.name="roof"
new_chine.curve_width=0.8
new_chine.curve_angle=0
new_chine.symmetrical=False
new_chine.longitudal_count=1
new_chine.longitudal_z_offset=0

# invert for reverse curve
#new_chine.extrude_multiplier=-1
#new_chine.longitudal_width=-new_chine.longitudal_width

new_chine.make_chine()

# ================ modify hull

# ================ Add deck cockpit
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, 0) )

ob = bpy.context.active_object

ob.name="deck_cockpit"

bpy.ops.transform.resize(value=(1,1,2))
bpy.ops.object.transform_apply(scale=True,location=False)
bpy.ops.transform.rotate(value=radians(-22),orient_axis='Y')

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
bool_new.object = ob
bool_new.operation = 'DIFFERENCE'

curve_helper.hide_object(ob)


# ================ Add Pilot House
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1, 0, 0.27) )

bpy.ops.transform.resize(value=(2,0.9,1.5))
bpy.ops.object.transform_apply(scale=True,location=False)


ob = bpy.context.active_object

ob.name="Pilot House"

bpy.ops.object.mode_set(mode='EDIT')

bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

for face in ob.data.polygons:
	face.select = geometry_helper.GoingUp( face.normal )

bpy.ops.object.mode_set(mode='EDIT')

bpy.ops.transform.resize(value=(1, 0.6, 1))

bpy.ops.transform.translate(value=(-0.3, 0, 0))

bpy.ops.mesh.bevel(offset=0.1,segments=4)

bpy.ops.object.mode_set(mode='OBJECT')

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
bool_new.object = ob
bool_new.operation = 'UNION'

window_helper.make_window_on_object(ob,(-0.5,0.31,0.35),90-8)

curve_helper.hide_object(ob)



def add_extras():
	# ================ Add Rudder
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.6, 0, -0.75) )

	rudder_object = bpy.context.active_object

	rudder_object.name="Rudder"

	bpy.ops.transform.resize(value=(0.7,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = rudder_object
	bool_new.operation = 'UNION'

	curve_helper.hide_object(rudder_object)

	# ================ Add Keel
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1, 0, -0.75) )

	ob = bpy.context.active_object

	ob.name="Keel"

	bpy.ops.transform.resize(value=(5.6,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	curve_helper.hide_object(ob)

def offline():

	# ================ Add deck cockpit
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.2, 0, 0) )

	ob = bpy.context.active_object

	ob.name="deck_cockpit"

	bpy.ops.transform.resize(value=(3,1,1))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
	bool_new.object = ob
	bool_new.operation = 'DIFFERENCE'

	curve_helper.hide_object(ob)

# =======================================================

add_extras()

def add_props():

	view_collection_props=curve_helper.make_collection("props",bpy.context.scene.collection.children)

	import_library_path="assets/actors.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(1.3,0,-0.6),view_collection_props,rotation=(0,0,0))
	ob = geometry_helper.import_object(import_library_path,"man.stand",(0.2,0,-0.95),view_collection_props,rotation=(0,0,0))

	import_library_path="assets/boat_assets.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(0.6,0,-1.3),view_collection_props,rotation=(0,0,0))
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(-.6,0,-1.3),view_collection_props,rotation=(0,0,0))

	ob = geometry_helper.import_object(import_library_path,"propshaft",(-4.05,0,-0.97),view_collection_props,rotation=(0,93,0))


add_props()

clean_distance=0.5
x_locations=[	-the_hull.hull_length/2+clean_distance,
				the_hull.hull_length/2-clean_distance]

rotations=[-22,0]

the_hull.cleanup_longitudal_ends(x_locations,rotations)

the_hull.cleanup_center(clean_location=[0.5,0,0],clean_size=[2.8,1,1])


levels=[ -0.9,-0.5 ]

bulkhead_definitions = [ 
	
						(0,levels[0],False),
						(1,levels[0],False),
						(-1,levels[0],False),
						(-2,levels[0],False),
						(2,levels[0],False),

						(3,levels[1],False),
						(-3,levels[1],False),
						(4,levels[1],True),
						(-4,levels[1],True),

						(5,False,False),
					#	(-5,False,False)
]


the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()
