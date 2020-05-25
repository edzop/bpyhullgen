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

from math import radians

from ..hullgen import curve_helper

class keel:
    lateral_offset=0
    top_height=0
    the_hull_definition=None
    thickness=0.1
    keel_object=None
    keel_collection=None
    station_start=0
    station_end=1

    
    slicer_cut_height=0.2

    keel_slicer_object=None
    keel_slicer_collection=None

    def __init__(self,the_hull_definition,lateral_offset,top_height,station_start,station_end):
        self.lateral_offset=lateral_offset
        self.top_height=top_height
        self.the_hull_definition=the_hull_definition
        self.keel_collection=curve_helper.make_collection("keels",bpy.context.scene.collection.children)
        self.station_start=station_start
        self.station_end=station_end

        self.thickness=the_hull_definition.structural_thickness

        #curve_helper.hide_object(self.bulkhead_void_collection)


    def make_keel(self,slicer_cut_height=0.2):
        cube_size=1.0
        self.slicer_cut_height=slicer_cut_height

        thickness_shift=0

        if self.lateral_offset>0:
            thickness_shift=self.thickness
        else:
            thickness_shift=-self.thickness

        keel_length=self.station_end-self.station_start

        bpy.ops.mesh.primitive_plane_add(size=cube_size, 
            enter_editmode=False, 
            location=(  self.station_start+keel_length/2+self.the_hull_definition.bool_correction_offset[0], 
                        self.the_hull_definition.bool_correction_offset[1]+self.lateral_offset+thickness_shift/2, 
                        self.the_hull_definition.bool_correction_offset[2]+self.top_height))

        #bpy.ops.mesh.primitive_cube_add(size=cube_size, 
        #    enter_editmode=False, 
        #    location=(  self.the_hull_definition.bool_correction_offset[0], 
        #                self.the_hull_definition.bool_correction_offset[1]+self.lateral_offset, 
        #                self.the_hull_definition.bool_correction_offset[2]+self.top_height))
        bpy.ops.transform.rotate(value=radians(90),orient_axis='X')

        bpy.ops.transform.resize(value=(keel_length, 
                                0, 
                                self.the_hull_definition.hull_height))

        bpy.ops.transform.translate(value=(0,0,-self.the_hull_definition.hull_height/2))

        bpy.ops.object.transform_apply(scale=True,location=False)
        
        self.keel_object=bpy.context.view_layer.objects.active
        self.keel_object.name="Keel.s%0.2f"%(self.lateral_offset)


        curve_helper.select_object(self.keel_object,True)
        curve_helper.move_object_to_collection(self.keel_collection,self.keel_object)

        bool_new = self.keel_object.modifiers.new(type="BOOLEAN", name="bool.hull_shape")
        bool_new.object = self.the_hull_definition.hull_object
        bool_new.operation = 'INTERSECT'

        curve_helper.select_object(self.keel_object,True)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bool_new.name)

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        modifier=self.keel_object.modifiers.new(name="solidify", type='SOLIDIFY')
        modifier.thickness=thickness_shift
        #bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)

        # Make Keel Slicer for notches
        bpy.ops.mesh.primitive_cube_add(size=cube_size, 
            enter_editmode=False, 
            location=(  self.station_start+keel_length/2+self.the_hull_definition.bool_correction_offset[0], 
                        self.the_hull_definition.bool_correction_offset[1]+self.lateral_offset, 
                        self.the_hull_definition.bool_correction_offset[2]+self.top_height))
        
        # shift down a smidge to compensate for boolean coplanar faces bug
        # maybe this bug will be fixed with blender > 2.83 bool rewrite
        bool_coplanar_edge_fix=0.01

        bpy.ops.transform.resize(value=(keel_length, 
                                self.thickness+bool_coplanar_edge_fix, 
                                self.the_hull_definition.hull_height))

        bpy.ops.transform.translate(value=(0,0,-self.the_hull_definition.hull_height/2-(self.slicer_cut_height)))

        bpy.ops.object.transform_apply(scale=True,location=False)
        
        self.keel_slicer_object=bpy.context.view_layer.objects.active
        self.keel_slicer_object.name="Keel_Slicer.s%0.2f"%(self.lateral_offset)
        self.keel_slicer_object.display_type="WIRE"
        self.keel_slicer_object.hide_render = True
        self.keel_slicer_object.hide_viewport = True

        curve_helper.select_object(self.keel_slicer_object,True)
        curve_helper.move_object_to_collection(self.keel_collection,self.keel_slicer_object)


        bool_new = self.keel_slicer_object.modifiers.new(type="BOOLEAN", name="bool.hull_shape")
        bool_new.object = self.the_hull_definition.hull_object
        bool_new.operation = 'INTERSECT'

        curve_helper.select_object(self.keel_slicer_object,True)
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=bool_new.name)

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        
        bpy.ops.transform.translate(value=(0,0,-bool_coplanar_edge_fix))

        return self.keel_object
