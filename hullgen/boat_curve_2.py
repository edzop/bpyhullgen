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

from ..hullgen import curve_helper

def make_rounded(ob):
    bpy.context.view_layer.objects.active=ob
    bpy.ops.object.modifier_add(type='BEVEL')
    bpy.context.object.modifiers["Bevel"].width = 0.01
    bpy.context.object.modifiers["Bevel"].segments = 2
    bpy.ops.object.modifier_add(type='SUBSURF')



# Creates a new plane that will intersect another plane. This new plane will act as the slicer
# It marks the front and back vertex groups for reference later after boolean operation
def create_slicer_plane_mesh(name,height):

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, location=(0, 0, height))

    ob = bpy.context.active_object

    ob.name=name

    # must be in object mode to select vertices by index
    bpy.ops.object.mode_set(mode='OBJECT')
        
    group = bpy.context.object.vertex_groups.new()
    group.name = "back"
    group.add([0,1], 1.0, 'ADD')

    group = bpy.context.object.vertex_groups.new()
    group.name = "front"
    group.add([2,3], 1.0, 'ADD')
    return ob

# After the boolean operation is complete the vertices can be removed that are on the other side
# of the plane used for the boolean operation. 
def delete_back_front(ob):
    ob.select_set(state=True)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_set_active(group="back")
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.delete(type='VERT')

    bpy.ops.object.vertex_group_set_active(group="front")
    bpy.ops.object.vertex_group_select()
    bpy.ops.mesh.delete(type='VERT')
    
def make_slicer_plane(wall_curve,name,height,thickness):
    
    # Add first plane
    slicer1=create_slicer_plane_mesh(name,height)

    slicer1.select_set(True)
    bpy.context.view_layer.objects.active=slicer1

    bool_two = slicer1.modifiers.new(type="BOOLEAN", name="slice")
    bool_two.object = wall_curve
    bool_two.operation = 'DIFFERENCE'

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="slice")
    delete_back_front(slicer1)

    slicer1.select_set(False)

    # Add second plane
    slicer2=create_slicer_plane_mesh(name,height+thickness)

    slicer2.select_set(True)
    bpy.context.view_layer.objects.active=slicer2

    bool_two = slicer2.modifiers.new(type="BOOLEAN", name="slice")
    bool_two.object = wall_curve
    bool_two.operation = 'DIFFERENCE'

    bpy.context.view_layer.objects.active=slicer2
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="slice")
    delete_back_front(slicer2)

    bpy.ops.object.mode_set(mode='OBJECT')

    slicer1.select_set(True)
    slicer2.select_set(True)

    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bridge_edge_loops()

    bpy.ops.object.mode_set(mode='OBJECT')

    # second object selected is left over after join
    slicer2.name=name
    return slicer2

def makecurve(curve_name,thickness,height,h_offset,v_offset):
    bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
    
    bez_curve = bpy.context.active_object
    bez_curve.name=curve_name
    curve_data=bez_curve.data

    curve_data.resolution_u = 64
    curve_data.render_resolution_u = 64
    curve_data.extrude=height

    bez_points = bez_curve.data.splines[0].bezier_points
    bez_points[1].tilt=math.radians(40)
    #TODO degrees to radians for tilt
        
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.convert(target='MESH', keep_original=False)
    bpy.ops.object.shade_flat()

    mesh_object = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')
    
    # extrude thicknes along Y axis
    #bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, thickness, 0), 
    #                                "constraint_axis":(False, True, False)})

    # extrude height along Z axis
    #bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height), 
    #                                "constraint_axis":(False, False, True)})

    # offset along Y axis for shift
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(0, h_offset, v_offset))

    bpy.ops.object.mode_set(mode='OBJECT')
    
#    bpy.ops.object.modifier_add(type='BEVEL')
#    bpy.context.object.modifiers["Bevel"].width = 0.01
#    bpy.ops.object.modifier_add(type='SUBSURF')
    
    return mesh_object

wall_height=0.6
support_height=0.1

def select_and_extrude_slicer(slicer,amount):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = slicer
    slicer.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    # extrude thicknes along Y axis
    bpy.ops.mesh.select_all(action='SELECT')
    #bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, amount, 0), 
                                    "constraint_axis":(False, True, False)})
