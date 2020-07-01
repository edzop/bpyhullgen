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
    new_chine.rotation=[180,0,0]
    new_chine.offset=[-.95,0,0]
    new_chine.name="side"
    new_chine.make_chine()

    new_chine.rotation=[82,0,0]
    #new_chine.offset=[0,0,0]
    new_chine.name="low"
    #new_chine.curve_length=the_hull.hull_length*1.4
#    new_chine.asymmetry[1]=0
    new_chine.make_chine()


    #new_chine.curve_length=the_hull.hull_length*1.1
    new_chine.longitudal_count=0
    new_chine.rotation=[-36,0,0]
    #new_chine.offset=[0.04,0,-0.06]
    new_chine.name="upper"
    #new_chine.curve_length=the_hull.hull_length*1.3
    new_chine.make_chine()



    new_chine.asymmetry[1]=0
    new_chine.rotation=[-90,0,0]
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
[ 1, [6.096892,-5.457021,-0.208632],[1.097236,-0.166389,-0.166539] ],
[ 2, [0.832591,-1.967613,9.744141],[0.000000,0.000000,0.000000] ],
[ 3, [6.916142,-0.764634,0.672572],[-0.018434,0.001545,-0.917216] ],
[ 4, [-6.122976,-4.947592,0.150181],[-0.758119,0.379426,-0.492896] ],
[ 5, [3.023221,-0.004060,-0.149050],[0.990780,0.029352,0] ]
]

render_helper.setup_keyframes(framedata)
