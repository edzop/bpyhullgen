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
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(length=11.2,width=3.9,height=3.6)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.rotation=[180,0,0]
new_chine.offset=[0,-0.06,-0.5]
new_chine.name="side"
#new_chine.curve_twist=[0,-25,-25]
#new_chine.make_chine(twist=[0,1,2])
new_chine.longitudal_count=1
new_chine.longitudal_z_offset=0.1
new_chine.make_chine()

window_helper.make_window_on_chine(new_chine,0.5,-0.2)
window_helper.make_window_on_chine(new_chine,1.5,-0.2)
window_helper.make_window_on_chine(new_chine,-1.5,-0.2)


new_chine.rotation=[39,0,0]
new_chine.offset=[0,-0.2,-0.4]
new_chine.name="mid"
new_chine.longitudal_count=1
new_chine.longitudal_z_offset=-0.2
#new_chine.curve_twist=[0,0,0]
new_chine.make_chine()

new_chine.rotation=[-45,0,0]
new_chine.offset=[0,0,-0.31]
new_chine.name="upper"
new_chine.longitudal_count=0
new_chine.make_chine()

new_chine.rotation=[79,3,0]
new_chine.offset=[0,0,0]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.5
new_chine.curve_width=1.6
new_chine.longitudal_count=1
new_chine.longitudal_z_offset=-0.2
new_chine.make_chine()
#new_chine.curve_length=the_hull.hull_length*1.0

new_chine.rotation=[-90,0,0]
new_chine.offset=[0,0,-0.7]
new_chine.name="roof"
new_chine.curve_width=0.8
new_chine.curve_angle=10
#new_chine.curve_length=13
new_chine.symmetrical=False
new_chine.longitudal_count=0
#new_chine.longitudal_width=0.15
new_chine.make_chine()

# ================ modify hull


# ================ Add Rudder
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, -1.25) )

rudder_object = bpy.context.active_object

rudder_object.name="Rudder"

bpy.ops.transform.resize(value=(0.7,0.05,0.8))
bpy.ops.object.transform_apply(scale=True,location=False)

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
bool_new.object = rudder_object
bool_new.operation = 'UNION'

curve_helper.hide_object(rudder_object)

# ================ Add Keel
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 0, -1.25) )

ob = bpy.context.active_object

ob.name="Keel"

bpy.ops.transform.resize(value=(7,0.05,0.8))
bpy.ops.object.transform_apply(scale=True,location=False)

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
bool_new.object = ob
bool_new.operation = 'UNION'

curve_helper.hide_object(ob)

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

curve_helper.hide_object(ob)

# ================ Add deck cockpit
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0) )

ob = bpy.context.active_object

ob.name="deck_cockpit"
ob.display_type="WIRE"

bpy.ops.transform.resize(value=(1.8,1,1))
bpy.ops.object.transform_apply(scale=True,location=False)
ob.location.x=-3

bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
bool_new.object = ob
bool_new.operation = 'DIFFERENCE'

curve_helper.hide_object(ob)

# =======================================================

#material_helper.disable_cutaway(material_helper.get_material_hull())


#geometry_helper.apply_all_bool_modifiers()
#curve_helper.select_object(the_hull.hull_object,True)

view_collection_props=curve_helper.make_collection("props",bpy.context.scene.collection.children)
import_library_path="assets/boat_assets.blend/Collection/"
ob = geometry_helper.import_object(import_library_path,"propshaft",(-4.8,0,-1.4),view_collection_props,rotation=(0,93,0))
ob = geometry_helper.import_object(import_library_path,"yahama_gm_30hp",(-2.95,0,-1.1),view_collection_props,rotation=(0,4,0))




levels=[ -0.9,-0.5 ]

# X station position
# Vertical height adjust (or FALSE for no vertical height adjustment)
# Cutout void in middle (False for watertight bulkhead)


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

framedata=[
[ 1, [3.096725,-15.350384,4.958309],[0.308127,0.029809,-0.078311] ],
[ 2, [0.315304,-0.819446,15.150707],[0.000000,0.000000,0.000000] ],
[ 3, [10.815125,-0.906247,0.801231],[0.000000,0.000000,-1.348800] ],
[ 4, [-8.121270,-1.772234,-1.529946],[-2.644429,0.379426,-0.611676] ],
[ 5, [3.023221,-0.004060,-0.415002],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)
