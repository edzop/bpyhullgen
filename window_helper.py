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

import math


def calc_arc_point_ellipse(centerpoint,angle,distance):
    x= (distance[0]/2) * math.sin(math.radians(angle))
    y= (distance[1]/2) * math.cos(math.radians(angle))

    return (x,y)

def calc_arc_point_circle(centerpoint,angle,distance):
    x= (distance/2) * math.sin(math.radians(angle))
    y= (distance/2) * math.cos(math.radians(angle))

    return (x,y)

def make_circle(name,centerpoint,diameter):
    bpy.ops.mesh.primitive_cylinder_add(radius=diameter, depth=0.4, enter_editmode=False, location=centerpoint)
    new_object=bpy.context.view_layer.objects.active
    new_object.name=name
    return new_object

    
def make_window(centerpoint,diameter):


    ellipse_ratio=2

    main_circle=make_circle("main_window",centerpoint,diameter)

    bpy.ops.transform.resize(value=(ellipse_ratio, 1, 1), 
        constraint_axis=(True, True, False))

    bpy.ops.object.transform_apply(rotation=False,scale=True,location=False)
    
    bolt_diameter=diameter*0.1

    bolt_margin=diameter*0.4
    
    for a in range(0,360,30):

        arc_point=calc_arc_point_ellipse(centerpoint,a,
            [diameter*2*ellipse_ratio+bolt_margin,diameter*2+bolt_margin]
            )
        bolt_hole=make_circle("bolt",(arc_point[0],arc_point[1],centerpoint[2]),bolt_diameter)
        bolt_hole.parent=main_circle


