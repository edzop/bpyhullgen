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
from bpyhullgen.hullgen import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import bulkhead
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import render_helper


the_hull=hull_maker.hull_maker(length=12,width=1,height=0.8)
the_hull.make_hull_object()


new_chine=chine_helper.chine_helper(the_hull,
	name="side1",
	length=the_hull.hull_length*1.3,
	width=1,
	offset=[0,0,0],
    symmetrical=False
	)

new_longitudal=chine_helper.longitudal_definition(z_offset=-0.2,width=-0.4,thickness=0.1)
new_longitudal.set_limit_x_length(-6,6)
new_chine.add_longitudal_definition(new_longitudal)

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="side2",
	length=the_hull.hull_length*1.3,
	width=1,
	offset=[0,0.0,0],
    symmetrical=False,
    rotation=[-180,0,0]
	)

new_longitudal=chine_helper.longitudal_definition(z_offset=-0.2,width=-0.4,thickness=0.1)
new_longitudal.set_limit_x_length(the_hull.start_bulkhead_location,2)
new_chine.add_longitudal_definition(new_longitudal)

the_hull.add_chine(new_chine)

the_hull.bulkhead_count=0

the_hull.integrate_components()

for chine in the_hull.chine_list:
    for chine_instance in chine.chine_instances:
        curve = chine_instance.curve_object

        curve.hide_viewport=False
        curve.hide_render=False
        wireframe = curve.modifiers.new(type="WIREFRAME", name="wireframe")

the_hull.hull_object.hide_render=True
the_hull.hull_object.hide_viewport=True

info_text="Demonstration of two chines with reverse extrude directions"
geometry_helper.add_info_text(info_text)

framedata=[
[ 1, [0.000000,-1.362492,27.603287],[0.000000,0.196316,-0.509545] ],
[ 2, [19.154360,5.335245,12.450815],[1.170676,-0.401701,-0.356683] ]
]

render_helper.setup_keyframes(framedata)
