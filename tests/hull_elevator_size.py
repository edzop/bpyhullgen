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
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(width=1,length=1.95,height=1)

the_hull.make_hull_object()


new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length*2.0,
	width=0.35,
	offset=[-.95,0,0],
	asymmetry=[1,0])

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="low",
	length=the_hull.hull_length*2.0,
	width=0.35,
	offset=[-.95,0,0],
	asymmetry=[1,0],
    rotation=[82,0,0])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="upper",
	length=the_hull.hull_length*2.0,
	width=0.35,
	offset=[-.95,0,0],
	asymmetry=[1,0],
    rotation=[36,0,0])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="roof",
	length=the_hull.hull_length*3.0,
	width=-0.35,
	offset=[-0.5,0,1.65],
	asymmetry=[1,0],
    rotation=[-90,12,0],
    symmetrical=False)

the_hull.add_chine(new_chine)

the_hull.integrate_components()

framedata=[

[ 1, [2.236060,-2.631392,1.005279],[0.226258,-0.350238,0.121912] ],
[ 2, [0.832591,-1.967613,2.672717],[0.000000,0.000000,0.000000] ],
[ 3, [2.832714,-0.172231,0.672572],[-0.018434,0.001545,-0.012598] ],
[ 4, [-1.995935,-2.113114,0.150181],[-0.210668,0.021942,-0.125707] ],
[ 5, [-3.033586,-0.187909,-0.149050],[-0.837497,-0.021717,0.000000] ]

]

render_helper.setup_keyframes(framedata)
