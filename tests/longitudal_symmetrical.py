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
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(length=12,width=5,height=0.8)
the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)
#new_chine.extrude_width=0.1
#new_chine.rotation=[0,0,0]
new_chine.offset=[0,-0.4,0]
new_chine.name="side"
new_chine.curve_width=1

#chine_helper.longitudal_element(0,0.15,0.8)
new_longitudal=chine_helper.longitudal_element(z_offset=0,width=-0.2,thickness=0.2)
#new_longitudal.slicer_ratio=1
new_chine.add_longitudal_element(new_longitudal)

new_chine.symmetrical=True
new_chine.make_chine()

for l in the_hull.chine_list:
    l.hide_viewport=False
    l.hide_render=False
    wireframe = l.modifiers.new(type="WIREFRAME", name="w2")

bpy.data.objects.remove(the_hull.hull_object)

framedata=[
[ 1, [0.000000,-2.867616,18.242138],[0.000000,0.000000,-0.166539] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [7.771358,0.000000,2.225859],[-0.018434,0.001545,-0.135337] ]
]

render_helper.setup_keyframes(framedata)
