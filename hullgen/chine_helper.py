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
from math import radians, degrees

from ..hullgen import curve_helper
from ..hullgen import material_helper

class chine_helper:
    rotation=[0,0,0]
    offset=[0,0,0]
    name="chine_01"
    #curve_twist1=-20
    #curve_twist2=-20
    the_hull=None
    symmetrical=True

    bool_correction_offset=0

    curve_length=12
    curve_width=1.2

    curve_height=1

    extrude_width=1

    asymmetry=[0,0]

    longitudal_count=0
    longitudal_height=0
    longitudal_thickness=0.05
    longitudal_width=-0.15
    longitudal_z_offset=0

    longitudal_bend_radius=0
    longitudal_curve_angle=0


    # how much wider the slicers will be than the longitudals - value of 1.1 means notches will be 110 percent of longitudal
    slicer_overcut=1.1

    # ratio of longitudal to slicer means how high the slicers are in relation to longitudals
    # If it's 0.5 it will be half - it affects the notches height for bulkheads 
    slicer_longitudal_ratio=0.5

    # amount of distance slicer is poking through skin to ensure clean geometry
    skin_pokethrough=0.01

    # reference to first chine side
    chine_object_1=None

    # reference to second chine side - if symmetrical this will be None
    chine_object_2=None 

    # view collections
    view_collection_chines=None
    view_collection_longitudals=None
    view_collection_longitudal_slicers=None

    def set_longitudal_curve(self,radius,angle):
        self.longitudal_curve_angle=angle
        self.longitudal_bend_radius=radius

    def __init__(self,the_hull):
        self.the_hull=the_hull

        self.longitudal_thickness=the_hull.structural_thickness
        
        self.bool_correction_offset=the_hull.bool_correction_offset

        self.curve_height=the_hull.hull_height
        self.extrude_width=the_hull.hull_height*3

        self.view_collection_chines=curve_helper.make_collection("chines",bpy.context.scene.collection.children)
        self.view_collection_longitudals=curve_helper.make_collection("longitudals",bpy.context.scene.collection.children)
        self.view_collection_longitudal_slicers=curve_helper.make_collection("longitudal_slicers",bpy.context.scene.collection.children)
 
    # After the boolean operation is complete the vertices can be removed that are on the other side
    # of the plane used for the boolean operation. 
    def delete_back_front(self,ob):
        ob.select_set(state=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group="back")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group="front")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')

    
    # Creates a new plane that will intersect another plane. This new plane will act as the slicer
    # It marks the front and back vertex groups for reference later after boolean operation
    def create_slicer_plane_mesh(self,name,height,inverted_curves):

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        theCurveHelper = curve_helper.Curve_Helper()

        curve_angle=0
        bend_radius=0

        if inverted_curves:
            curve_angle=-self.longitudal_curve_angle
            bend_radius=-self.longitudal_bend_radius
        else:
            curve_angle=self.longitudal_curve_angle
            bend_radius=self.longitudal_bend_radius
        
        theCurveHelper.curve_angle=curve_angle

        theCurveHelper.define_curve(self.curve_length,bend_radius)
        theCurveHelper.curve_height=0

        theCurveHelper.generate_curve(name)

        bpy.ops.transform.rotate(value=radians(90),orient_axis='X')
        bpy.ops.object.transform_apply(rotation=True,scale=False,location=False)

        newCurve=theCurveHelper.curve_object

        curve_helper.select_object(newCurve,True)

        bpy.ops.object.mode_set(mode='EDIT')

        # extrude thicknes along Y axis
        bpy.ops.mesh.select_all(action='SELECT')
        #bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,self.curve_width*5,0), 
                                        "constraint_axis":(False, False,True)})
        
        bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')

        group = newCurve.vertex_groups.new()
        group.name = "back"

        # for some reason vector math type if vert.co.y==0 equals false negative because of some rounding issue so I'm using -1 as cutoff for comparison

        verts = []
        for vert in newCurve.data.vertices:
            #print("%f %f %f"%(vert.co.x,vert.co.y,vert.co.z))
            if vert.co.y>-1:
                verts.append(vert.index)
            
        group.add(verts, 1.0, 'ADD')

        group = bpy.context.object.vertex_groups.new()
        group.name = "front"

        verts = []
        for vert in newCurve.data.vertices:
            if vert.co[1]<-1:
                verts.append(vert.index)

        group.add(verts, 1.0, 'ADD')

        

        #bpy.ops.transform.rotate(value=radians(90),orient_axis='X')
        #bpy.ops.object.transform_apply(rotation=True,scale=False,location=False)
        
        newCurve.location.z=height
        newCurve.location.y=-self.curve_width*5/2

        #theCurveHelper.extrude_curve(newCurve)
        #bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})

        bpy.ops.object.select_all(action='DESELECT')

        return newCurve

            
    # =====================================

    def select_and_extrude_slicer(self,slicer,amount):
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
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')


    # for symmetrical chines - if there is any curve in slicer plane - it needs to be inverted for opposite side (symmetrical)
    def make_slicer_plane(self,wall_curve,name,height,thickness,z_offset,inverted_curves=False):

        name_prefix="cutter"

        # Add first plane
        slicer1=self.create_slicer_plane_mesh(name_prefix+name+".a",height+(thickness/2)+z_offset,inverted_curves)
        
        slicer1.select_set(True)
        bpy.context.view_layer.objects.active=slicer1
        
        bool_two = slicer1.modifiers.new(type="BOOLEAN", name="slice")
        bool_two.object = wall_curve
        bool_two.operation = 'DIFFERENCE'
        
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="slice")
        
        self.delete_back_front(slicer1)

        slicer1.select_set(False)
        
        # Add second plane
        slicer2=self.create_slicer_plane_mesh(name_prefix+name+".b",height-(thickness/2)+z_offset,inverted_curves)
   
        slicer2.select_set(True)
        
        bpy.context.view_layer.objects.active=slicer2
        
        bool_two = slicer2.modifiers.new(type="BOOLEAN", name="slice")
        bool_two.object = wall_curve
        bool_two.operation = 'DIFFERENCE'

        bpy.context.view_layer.objects.active=slicer2
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="slice")
   
        
        self.delete_back_front(slicer2)

        bpy.ops.object.mode_set(mode='OBJECT')

        slicer1.select_set(True)
        slicer2.select_set(True)

        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        

        bpy.ops.mesh.bridge_edge_loops()
        
        bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.ops.mesh.select_all(action='DESELECT')
        
        # second object selected is left over after join
        slicer2.name=name_prefix+name


        #bpy.ops.object.transform_apply(rotation=False,scale=False,location=True)
        return slicer2

    def make_chine(self,twist=None):

        bpy.ops.object.select_all(action='DESELECT')

        name_prefix="chine_"

        theCurveHelper = curve_helper.Curve_Helper()

        theCurveHelper.asymmetry=self.asymmetry

        #theCurveHelper.define_curve(self.curve_length,self.curve_width)

        # ================================================================================================ 
        # First curve is Left Side or non-symmetrical "single side"
        # ================================================================================================
        first_curve_name=name_prefix+self.name

        if self.symmetrical:
            first_curve_name+=".L"

        if twist!=None:
            theCurveHelper.curve_twist[0]=twist[0]
            theCurveHelper.curve_twist[1]=twist[1]
            theCurveHelper.curve_twist[2]=twist[2]

        theCurveHelper.define_curve(length=self.curve_length,width=self.curve_width)
        theCurveHelper.curve_height=self.curve_height
        theCurveHelper.generate_curve(first_curve_name)

        self.curve_object_1=theCurveHelper.curve_object

        material_helper.assign_material(self.curve_object_1,material_helper.get_material_bool())
        bpy.ops.transform.translate(value=(self.bool_correction_offset[0], self.bool_correction_offset[1], self.bool_correction_offset[2]))

        if self.longitudal_count>0:

            longitudal_plane=self.make_slicer_plane(
                self.curve_object_1,
                self.curve_object_1.name+".longitudal",
                self.longitudal_height,
                self.longitudal_thickness,
                self.longitudal_z_offset,
                False)

            longitudal_plane.parent=self.curve_object_1
            material_helper.assign_material(longitudal_plane,material_helper.get_material_stringer())
            self.the_hull.longitudal_list.append(longitudal_plane)
            self.select_and_extrude_slicer(longitudal_plane,-self.longitudal_width)
            
            slicer_plane=self.make_slicer_plane(
                self.curve_object_1,
                self.curve_object_1.name+".slicer",
                self.longitudal_height,
                self.longitudal_thickness*self.slicer_overcut,
                self.longitudal_z_offset,
                False)

            slicer_plane.parent=longitudal_plane
            material_helper.assign_material(slicer_plane,material_helper.get_material_support())
            self.the_hull.longitudal_slicer_list.append(slicer_plane)
            self.select_and_extrude_slicer(slicer_plane,-self.longitudal_width*self.slicer_longitudal_ratio)

            if self.curve_width<0:
                slicer_plane.location.y=self.skin_pokethrough
            else:
                slicer_plane.location.y=-self.skin_pokethrough

            # for some reason bool doesn't work if X is 0 on parent object... maybe bug in blender boolean code
            slicer_plane.location.x=0.0001
            slicer_plane.location.z=- ( (self.longitudal_thickness*self.slicer_overcut)-self.longitudal_thickness ) / 2

            curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)
            curve_helper.hide_object(slicer_plane)
            curve_helper.move_object_to_collection(self.view_collection_longitudals,longitudal_plane)
        
        curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
        theCurveHelper.extrude_curve(self.extrude_width)
        
        theCurveHelper.rotate_curve(self.rotation)
        bpy.ops.transform.translate(value=(self.offset[0], self.offset[1], self.offset[2]))
        theCurveHelper.deselect_curve()
        
        theCurveHelper.add_boolean(self.the_hull.hull_object)

        curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
        curve_helper.hide_object(theCurveHelper.curve_object)

        curve_helper.hide_object(self.curve_object_1)


        if self.symmetrical:
        # ================================================================================================ 
        # Right Side
        # ================================================================================================

            if twist!=None:
                theCurveHelper.curve_twist[0]=-twist[0]
                theCurveHelper.curve_twist[1]=-twist[1]
                theCurveHelper.curve_twist[2]=-twist[2]

            theCurveHelper.define_curve(length=self.curve_length,width=self.curve_width)
            theCurveHelper.curve_height=self.curve_height
            theCurveHelper.generate_curve(name_prefix+self.name+".R")
            self.curve_object_2=theCurveHelper.curve_object

            material_helper.assign_material(self.curve_object_2,material_helper.get_material_bool())
            bpy.ops.transform.translate(value=(self.bool_correction_offset[0], self.bool_correction_offset[1], self.bool_correction_offset[2]))

            if self.longitudal_count>0:

                longitudal_plane=self.make_slicer_plane(
                    self.curve_object_2,
                    self.curve_object_2.name+".longitudal",
                    self.longitudal_height,
                    self.longitudal_thickness,
                    -self.longitudal_z_offset,
                    True)

                longitudal_plane.parent=self.curve_object_2
                material_helper.assign_material(longitudal_plane,material_helper.get_material_stringer())
                self.the_hull.longitudal_list.append(longitudal_plane)
               
                self.select_and_extrude_slicer(longitudal_plane,-self.longitudal_width)
                #longitudal_plane.rotation.y=180
                #curve_helper.select_object(longitudal_plane,True)
                #bpy.ops.transform.rotate(value=radians(180),orient_axis='Y')
                #bpy.ops.object.mode_set(mode='OBJECT')
                #curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)

                slicer_plane=self.make_slicer_plane(
                    self.curve_object_2,
                    self.curve_object_2.name+".slicer",
                    self.longitudal_height,
                    self.longitudal_thickness*self.slicer_overcut,
                    -self.longitudal_z_offset,
                    True)

                slicer_plane.parent=longitudal_plane
                material_helper.assign_material(slicer_plane,material_helper.get_material_support())
                self.the_hull.longitudal_slicer_list.append(slicer_plane)
                self.select_and_extrude_slicer(slicer_plane,-self.longitudal_width*self.slicer_longitudal_ratio)
                #curve_helper.select_object(slicer_plane,True)
                #bpy.ops.transform.rotate(value=radians(180),orient_axis='Y')

                if self.curve_width<0:
                    slicer_plane.location.y=self.skin_pokethrough
                else:
                    slicer_plane.location.y=-self.skin_pokethrough

                # for some reason bool doesn't work if X is 0 on parent object... maybe bug in blender boolean code
                slicer_plane.location.x=0.0001
                slicer_plane.location.z=- ( (self.longitudal_thickness*self.slicer_overcut)-self.longitudal_thickness ) / 2

                curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)
                curve_helper.hide_object(slicer_plane)
                curve_helper.move_object_to_collection(self.view_collection_longitudals,longitudal_plane)

            curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)        
            theCurveHelper.extrude_curve(self.extrude_width)

            rotation_opposite=[180-self.rotation[0],
                                self.rotation[1],
                                self.rotation[2],
                                ]

            theCurveHelper.rotate_curve(rotation_opposite,flip_z=False)
            bpy.ops.transform.translate(value=(self.offset[0], -self.offset[1], self.offset[2]))
            theCurveHelper.deselect_curve()
            theCurveHelper.add_boolean(self.the_hull.hull_object)
            
            curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
            curve_helper.hide_object(theCurveHelper.curve_object)

            curve_helper.hide_object(self.curve_object_2)

            
