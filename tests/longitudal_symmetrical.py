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
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(length=12,width=5,height=0.8)
the_hull.make_hull_object()

the_hull.bulkhead_count=0

new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length,
	width=-1,
	offset=[0,0.7,0])

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0,
    width=0.2,
    thickness=0.2)

new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)


the_hull.integrate_components()

for chine in the_hull.chine_list:
    for chine_instance in chine.chine_instances:        
        ob=chine_instance.curve_object
        ob.hide_viewport=False
        ob.hide_render=False
        wireframe = ob.modifiers.new(type="WIREFRAME", name="w2")

the_hull.hull_object.hide_viewport=True
the_hull.hull_object.hide_render=True

framedata=[
[ 1, [0.000000,-2.867616,18.242138],[0.000000,0.000000,-0.166539] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [7.771358,0.000000,2.225859],[-0.018434,0.001545,-0.135337] ]
]

render_helper.setup_keyframes(framedata)
