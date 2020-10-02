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

def make_chines():

    new_chine=chine_helper.chine_helper(the_hull)

    new_chine.asymmetry[0]=1

    new_chine.curve_width=0.35
    new_chine.longitudal_curve_angle=40
    new_chine.curve_length=the_hull.hull_length*2
    #new_chine.curve_angle=23
    new_chine.rotation=[-180,0,0]
    new_chine.offset=[-.95,0,0]
    new_chine.name="side"
    new_chine.make_chine()

    new_chine.rotation=[-82,0,0]
    #new_chine.offset=[0,0,0]
    new_chine.name="low"
    #new_chine.curve_length=the_hull.hull_length*1.4
#    new_chine.asymmetry[1]=0
    new_chine.make_chine()


    #new_chine.curve_length=the_hull.hull_length*1.1
    new_chine.longitudal_count=0
    new_chine.rotation=[36,0,0]
    #new_chine.offset=[0.04,0,-0.06]
    new_chine.name="upper"
    #new_chine.curve_length=the_hull.hull_length*1.3
    new_chine.make_chine()



    new_chine.asymmetry[1]=0
    new_chine.rotation=[90,0,0]
    new_chine.offset=[.5,0,0.6]

    new_chine.curve_width=-0.35
    new_chine.curve_length=the_hull.hull_length*3

    new_chine.name="roof"
    new_chine.width=-1
    new_chine.extrude_width=-1
    new_chine.symmetrical=False

    new_chine.make_chine()




make_chines()

framedata=[

[ 1, [2.236060,-2.631392,1.005279],[0.226258,-0.350238,0.121912] ],
[ 2, [0.832591,-1.967613,2.672717],[0.000000,0.000000,0.000000] ],
[ 3, [2.832714,-0.172231,0.672572],[-0.018434,0.001545,-0.012598] ],
[ 4, [-1.995935,-2.113114,0.150181],[-0.210668,0.021942,-0.125707] ],
[ 5, [-3.033586,-0.187909,-0.149050],[-0.837497,-0.021717,0.000000] ]

]

render_helper.setup_keyframes(framedata)
