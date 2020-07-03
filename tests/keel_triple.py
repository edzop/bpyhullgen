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
from bpyhullgen.hullgen import keel
from bpyhullgen.hullgen import render_helper

the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.make_hull_object()

def make_chines():

    new_chine=chine_helper.chine_helper(the_hull)

    new_chine.curve_width=1
#    new_chine.curve_height=0.5
    new_chine.curve_length=the_hull.hull_length*1.2
    new_chine.rotation=[180,0,0]
    new_chine.offset=[0,-0.35,-0.5]
    new_chine.name="side"
    new_chine.make_chine()

    new_chine.rotation=[82,0,0]
    new_chine.offset=[0,0,0]
    new_chine.name="low"
    new_chine.curve_length=the_hull.hull_length*1.4
    new_chine.asymmetry[1]=0
    new_chine.make_chine()

    new_chine.asymmetry[1]=0
    new_chine.rotation=[-90,0,0]
    new_chine.offset=[0,0,-0.5]
    new_chine.name="roof"
    new_chine.curve_width=0.8
    new_chine.symmetrical=False

    new_chine.make_chine()

make_chines()

floor_height=-0.45

bulkhead_definitions=[]

thickness=0.05

bulkhead_definitions.append([-1,floor_height,False,thickness])
bulkhead_definitions.append([1,floor_height,False,thickness])
bulkhead_definitions.append([-2,floor_height,False,thickness])
bulkhead_definitions.append([2,floor_height,False,thickness])


station_start=-2-thickness/2-0.1
station_end=3

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()

the_keel = keel.keel(the_hull,lateral_offset=0.2,top_height=floor_height,station_start=station_start,station_end=station_end)
the_keel.make_keel()
the_hull.integrate_keel(the_keel)	

the_keel = keel.keel(the_hull,lateral_offset=-0.2,top_height=floor_height,station_start=station_start,station_end=station_end)
the_keel.make_keel()
the_hull.integrate_keel(the_keel)

the_keel = keel.keel(the_hull,lateral_offset=0,top_height=floor_height,station_start=station_start,station_end=station_end)
the_keel.make_keel()
the_hull.integrate_keel(the_keel)

the_hull.hull_object.hide_viewport=True

framedata=[
[ 1, [3.191784,-9.493891,3.358960],[0.403186,0.026390,-0.141792] ],
[ 2, [0.578287,-0.787018,10.949531],[0.262983,0.032428,-0.003520] ],
[ 3, [6.574893,-1.479655,0.840273],[-0.018434,0.001545,-0.802150] ],
[ 4, [-4.350198,-2.761443,0.150181],[-0.363852,0.379426,-0.492896] ],
[ 5, [3.023221,-0.004060,-0.149050],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)