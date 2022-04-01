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

the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.make_hull_object()

new_chine=chine_helper.chine_definition(the_hull,
	name="side",
	length=the_hull.hull_length*1.2,
	width=1,
	offset=[0,-0.35,-0.5],
	rotation=[180,0,0])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_definition(the_hull,
	name="low",
	length=the_hull.hull_length*1.4,
	width=1,
	offset=[0,0,0],
	rotation=[82,0,0])

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_definition(the_hull,
	name="roof",
	length=the_hull.hull_length*1.4,
	width=0.8,
	rotation=[-90,1,0],
	offset=[0,0,-0.5],
	symmetrical=False)

the_hull.add_chine(new_chine)

the_hull.bulkhead_count=0

the_hull.integrate_components()

framedata=[
[ 1, [6.096892,-5.457021,-0.208632],[1.097236,-0.166389,-0.166539] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [6.916142,-0.764634,0.672572],[-0.018434,0.001545,-0.917216] ],
[ 4, [-6.122976,-4.947592,0.150181],[-0.758119,0.379426,-0.492896] ],
[ 5, [6.0,-0.5,0],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)
