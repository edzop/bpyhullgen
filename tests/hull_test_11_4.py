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
from bpyhullgen.hullgen import window_helper
from bpyhullgen.hullgen import keel

the_hull=hull_maker.hull_maker(length=11.4,width=3.9,height=3.6)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.rotation=[180,0,0]
new_chine.offset=[0,-0.06,-0.5]
new_chine.name="side"
new_chine.longitudal_count=1
new_chine.longitudal_thickness=0.05
new_chine.longitudal_width=-0.15

new_chine.make_chine()

window_helper.make_window_on_chine(new_chine,0.5,-0.3)
window_helper.make_window_on_chine(new_chine,1.5,-0.3)
window_helper.make_window_on_chine(new_chine,-1.5,-0.3)


new_chine.rotation=[-39,0,0]
new_chine.offset=[0,-0.2,-0.4]
new_chine.longitudal_z_offset=-0.33
new_chine.name="mid"
new_chine.set_longitudal_curve(0.4,10)
new_chine.longitudal_z_offset=-0.55
new_chine.make_chine()

new_chine.longitudal_count=0
new_chine.rotation=[45,0,0]
new_chine.offset=[0,0,-0.31]
new_chine.name="upper"
new_chine.longitudal_z_offset=0
new_chine.set_longitudal_curve(0,0)
new_chine.make_chine()


new_chine.longitudal_count=0
new_chine.rotation=[-79,0,0]
new_chine.offset=[0,0,0]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.5
new_chine.curve_width=1.6
new_chine.set_longitudal_curve(0.6,10)
new_chine.longitudal_z_offset=-0.5
new_chine.make_chine()

new_chine.longitudal_count=1
new_chine.rotation=[90,0,0]
new_chine.offset=[0,0,-0.7]
new_chine.name="roof"
new_chine.curve_width=0.8
#new_chine.curve_angle=55
new_chine.longitudal_z_offset=0
new_chine.symmetrical=False
new_chine.set_longitudal_curve(0,0)
new_chine.make_chine()

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

	curve_helper.hide_object(ob)

add_pilot_house(the_hull)

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

	curve_helper.hide_object(ob)

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

	curve_helper.hide_object(ob)

add_deck_cockpit(the_hull)

# ============================================================================================
def add_props():
	view_collection_props=curve_helper.make_collection("props",bpy.context.scene.collection.children)

	import_library_path="assets/actors.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"man.stand",(0,0.4,-1.3),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"man.lie_down",(1.05,0,-0.64),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(-0.35,0,-0.75),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"man.sit_lean",(-2.1,0.13,-0.87),view_collection_props)


	import_library_path="assets/boat_assets.blend/Collection/"
	
	ob = geometry_helper.import_object(import_library_path,"mattress.twin",(2,0,-0.9),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"mattress.twin",(-2,0,-0.9),view_collection_props)

	ob = geometry_helper.import_object(import_library_path,"rope_coils_2_high",(4.7,0,-0.7),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"yahama_gm_30hp",(-2.4,0,-1.1),view_collection_props)


	ob = geometry_helper.import_object(import_library_path,"chair.reading_sitting_up_full",(-0.7,0,-0.2),view_collection_props)

	ob = geometry_helper.import_object(import_library_path,"anchor",(5.9,0.15,-0.25),view_collection_props)
	ob = geometry_helper.import_object(import_library_path,"anchor",(5.9,-0.15,-0.25),view_collection_props)


	ob = geometry_helper.import_object(import_library_path,"tank_fuel_5gal",(-0.60,0.65,-1.15),view_collection_props,rotation=(-90,0,90))
	ob = geometry_helper.import_object(import_library_path,"tank_fuel_5gal",(-0.85,0.65,-1.15),view_collection_props,rotation=(-90,0,90))
	ob = geometry_helper.import_object(import_library_path,"tank_fuel_5gal",(-0.35,0.65,-1.15),view_collection_props,rotation=(-90,0,90))


	ob = geometry_helper.import_object(import_library_path,"battery",(0.6,0.17,-1.15),view_collection_props,rotation=(0,0,0))


add_props()

clean_distance=0.33
x_locations=[	-the_hull.hull_length/2+clean_distance,
				the_hull.hull_length/2-clean_distance]

the_hull.cleanup_longitudal_ends(x_locations)

the_hull.cleanup_center(clean_location=[-1.2,0,0],clean_size=[4.2,1,1])

levels=[ -1.1,-0.5 ]

thickness=0.05

bulkhead_definitions = [

						(5,False,False,thickness),
						(4,levels[1],True,thickness),						
						(3,levels[1],False,thickness),
						(2,levels[0],False,thickness), 
						(1,levels[0],False,thickness),
	
						(0,levels[0],False,thickness),
						
						(-1,levels[0],False,thickness),
						(-2,levels[0],False,thickness),
						(-3,levels[1],False,thickness),
						(-4,levels[1],True,thickness),					
						(-5,False,False,thickness)
]

x_locations=[	
				bulkhead_definitions[0][0]+thickness/2-the_hull.bool_coplaner_hack,
				bulkhead_definitions[len(bulkhead_definitions)-1][0]-thickness/2+the_hull.bool_coplaner_hack
			]

the_hull.cleanup_longitudal_ends(x_locations)


the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()

			
#the_hull.hull_object.hide_set(True)
#the_hull.hull_object.hide_render=True
keel_middle_space=0.3
the_keel = keel.keel(the_hull,lateral_offset=keel_middle_space/2,top_height=levels[0])
the_keel.make_keel()
the_hull.integrate_keel(the_keel)	

the_keel = keel.keel(the_hull,lateral_offset=-keel_middle_space/2,top_height=levels[0])
the_keel.make_keel()
the_hull.integrate_keel(the_keel)


