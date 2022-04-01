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
  
from bpyhullgen.bpyutils import bpy_helper
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.bpyutils import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(width=4.7)
the_hull.make_hull_object()

the_hull.bulkhead_count=0

new_chine=chine_helper.chine_definition(the_hull,
	name="wall",
	length=the_hull.hull_length,
	width=-1,
    rotation=[75,0,0],
	offset=[0,0.9,0.3])

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0,
    width=0.5,
    thickness=0.3,
    slicer_ratio=1)

new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_definition(the_hull,
	name="low",
	length=the_hull.hull_length,
	width=-1,
    rotation=[45,0,0],
	offset=[0,1.5,0])

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0,
    width=0.4,
    thickness=0.3,
    slicer_ratio=1)

new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_definition(the_hull,
	name="top",
	length=the_hull.hull_length,
	width=-1,
    rotation=[90,0,0],
	offset=[0,0,0.6],
    symmetrical=False)

new_longitudinal=chine_helper.longitudinal_definition(z_offset=0,
    width=0.4,
    thickness=0.3,
    slicer_ratio=1)

new_chine.add_longitudinal_definition(new_longitudinal)

the_hull.add_chine(new_chine)

def offline():
    # LOW Chine ==========================
    new_chine.longitudinal_z_offset=0
    new_chine.rotation=[-45,0,0]
    new_chine.offset=[0,1.5,0.0]
    new_chine.name="low_curve"
    new_chine.clear_longitudinal_elements()
    new_longitudinal=chine_helper.longitudinal_element(0,0.4,0.1)
    new_longitudinal.slicer_ratio=1
    new_chine.add_longitudinal_definition(new_longitudinal)
    new_chine.make_chine()


    # TOP Chine ==========================
    new_chine.rotation=[90,0,0]
    new_chine.offset=[0,0,0.6]
    new_chine.name="top_curve"
    new_chine.symmetrical=False
    new_chine.make_chine()

hull_material = material_helper.get_material_hull()
material_helper.disable_cutaway(hull_material)

the_hull.integrate_components()

for chine in the_hull.chine_list:   
    for chine_instances in chine.chine_instances:        
        for longitudinal_slicer in chine_instances.longitudinal_slicers:
            modifier=the_hull.hull_object.modifiers.new(name="bool_long_slice", type='BOOLEAN')
            modifier.object=longitudinal_slicer
            modifier.operation="DIFFERENCE"

for chine in the_hull.chine_list:
    for chine_instances in chine.chine_instances:
        for longitudinal_object in chine_instances.longitudinal_objects:
            curve_helper.make_rounded(longitudinal_object,0.2)


framedata=[
[ 1, [13.366231,0.000000,2.975308],[1.097236,0.000000,-0.628930] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [1.344386,-4.539305,18.487137],[0.095605,-0.101464,-0.945598] ],
[ 4, [-11.784670,-6.005480,1.519711],[-2.895431,-0.565782,-0.328658] ]
]

render_helper.setup_keyframes(framedata)
