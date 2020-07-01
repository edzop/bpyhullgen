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
  
from math import radians, degrees
 
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import window_helper
from bpyhullgen.hullgen import render_helper

from bpyhullgen.hullgen import keel

the_hull=hull_maker.hull_maker(width=5,length=11,height=3)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

#new_chine.longitudal_thickness=0.05
new_chine.longitudal_width=-0.15
new_chine.curve_width=1.2
new_chine.curve_length=the_hull.hull_length*1.1
new_chine.rotation=[180,0,0]
new_chine.offset=[0,-0.27,-0.5]
new_chine.name="side"
new_longitudal=chine_helper.longitudal_element(z_offset=-0.46,width=-0.2,thickness=0.1)
new_longitudal.set_curve(radius=-0.4,angle=-10)
new_chine.add_longitudal_element(new_longitudal)




#new_chine.curve_twist=[0,25,25]
new_chine.make_chine(twist=[0,0,0])
new_chine.clear_longitudal_elements()
#new_chine.make_chine()

#new_chine.set_longitudal_curve(0,0)

new_chine.curve_length=the_hull.hull_length*1.1
new_chine.curve_width=1.4


new_chine.rotation=[40,0,0]
new_chine.offset=[0,-0.2,0.45]
new_chine.name="mid"
#new_chine.curve_twist=[0,0,0]
new_chine.add_longitudal_element(chine_helper.longitudal_element(z_offset=-0.83,width=-0.2,thickness=0.1))
new_chine.longitudal_z_offset=-0.7

new_chine.make_chine()
new_chine.clear_longitudal_elements()

new_chine.curve_width=1.1

new_chine.rotation=[-36,0,0]
new_chine.offset=[0,0,-0.9]
new_chine.curve_width=1.1
new_chine.name="upper"
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.asymmetry[1]=0
new_chine.make_chine()

window_helper.make_window_on_chine(new_chine,0.5,0.34)
window_helper.make_window_on_chine(new_chine,1.5,0.34)
window_helper.make_window_on_chine(new_chine,-1.5,0.34)

new_chine.rotation=[75,0,0]
new_chine.offset=[0,0,0.2]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.curve_width=1.6
new_chine.asymmetry[1]=0
new_chine.curve_twist=[0,30,-50]

#new_chine.longitudal_count=0
#new_chine.longitudal_bend_radius=0.2
#new_chine.set_longitudal_curve(0.2,10)
#new_chine.longitudal_z_offset=-0.4
new_chine.make_chine()

new_chine.asymmetry[1]=0
new_chine.curve_length=the_hull.hull_length*1.25
new_chine.rotation=[-90,1,0]
new_chine.offset=[0,0,-0.51]

new_chine.name="roof"
new_chine.curve_width=0.8
new_chine.curve_angle=0
new_chine.symmetrical=False

#new_chine.set_longitudal_curve(0,0)
new_chine.add_longitudal_element(chine_helper.longitudal_element(z_offset=0,width=-0.2,thickness=0.1))


# invert for reverse curve
#new_chine.extrude_multiplier=-1
#new_chine.longitudal_width=-new_chine.longitudal_width

new_chine.make_chine()

# ================ modify hull

# ================ Add deck cockpit
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, 0) )

ob = bpy.context.active_object

ob.name="deck_cockpit"

tail_cut_angle=22

bpy.ops.transform.resize(value=(1,1,2))
bpy.ops.object.transform_apply(scale=True,location=False)
bpy.ops.transform.rotate(value=radians(tail_cut_angle),orient_axis='Y')

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
bool_new.object = ob
bool_new.operation = 'DIFFERENCE'

curve_helper.hide_object(ob)


def add_pilot_house():
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

add_pilot_house()

def add_extras():
	# ================ Add Rudder
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.6, 0, -1.05) )

	rudder_object = bpy.context.active_object

	rudder_object.name="Rudder"

	bpy.ops.transform.resize(value=(0.7,0.10,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = rudder_object
	bool_new.operation = 'UNION'

	curve_helper.hide_object(rudder_object)

	# ================ Add Keel
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.9, 0, -1.05) )

	ob = bpy.context.active_object

	ob.name="Keel"

	bpy.ops.transform.resize(value=(3.8,0.10,0.8))
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
	ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(1.3,0,-0.6),view_collection_props,rotation=(0,0,0),parent=the_hull.hull_object)
	ob = geometry_helper.import_object(import_library_path,"man.stand",(0.2,0,-0.95),view_collection_props,rotation=(0,0,0),parent=the_hull.hull_object)

	import_library_path="assets/boat_assets.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(0.6,0,-1.3),view_collection_props,rotation=(0,0,0),parent=the_hull.hull_object)
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(-.6,0,-1.3),view_collection_props,rotation=(0,0,0),parent=the_hull.hull_object)

	ob = geometry_helper.import_object(import_library_path,"propshaft",(-4.05,0,-1.2),view_collection_props,rotation=(0,-93,0),parent=the_hull.hull_object)


add_props()

#clean_distance=0.5
#x_locations=[	-the_hull.hull_length/2+clean_distance,
#				the_hull.hull_length/2-clean_distance]



#the_hull.cleanup_longitudal_ends(x_locations,rotations)

# Make bulkheads

levels=[ -0.9,-0.5 ]
#thickness=0.05
thickness=the_hull.structural_thickness

bulkhead_definitions = [

						(5	,False		,False	,thickness),
						(4	,levels[1]	,True	,thickness),
						(3	,levels[1]	,False	,thickness),
						(2	,levels[0]	,False	,thickness),
						(1	,levels[0]	,False	,thickness),
	
						(0	,levels[0]	,False	,thickness),
						
						(-1	,levels[0]	,False	,thickness),
						(-2	,levels[0]	,False	,thickness),						
						(-3	,levels[1]	,False	,thickness),						
						(-4	,levels[1]	,True	,thickness)

					#	(-5,False,False)
]

the_hull.cleanup_center(clean_location=[0.0,0,0],clean_size=[4-thickness+the_hull.bool_coplaner_hack,1,1])

x_locations=[	
				bulkhead_definitions[0][0]+thickness/2-the_hull.bool_coplaner_hack,
				-the_hull.hull_length/2+0.5
				#bulkhead_definitions[len(bulkhead_definitions)-1][0]
			]

rotations=[0,tail_cut_angle]
the_hull.cleanup_longitudal_ends(x_locations,rotations)



the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()

station_start=bulkhead_definitions[len(bulkhead_definitions)-1][0]+thickness/2
station_end=bulkhead_definitions[1][0]-thickness/2

keel_middle_space=0.3
the_keel = keel.keel(the_hull,lateral_offset=keel_middle_space/2,top_height=levels[0],station_start=station_start,station_end=station_end)
the_keel.make_keel(0.1)
the_hull.integrate_keel(the_keel)	

the_keel = keel.keel(the_hull,lateral_offset=-keel_middle_space/2,top_height=levels[0],station_start=station_start,station_end=station_end)
the_keel.make_keel(0.1)
the_hull.integrate_keel(the_keel)

framedata=[
[ 1, [3.191784,-14.714936,4.039575],[0.403186,0.026390,-0.141792] ],
[ 2, [0.578287,-0.787018,14.286550],[0.262983,0.032428,-0.003520] ],
[ 3, [9.353881,-1.631767,0.840273],[-0.018434,0.001545,-0.668243] ],
[ 4, [-8.121270,-1.772234,-1.529946],[-2.644429,0.379426,-0.611676] ],
[ 5, [3.023221,-0.004060,-0.415002],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)