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
import imp   
 
curve_helper = imp.load_source('util_lux','curve_helper.py')

theCurveHelper = curve_helper.Curve_Helper()

theCurveHelper.curve_angle=40

for width in curve_helper.frange(0.1,1,0.1):
    theCurveHelper.define_curve(10,width)
    theCurveHelper.generate_curve("curve_width_%1.2f"%width)
    theCurveHelper.curve_object.location.y=-width
    theCurveHelper.curve_object.location.z=width/3
    wireframe = theCurveHelper.curve_object.modifiers.new(type="SOLIDIFY", name="solid")
    print("Width: %1.2f"%width)

theCurveHelper.curve_angle=-40

for length in curve_helper.frange(1,10,1):
    theCurveHelper.define_curve(length,-1)
    theCurveHelper.generate_curve("curve_length_%1.2f"%length)
    theCurveHelper.curve_object.location.y=length/20
    theCurveHelper.curve_object.location.z=length/30
    wireframe = theCurveHelper.curve_object.modifiers.new(type="SOLIDIFY", name="solid")
    print("Length: %1.2f"%length)
