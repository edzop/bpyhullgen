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
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(width=4.7)
the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.longitudal_count=1
new_chine.longitudal_thickness=0.3
new_chine.longitudal_width=0.5
new_chine.longitudal_height=0
new_chine.slicer_longitudal_ratio=1

new_chine.longitudal_bend_radius=0.8
new_chine.longitudal_curve_angle=4

new_chine.curve_width=-1
new_chine.curve_length=the_hull.hull_length+0.1

new_chine.rotation=[75,0,0]
new_chine.offset=[0,0.9,0.3]
new_chine.name="wall_curve"

new_chine.make_chine()

def not_used():
    new_chine.rotation=[-45,0,0]
    new_chine.offset=[0,1.5,0.0]
    new_chine.name="mid_curve"
    new_chine.make_chine()

    new_chine.rotation=[-90,0,0]
    new_chine.offset=[0,0,0.6]
    new_chine.name="top_curve"
    new_chine.symmetrical=False
    new_chine.make_chine()

for lg in the_hull.longitudal_slicer_list:
    modifier=the_hull.hull_object.modifiers.new(name="bool_long_slice", type='BOOLEAN')
    modifier.object=lg
    modifier.operation="DIFFERENCE"
    curve_helper.hide_object(lg)

for lg in the_hull.longitudal_list:
    curve_helper.make_rounded(lg,0.2)

hull_material = material_helper.get_material_hull()
material_helper.disable_cutaway(hull_material)

framedata=[
[ 1, [13.366231,0.000000,2.975308],[1.097236,0.000000,-0.628930] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [1.344386,-4.539305,18.487137],[0.095605,-0.101464,-0.945598] ],
[ 4, [-11.784670,-6.005480,1.519711],[-2.895431,-0.565782,-0.328658] ]
]

render_helper.setup_keyframes(framedata)
