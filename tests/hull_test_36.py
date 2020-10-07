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
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.hullgen import bpy_helper

the_hull=hull_maker.hull_maker(width=5,length=11,height=3)

the_hull.hull_output_scale=1/16
the_hull.target_screw_size=4.1

the_hull.bulkhead_count=9
the_hull.bulkhead_start_location=-4

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length*1.1,
	width=1.2,
	rotation=[180,0,0],
	offset=[0,-0.27,-0.5])

new_longitudal=chine_helper.longitudal_definition(z_offset=-0.3,width=-0.2,thickness=0.1)
new_chine.add_longitudal_definition(new_longitudal)
the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="mid",
	length=the_hull.hull_length*1.1,
	width=1.4,
	rotation=[40,0,0],
	offset=[0,-0.2,0.45])

new_chine.add_longitudal_definition(chine_helper.longitudal_definition(z_offset=-0.83,width=-0.2,thickness=0.1))

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="upper",
	length=the_hull.hull_length*1.2,
	width=1.1,
	rotation=[-36,0,0],
	offset=[0,0,0.9])

the_hull.add_chine(new_chine)


#window_helper.make_window_on_chine(new_chine,0.5,0.34)
#window_helper.make_window_on_chine(new_chine,1.5,0.34)
#window_helper.make_window_on_chine(new_chine,-1.5,0.34)


new_chine=chine_helper.chine_helper(the_hull,
	name="low",
	length=the_hull.hull_length*1.2,
	width=1.6,
	rotation=[75,0,0],
	offset=[0,0,0.2])

new_chine.curve_twist=[0,30,-50]

#new_chine.longitudal_count=0
#new_chine.longitudal_bend_radius=0.2
#new_chine.set_longitudal_curve(0.2,10)
#new_chine.longitudal_z_offset=-0.4
the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="roof",
	length=the_hull.hull_length*1.25,
	width=0.8,
	rotation=[-90,1,0],
	offset=[0,0,-0.51],
	symmetrical=False)


new_longitudal=chine_helper.longitudal_definition(z_offset=0,width=-0.2,thickness=0.1)
new_chine.add_longitudal_definition(new_longitudal)

the_hull.add_chine(new_chine)

# ================ modify hull ==============================

tail_cut_angle=-22

def add_deck_cockpit():

	# ================ Add deck cockpit
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, 0) )

	ob = bpy.context.active_object

	ob.name="deck_cockpit"
	
	bpy.ops.transform.resize(value=(1,1,2))
	bpy.ops.object.transform_apply(scale=True,location=False)
	bpy.ops.transform.rotate(value=radians(tail_cut_angle),orient_axis='Y')

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
	bool_new.object = ob
	bool_new.operation = 'DIFFERENCE'

	bpy_helper.hide_object(ob)

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

	bpy_helper.hide_object(ob)

#add_pilot_house()

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

	bpy_helper.hide_object(rudder_object)

	# ================ Add Keel
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.9, 0, -1.05) )

	ob = bpy.context.active_object

	ob.name="Keel"

	bpy.ops.transform.resize(value=(3.8,0.10,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(ob)

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

	bpy_helper.hide_object(ob)

# =======================================================

print("extra")
the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.sit_chair",location=[1.3,0,-0.6])
the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.stand",location=[0.2,0,-0.95])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="propshaft",location=[-4.05,0,-1.2],rotation=[0,93,0])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="wheel_axle.8ft",location=[0.6,0,-1.3])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="wheel_axle.8ft",location=[-0.6,0,-1.3])

rotations=[tail_cut_angle,0]
clean_distance=0.5
x_locations=[	-the_hull.hull_length/2+clean_distance,
				the_hull.hull_length/2-clean_distance]


levels=[ -0.9,-0.5 ]

thickness=the_hull.structural_thickness



the_keel_builder = keel_helper.keel_builder(the_hull)
the_keel_builder.make_solid_double_keel(top_height=levels[0],start_bulkhead=1,end_bulkhead=6)


the_hull.integrate_components()

the_hull.cleanup_longitudal_ends(x_locations,rotations)

add_deck_cockpit()

framedata=[
[ 1, [3.191784,-14.714936,4.039575],[0.403186,0.026390,-0.141792] ],
[ 2, [0.578287,-0.787018,14.286550],[0.262983,0.032428,-0.003520] ],
[ 3, [9.353881,-1.631767,0.840273],[-0.018434,0.001545,-0.668243] ],
[ 4, [-8.121270,-1.772234,-1.529946],[-2.644429,0.379426,-0.611676] ],
[ 5, [3.023221,-0.004060,-0.415002],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)

performance_timer.get_elapsed_string()