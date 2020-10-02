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
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.hullgen import render_helper
from bpyhullgen.hullgen import bpy_helper

from math import radians

performance_timer = bpy_helper.ElapsedTimer()


the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.start_bulkhead_location=-3

the_hull.hull_output_scale=1/16
target_screw_size=4.1 # mm

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.target_screw_size=target_screw_size

new_chine.curve_width=1
#new_chine.curve_height=4
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.rotation=[0,0,0]
new_chine.offset=[0,0.35,0]
new_chine.asymmetry[0]=1

new_chine.name="side"

new_longitudal=chine_helper.longitudal_element(z_offset=-0.2,width=-0.13,thickness=0.1)
new_longitudal.set_limit_x_length(the_hull.start_bulkhead_location,2)
#new_chine.add_longitudal_element(new_longitudal)

#new_chine.make_segmented_longitudals(z_offset=-0.2,start_bulkhead=0,end_bulkhead=5)

#new_chine.clear_longitudal_elements()
#new_chine.curve_twist=[0,-25,-25]
#new_chine.make_chine(twist=[0,1,2])
new_chine.make_chine()

#new_chine.make_screws()

new_chine.clear_longitudal_elements()



new_chine.curve_length=the_hull.hull_length*1.1

new_chine.rotation=[36,0,0]
new_chine.offset=[0,0,-0.84]
new_chine.name="upper"
new_chine.curve_length=the_hull.hull_length*1.3
new_chine.make_chine()

new_chine.curve_length=the_hull.hull_length*1.3
new_chine.rotation=[-39,0,0]
new_chine.offset=[0,-0.2,0.331]
new_chine.name="mid"
#new_chine.curve_twist=[0,0,0]
new_chine.make_chine()



new_chine.rotation=[-82,0,0]
new_chine.offset=[0,0,0]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.4
#new_chine.curve_width=1.6
new_chine.asymmetry[1]=0
new_chine.make_chine()
new_chine.asymmetry[1]=0
#new_chine.curve_length=the_hull.hull_length*1.0


new_chine.rotation=[90,0,0]
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


def add_props():
	view_collection_props=bpy_helper.make_collection("props",bpy.context.scene.collection.children)

	import_library_path="assets/actors.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(0,0,-0.6),view_collection_props,rotation=(0,0,0))

	import_library_path="assets/boat_assets.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(0,0,-0.96),view_collection_props,rotation=(0,0,0))

#add_props()



levels=[ -0.7]


bulkhead_definitions = []


current_bulkhead_location=the_hull.start_bulkhead_location
for bulkhead_index in range(0,the_hull.bulkhead_count):
	bulkhead_definitions.append([current_bulkhead_location,-0.7,False,the_hull.bulkhead_thickness])
	current_bulkhead_location+=the_hull.bulkhead_spacing
	print("add bulkhead: %d %f"%(bulkhead_index,current_bulkhead_location))


#bulkhead_definitions = [

					#	(5	,False		,False	,bulkhead_thickness),
					#	(4	,levels[1]	,True	,bulkhead_thickness),
					#	(3	,levels[1]	,False	,bulkhead_thickness),
#						(-3	,levels[0]	,False	,bulkhead_thickness),
#						(-2	,levels[0]	,False	,bulkhead_thickness),	
#						(-1	,levels[0]	,False	,bulkhead_thickness),
						
#						(0	,levels[0]	,False	,bulkhead_thickness),
#						(1	,levels[0]	,False	,bulkhead_thickness),
#						(2	,levels[0]	,False	,bulkhead_thickness),
					#	(-3	,levels[1]	,False	,bulkhead_thickness),						
					#	(-4	,levels[1]	,True	,bulkhead_thickness)

					#	(-5,False,False)
#]

#the_hull.cleanup_center(clean_location=[0.0,0,0],clean_size=[4-bulkhead_thickness+the_hull,1,1])

station_start=bulkhead_definitions[0][0]-the_hull.bulkhead_thickness
station_end=bulkhead_definitions[len(bulkhead_definitions)-1][0]+the_hull.bulkhead_thickness



#x_locations=[	
#				bulkhead_definitions[0][0],
#				bulkhead_definitions[len(bulkhead_definitions)-1][0]
#			]

#the_hull.cleanup_longitudal_ends(x_locations)

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()
the_hull.hull_object.hide_viewport=True

def make_keels():
	the_keel_builder = keel_helper.keel_builder(the_hull)
	the_keel_builder.make_segmented_keel(top_height=levels[0],start_bulkhead=1,end_bulkhead=6)
	the_keel_builder.target_screw_size=target_screw_size
	#the_keel_builder.make_screws()

make_keels()


def disabled_keel():

		keel_middle_space=0.3
		the_keel = keel_helper.keel(the_hull,
				lateral_offset=keel_middle_space/2,
				top_height=levels[0],
				station_start=station_start,
				station_end=station_end)

		the_keel.set_limit_x_length(-1-thickness,1+thickness)

		the_keel.make_keel(keel_thickness)
		the_hull.integrate_keel(the_keel)	

		the_keel = keel_helper.keel(the_hull,
				lateral_offset=-keel_middle_space/2,
				top_height=levels[0],
				station_start=station_start,
				station_end=station_end)

		the_keel.set_limit_x_length(-1-thickness,1+thickness)

		the_keel.make_keel(keel_thickness)
		the_hull.integrate_keel(the_keel)				

def make_fuel_tanks():

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


#make_keels()

framedata=[
[ 1, [2.256688,-9.173357,4.958309],[0.000000,0.000000,0.000000] ],
[ 2, [0.315304,-0.819446,10.211541],[0.000000,0.000000,0.000000] ],
[ 3, [7.223459,-0.424494,0.439452],[0.000000,0.000000,-0.409564] ],
[ 4, [-8.400036,-1.356833,0.990534],[-2.644429,-0.102626,-0.230217] ],
[ 5, [-3.368380,-0.004060,-0.279753],[0.028123,0.029352,-0.230217] ]
]

render_helper.setup_keyframes(framedata)

performance_timer.get_elapsed_string()