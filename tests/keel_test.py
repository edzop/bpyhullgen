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

    new_chine.rotation=[-82,0,0]
    new_chine.offset=[0,0,0]
    new_chine.name="low"
    new_chine.curve_length=the_hull.hull_length*1.4
    new_chine.asymmetry[1]=0
    new_chine.make_chine()

    new_chine.asymmetry[1]=0
    new_chine.rotation=[90,0,0]
    new_chine.offset=[0,0,-0.5]
    new_chine.name="roof"
    new_chine.curve_width=0.8
    new_chine.symmetrical=False

    new_chine.make_chine()

make_chines()

floor_height=-0.45

bulkhead_definitions=[]

bulkhead_definitions.append([-1,floor_height,False])
bulkhead_definitions.append([1,floor_height,False])

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()

the_keel = keel.keel(the_hull,lateral_offset=0.3,top_height=floor_height)
the_keel.make_keel()
the_hull.integrate_keel(the_keel)	

the_keel = keel.keel(the_hull,lateral_offset=-0.3,top_height=floor_height)
the_keel.make_keel()
the_hull.integrate_keel(the_keel)


the_hull.hull_object.hide_set(True)