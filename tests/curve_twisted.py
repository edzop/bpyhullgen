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
   
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import render_helper

theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.curve_twist[0]=12
theCurveHelper.curve_twist[1]=6

theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("curvetest")
theCurveHelper.extrude_curve(1)

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")

info_text="A 3D curve with twist on the third axis"
geometry_helper.add_info_text(info_text)

framedata=[
[ 1, [0.000000,-1.362492,27.603287],[0.000000,0.196316,-0.509545] ],
[ 2, [19.154360,5.335245,12.450815],[1.170676,-0.401701,-0.356683] ]
]

render_helper.setup_keyframes(framedata)
