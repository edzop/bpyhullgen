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

from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.hullgen import render_helper
from bpyhullgen.bpyutils import bpy_helper

performance_timer = bpy_helper.ElapsedTimer()

the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.make_hull_object()


new_chine=chine_helper.chine_helper(the_hull,
    name="side",
    length=the_hull.hull_length*1.2,
    width=1,
    rotation=[180,0,0],
    offset=[0,-0.35,-0.5])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
    name="low",
    length=the_hull.hull_length*1.4,
    width=1,
    rotation=[82,0,0])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
    name="roof",
    length=the_hull.hull_length*1.2,
    width=0.8,
    rotation=[-90,0,0],
    offset=[0,0,-0.5],
    symmetrical=False)

the_hull.add_chine(new_chine)


the_hull.default_floor_height=-0.45

the_keel_builder = keel_helper.keel_builder(the_hull,keel_middle_space=0.3)

the_keel_builder.make_solid_double_keel(top_height=the_hull.default_floor_height,start_bulkhead=1,end_bulkhead=6)
the_keel_builder.make_solid_single_keel(top_height=the_hull.default_floor_height,start_bulkhead=1,end_bulkhead=6)

the_hull.integrate_components()

the_hull.hull_object.hide_viewport=True

framedata=[
[ 1, [3.191784,-9.493891,3.358960],[0.403186,0.026390,-0.141792] ],
[ 2, [0.578287,-0.787018,10.949531],[0.262983,0.032428,-0.003520] ],
[ 3, [6.574893,-1.479655,0.840273],[-0.018434,0.001545,-0.802150] ],
[ 4, [-4.350198,-2.761443,0.150181],[-0.363852,0.379426,-0.492896] ],
[ 5, [3.023221,-0.004060,-0.149050],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)

performance_timer.get_elapsed_string()