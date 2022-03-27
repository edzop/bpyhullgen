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
   
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.bpyutils import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import window_helper
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.bpyutils import bpy_helper
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(length=11.3,width=3.9,height=3.6)

the_hull.make_hull_object()


new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length*1.01,
	width=1,
	rotation=[180,0,0],
	offset=[0,0.06,0],
	)

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0.4,width=-0.15,thickness=0.05)
new_longitudinal.set_limit_x_length(-4.5,4.5)
new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)


#window_helper.make_window_on_chine(new_chine,0.5,0.3)
#window_helper.make_window_on_chine(new_chine,1.5,0.3)
#window_helper.make_window_on_chine(new_chine,-1.5,0.3)

new_chine=chine_helper.chine_helper(the_hull,
	name="mid",
	length=the_hull.hull_length*1.01,
	width=1,
	rotation=[39,0,0],
	offset=[0,-0.2,-0.4],
	)

new_longitudinal=chine_helper.longitudinal_definition(z_offset=-0.1,width=-0.15,thickness=0.05)
new_longitudinal.set_curve(0.4,5)
new_longitudinal.set_limit_x_length(-4.5,4.5)
new_chine.add_longitudinal_definition(new_longitudinal)
the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="upper",
	length=the_hull.hull_length*1.1,
	width=1,
	rotation=[-45,0,0],
	offset=[0,0,-0.31],
	)


the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="low",
	length=the_hull.hull_length*1.5,
	width=1.6,
	rotation=[79,0,0],
	)

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0.65,width=-0.15,thickness=0.05)
new_longitudinal.set_curve(0.6,10)
new_longitudinal.set_limit_x_length(-3.4,3.4)
new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)



new_chine=chine_helper.chine_helper(the_hull,
	name="roof",
	length=the_hull.hull_length*1.4,
	width=0.8,
	rotation=[-90,0,0],
	#asymmetry=[1,0],
	offset=[0,0,-0.7],
	symmetrical=False
	)

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0.0,width=-0.15,thickness=0.05)
new_longitudinal.set_limit_x_length(-4.7,4.7)
new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)



# ================ modify hull


# ================ Add Pilot House


def add_pilot_house(the_hull):

	bpy.ops.mesh.primitive_cube_add(size=2.0, 
				enter_editmode=False, 
				location=( -0.4,0,-0.3) )

	bpy.ops.transform.resize(value=(1,1,1))
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

	bpy.ops.transform.translate(value=(-0.4, 0, 0))

	bpy.ops.mesh.bevel(offset=0.1)

	bpy.ops.object.mode_set(mode='OBJECT')

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(ob)

#add_pilot_house(the_hull)

def add_window(the_hull):
	# ================ Add Window
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(  -.7, 0, 0.35) )

	bpy.ops.transform.resize(value=(2.2,0.5,0.3))
	bpy.ops.object.transform_apply(scale=True,location=False)

	ob = bpy.context.active_object
	ob.name="Windows"

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
	bool_new.object = ob
	bool_new.operation = 'DIFFERENCE'

	bpy_helper.hide_object(ob)

#add_window(the_hull)

def add_deck_cockpit(the_hull):
	# ================ Deck Cockpit
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(  -2.5, 0, 0) )

	bpy.ops.transform.resize(value=(1.5,1,0.7))
	bpy.ops.object.transform_apply(scale=True,location=False)

	ob = bpy.context.active_object
	ob.name="Deck Cockpit"

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
	bool_new.object = ob
	bool_new.operation = 'DIFFERENCE'

	bpy_helper.hide_object(ob)

#add_deck_cockpit(the_hull)

# ============================================================================================


the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.stand",location=[0,0.4,-1.3])
the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.lie_down",location=[1.05,0,-0.77])
the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.sit_chair",location=[-0.35,0,-0.75])
the_hull.add_prop(blend_file="assets/actors.blend",target_object="man.sit_lean",location=[-2.1,0.13,-1.02])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="mattress.twin",location=[2,0,-1.1])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="mattress.twin",location=[-2,0,-1.1])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="rope_coils_2_high",location=[4.7,0,-0.7])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="yahama_gm_30hp",location=[-2.4,0,-1.1])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="anchor",location=[5.9,0.15,-0.25])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="anchor",location=[5.9,-0.15,-0.25])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="tank_fuel_5gal",location=[-0.35,0.65,-1.15],rotation=[-90,0,90])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="tank_fuel_5gal",location=[-0.60,0.65,-1.15],rotation=[-90,0,90])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="tank_fuel_5gal",location=[-0.85,0.65,-1.15],rotation=[-90,0,90])

the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="chair.reading_sitting_up_full",location=[-0.50,0,-0.52])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="battery",location=[0.6,0.17,-1.15])


clean_distance=0.33
x_locations=[	-the_hull.hull_length/2+clean_distance,
				the_hull.hull_length/2-clean_distance]


levels=[ -1.1,-0.5 ]

thickness=0.05

x_locations=[ 5,-5 ]
	
station_start=-5
station_end=5


def make_keels():
	keel_middle_space=0.3
	the_keel = keel_helper.keel(the_hull,lateral_offset=keel_middle_space/2,top_height=levels[0],station_start=station_start,station_end=station_end)
	the_keel.make_keel()
	the_hull.integrate_keel(the_keel)	

	the_keel = keel_helper.keel(the_hull,lateral_offset=-keel_middle_space/2,top_height=levels[0],station_start=station_start,station_end=station_end)
	the_keel.make_keel()
	the_hull.integrate_keel(the_keel)


the_hull.integrate_components()

framedata=[
[ 1, [3.191784,-15.956328,4.894828],[0.403186,0.026390,-0.141792] ],
[ 2, [0.578287,-0.787018,16.001944],[0.262983,0.032428,-0.003520] ],
[ 3, [10.796692,-0.904702,0.894610],[-0.018434,0.001545,-1.255421] ],
[ 4, [-8.121270,-1.772234,-1.529946],[-2.644429,0.379426,-0.611676] ],
[ 5, [3.023221,-0.004060,-0.415002],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)
