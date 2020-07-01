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
from bpyhullgen.hullgen import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import keel
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.curve_width=1
#new_chine.curve_height=4
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.rotation=[0,0,0]
new_chine.offset=[0,0.35,0]
new_chine.asymmetry[0]=1
new_chine.add_longitudal_element(chine_helper.longitudal_element(z_offset=-0.2,width=-0.13,thickness=0.1))
new_chine.add_longitudal_element(chine_helper.longitudal_element(z_offset=-0.4,width=-0.13,thickness=0.2))

new_chine.name="side"

#new_chine.curve_twist=[0,-25,-25]
#new_chine.make_chine(twist=[0,1,2])
new_chine.make_chine()
new_chine.clear_longitudal_elements()


new_chine.curve_length=the_hull.hull_length*1.1

new_chine.rotation=[-36,0,0]
new_chine.offset=[0,0,-0.84]
new_chine.name="upper"
new_chine.curve_length=the_hull.hull_length*1.3
new_chine.make_chine()

new_chine.curve_length=the_hull.hull_length*1.3
new_chine.rotation=[39,0,0]
new_chine.offset=[0,-0.2,0.331]
new_chine.name="mid"
#new_chine.curve_twist=[0,0,0]
new_chine.make_chine()



new_chine.rotation=[82,0,0]
new_chine.offset=[0,0,0]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.4
#new_chine.curve_width=1.6
new_chine.asymmetry[1]=0
new_chine.make_chine()
new_chine.asymmetry[1]=0
#new_chine.curve_length=the_hull.hull_length*1.0


new_chine.rotation=[-90,0,0]
new_chine.offset=[0,0,-0.5]
new_chine.name="roof"
new_chine.curve_width=0.8
#new_chine.curve_angle=10
#new_chine.curve_length=13
new_chine.symmetrical=False

#new_chine.longitudal_width=0.15
new_chine.make_chine()


# ================ modify hull


	# ================ Add Pilot House
def add_pilot_house():
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.27) )

	bpy.ops.transform.resize(value=(1,0.9,1))
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

add_pilot_house()

def add_extras():
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



view_collection_props=bpy_helper.make_collection("props",bpy.context.scene.collection.children)

import_library_path="assets/actors.blend/Collection/"
ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(0,0,-0.6),view_collection_props,rotation=(0,0,0))

import_library_path="assets/boat_assets.blend/Collection/"
ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(0,0,-0.96),view_collection_props,rotation=(0,0,0))





levels=[ -0.7]
thickness=0.05

bulkhead_definitions = [

					#	(5	,False		,False	,thickness),
					#	(4	,levels[1]	,True	,thickness),
					#	(3	,levels[1]	,False	,thickness),
						(-3	,levels[0]	,False	,thickness),
						(-2	,levels[0]	,False	,thickness),	
						(-1	,levels[0]	,False	,thickness),
						
						(0	,levels[0]	,False	,thickness),
						(1	,levels[0]	,False	,thickness),
						(2	,levels[0]	,False	,thickness),
					#	(-3	,levels[1]	,False	,thickness),						
					#	(-4	,levels[1]	,True	,thickness)

					#	(-5,False,False)
]

#the_hull.cleanup_center(clean_location=[0.0,0,0],clean_size=[4-thickness+the_hull.bool_coplaner_hack,1,1])

station_start=bulkhead_definitions[0][0]+thickness/2
station_end=bulkhead_definitions[len(bulkhead_definitions)-1][0]-thickness/2



x_locations=[	
				bulkhead_definitions[0][0],
				bulkhead_definitions[len(bulkhead_definitions)-1][0]
			]

the_hull.cleanup_longitudal_ends(x_locations)

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()

def make_keels():

	keel_middle_space=0.3
	the_keel = keel.keel(the_hull,
			lateral_offset=keel_middle_space/2,
			top_height=levels[0],
			station_start=station_start,
			station_end=station_end)

	the_keel.make_keel(0.1)
	the_hull.integrate_keel(the_keel)	

	the_keel = keel.keel(the_hull,
			lateral_offset=-keel_middle_space/2,
			top_height=levels[0],
			station_start=station_start,
			station_end=station_end)

make_keels()

def add_fuel_tanks():

	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[0][0]+bulkhead_definitions[0][3]/2,
					x2=bulkhead_definitions[1][0]-bulkhead_definitions[1][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_1L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[0][0]+bulkhead_definitions[0][3]/2,
					x2=bulkhead_definitions[1][0]-bulkhead_definitions[1][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_1R")


	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[1][0]+bulkhead_definitions[1][3]/2,
					x2=bulkhead_definitions[2][0]-bulkhead_definitions[2][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_2L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[1][0]+bulkhead_definitions[1][3]/2,
					x2=bulkhead_definitions[2][0]-bulkhead_definitions[2][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_2R")				


	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[4][0]+bulkhead_definitions[4][3]/2,
					x2=bulkhead_definitions[5][0]-bulkhead_definitions[5][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_3L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[4][0]+bulkhead_definitions[4][3]/2,
					x2=bulkhead_definitions[5][0]-bulkhead_definitions[5][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_3R")								


add_fuel_tanks()

framedata=[
[ 1, [2.256688,-9.173357,4.958309],[0.000000,0.000000,0.000000] ],
[ 2, [0.315304,-0.819446,10.211541],[0.000000,0.000000,0.000000] ],
[ 3, [7.223459,-0.424494,0.439452],[0.000000,0.000000,-0.409564] ],
[ 4, [-8.400036,-1.356833,0.990534],[-2.644429,-0.102626,-0.230217] ],
[ 5, [-3.368380,-0.004060,-0.279753],[0.028123,0.029352,-0.230217] ]
]

render_helper.setup_keyframes(framedata)