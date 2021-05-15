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
from bpyhullgen.hullgen import render_helper
from bpyhullgen.bpyutils import bpy_helper

performance_timer = bpy_helper.ElapsedTimer()

the_hull=hull_maker.hull_maker(length=11.9,width=3.9,height=3.6)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length*1.2,
	width=1.2,
	offset=[0,0.06,-0.5])

new_chine.add_longitudinal_definition(chine_helper.longitudinal_definition(z_offset=0.1,width=-0.2,thickness=0.1))

the_hull.add_chine(new_chine)

#window_helper.make_window_on_chine(new_chine,0.5,-0.2)
#window_helper.make_window_on_chine(new_chine,1.5,-0.2)
#window_helper.make_window_on_chine(new_chine,-1.5,-0.2)


new_chine=chine_helper.chine_helper(the_hull,
	name="mid",
	length=the_hull.hull_length*1.3,
	width=1.2,
	rotation=[39,0,0],
	offset=[0,-0.2,-0.3],

	)

new_chine.add_longitudinal_definition(chine_helper.longitudinal_definition(z_offset=-0.3,width=-0.2,thickness=0.1))

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
	rotation=[79,3,0],
	)

new_chine.add_longitudinal_definition(chine_helper.longitudinal_definition(z_offset=0,width=-0.2,thickness=0.1))

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="roof",
	length=the_hull.hull_length*1.6,
	width=0.8,
	rotation=[-90,0,0],
	symmetrical=False,
	offset=[0,0,-0.7],
	)

new_chine.curve_width=0.8
new_chine.curve_angle=10

the_hull.add_chine(new_chine)



# ================ modify hull

def offline2():
	# ================ Add Rudder
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, -1.25) )

	rudder_object = bpy.context.active_object

	rudder_object.name="Rudder"

	bpy.ops.transform.resize(value=(0.7,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = rudder_object
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(rudder_object)

	# ================ Add Keel
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 0, -1.25) )

	ob = bpy.context.active_object

	ob.name="Keel"

	bpy.ops.transform.resize(value=(7,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(ob)

	# ================ Add Pilot House
	bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.4, 0, -0.3) )

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

# ================ Add Tail cutaway
deck_cockpit=geometry_helper.make_cube(name="tail",
		location=[-7.5,0,0],size=[4,4,4],rotation=[0,22,0])

the_hull.add_subtractive_object(deck_cockpit)

# ================ Add Nose cutaway
deck_cockpit=geometry_helper.make_cube(name="nose",
		location=[8,0,0],size=[4,4,4],rotation=[0,0,0])

the_hull.add_subtractive_object(deck_cockpit)



# ================ Add Cockpit
deck_cockpit=geometry_helper.make_cube(name="cockpit",
		location=[-0.8,0,0.5],size=[2,.8,2],rotation=[0,0,0])

the_hull.add_subtractive_object(deck_cockpit)


the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="propshaft",location=[-4.8,0,-1.4],rotation=[0,93,0])
the_hull.add_prop(blend_file="assets/boat_assets.blend",target_object="yahama_gm_30hp",location=[-2.95,0,-1.1],rotation=[0,4,0])


levels=[ -0.9,-0.5 ]

the_hull.default_floor_height=-0.9

the_hull.integrate_components()

framedata=[
[ 1, [3.096725,-15.350384,4.958309],[0.308127,0.029809,-0.078311] ],
[ 2, [0.315304,-0.819446,15.150707],[0.000000,0.000000,0.000000] ],
[ 3, [10.815125,-0.906247,0.801231],[0.000000,0.000000,-1.348800] ],
[ 4, [-8.121270,-1.772234,-1.529946],[-2.644429,0.379426,-0.611676] ],
[ 5, [3.023221,-0.004060,-0.415002],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)

performance_timer.get_elapsed_string()
