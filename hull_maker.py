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
import math

#from . import curve_helper as curve_helper
curve_helper = imp.load_source('curve_helper','curve_helper.py')

#from . import curve_helper as curve_helper
#from . import material_helper as cumaterial_helperrve_helper
#from . import bulkhead as bulkhead

material_helper = imp.load_source('material_helper','material_helper.py')
bulkhead = imp.load_source('bulkhead','bulkhead.py')


class chine_helper:
    rotation=[0,0,0]
    offset=[0,0,0]
    name="chine_01"
    #curve_twist1=-20
    #curve_twist2=-20
    the_hull=None
    symmetrical=True

    bool_correction_offset=0.02

    curve_length=12
    curve_width=1.2
    extrude_multiplier=2.5

    asymmetry=[0,0]

    longitudal_count=0
    longitudal_height=0.0
    longitudal_thickness=0.3
    longitudal_width=0.5
    longitudal_z_offset=0

    # reference to first chine side
    chine_object_1=None

    # reference to second chine side - if symmetrical this will be None
    chine_object_2=None 

    # view collections
    view_collection_chines=None
    view_collection_longitudals=None
    view_collection_longitudal_slicers=None

    def __init__(self,the_hull):
        self.the_hull=the_hull
        self.bool_correction_offset=the_hull.bool_correction_offset

        self.view_collection_chines=curve_helper.make_collection("chines",bpy.context.scene.collection.children)
        self.view_collection_longitudals=curve_helper.make_collection("longitudals",bpy.context.scene.collection.children)
        self.view_collection_longitudal_slicers=curve_helper.make_collection("longitudal_slicers",bpy.context.scene.collection.children)

        #curve_helper.hide_object(self.view_collection_longitudal_slicers)
 
    # After the boolean operation is complete the vertices can be removed that are on the other side
    # of the plane used for the boolean operation. 
    def delete_back_front(self,ob):
        ob.select_set(state=True)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group="back")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.object.vertex_group_set_active(group="front")
        bpy.ops.object.vertex_group_select()
        bpy.ops.mesh.delete(type='VERT')

    
    # Creates a new plane that will intersect another plane. This new plane will act as the slicer
    # It marks the front and back vertex groups for reference later after boolean operation
    def create_slicer_plane_mesh(self,name,height,z_offset):

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        #slicer_face_overlap=0.007
#        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True, location=(self.bool_correction_offset[0], -slicer_face_overlap-abs(self.bool_correction_offset[1]), self.bool_correction_offset[2]+height-(self.longitudal_thickness/2)))
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True, 
        location=(  self.bool_correction_offset[0], 
                    self.bool_correction_offset[1], 
                    self.bool_correction_offset[2]+height+z_offset))

        bpy.ops.transform.resize(value=(self.curve_length, self.curve_width*5, 1))
        
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



    def make_slicer_plane(self,wall_curve,name,height,thickness,z_offset):

        name_prefix="cutter"
        
        # Add first plane
        slicer1=self.create_slicer_plane_mesh(name_prefix+name+".a",height-(thickness/2),z_offset)
        
        slicer1.select_set(True)
        bpy.context.view_layer.objects.active=slicer1
        
        bool_two = slicer1.modifiers.new(type="BOOLEAN", name="slice")
        bool_two.object = wall_curve
        bool_two.operation = 'DIFFERENCE'
        
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="slice")
        
        self.delete_back_front(slicer1)

        slicer1.select_set(False)
        
        # Add second plane
        slicer2=self.create_slicer_plane_mesh(name_prefix+name+".b",height+(thickness/2),z_offset)

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
        return slicer2

    def make_chine(self,twist=None):

        bpy.ops.object.select_all(action='DESELECT')

        name_prefix="chine_"

        theCurveHelper = curve_helper.Curve_Helper()

        theCurveHelper.asymmetry=self.asymmetry
        theCurveHelper.extrude_multiplier=self.extrude_multiplier


        theCurveHelper.define_curve(self.curve_length,self.curve_width)
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

        theCurveHelper.generate_curve(first_curve_name)
        self.curve_object_1=theCurveHelper.curve_object
        theCurveHelper.convert_to_mesh()
        material_helper.assign_material(self.curve_object_1,material_helper.get_material_bool())
        bpy.ops.transform.translate(value=(self.bool_correction_offset[0], self.bool_correction_offset[1], self.bool_correction_offset[2]))

        if self.longitudal_count>0:
            longitudal_plane=self.make_slicer_plane(self.curve_object_1,self.curve_object_1.name+".longitudal",self.longitudal_height,self.longitudal_thickness,self.longitudal_z_offset)
            longitudal_plane.parent=self.curve_object_1
            material_helper.assign_material(longitudal_plane,material_helper.get_material_bool())
            self.the_hull.longitudal_list.append(longitudal_plane)
            self.select_and_extrude_slicer(longitudal_plane,-self.longitudal_width)
            
            slicer_plane=self.make_slicer_plane(self.curve_object_1,self.curve_object_1.name+".slicer",self.longitudal_height,self.longitudal_thickness*1.5,self.longitudal_z_offset)
            slicer_plane.parent=self.curve_object_1
            self.the_hull.longitudal_slicer_list.append(slicer_plane)
            self.select_and_extrude_slicer(slicer_plane,-self.longitudal_width/2)
            slicer_plane.location.y=-0.005

            curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)
            curve_helper.hide_object(slicer_plane)
            curve_helper.move_object_to_collection(self.view_collection_longitudals,longitudal_plane)
            
        theCurveHelper.extrude_curve(self.curve_object_1)
    
        theCurveHelper.rotate_curve(self.rotation)
        bpy.ops.transform.translate(value=(self.offset[0], self.offset[1], self.offset[2]))
        theCurveHelper.deselect_curve()

        theCurveHelper.add_boolean(self.the_hull.hull_object)


        curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
        #curve_helper.hide_object(theCurveHelper.curve_object)

        curve_helper.hide_object(self.curve_object_1)


        if self.symmetrical:
        # ================================================================================================ 
        # Right Side
        # ================================================================================================

            if twist!=None:
                theCurveHelper.curve_twist[0]=-twist[0]
                theCurveHelper.curve_twist[1]=-twist[1]
                theCurveHelper.curve_twist[2]=-twist[2]

            theCurveHelper.generate_curve(name_prefix+self.name+".R")
            self.curve_object_2=theCurveHelper.curve_object
            theCurveHelper.convert_to_mesh()
            material_helper.assign_material(self.curve_object_2,material_helper.get_material_bool())
            bpy.ops.transform.translate(value=(self.bool_correction_offset[0], self.bool_correction_offset[1], self.bool_correction_offset[2]))

            if self.longitudal_count>0:
                longitudal_plane=self.make_slicer_plane(self.curve_object_2,self.curve_object_2.name+".longitudal",self.longitudal_height,self.longitudal_thickness,-self.longitudal_z_offset)
                longitudal_plane.parent=self.curve_object_2
                material_helper.assign_material(longitudal_plane,material_helper.get_material_bool())

                self.the_hull.longitudal_list.append(longitudal_plane)
                self.select_and_extrude_slicer(longitudal_plane,-self.longitudal_width)
                #bpy.ops.object.mode_set(mode='OBJECT')
                #curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)

                slicer_plane=self.make_slicer_plane(self.curve_object_2,self.curve_object_2.name+".slicer",self.longitudal_height,self.longitudal_thickness*1.5,-self.longitudal_z_offset)
                slicer_plane.parent=self.curve_object_2
                self.the_hull.longitudal_slicer_list.append(slicer_plane)
                self.select_and_extrude_slicer(slicer_plane,-self.longitudal_width/2)
                slicer_plane.location.y=-0.005

                curve_helper.move_object_to_collection(self.view_collection_longitudal_slicers,slicer_plane)
                curve_helper.hide_object(slicer_plane)
                curve_helper.move_object_to_collection(self.view_collection_longitudals,longitudal_plane)

            curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
                
            theCurveHelper.extrude_curve(self.curve_object_2)

            rotation_opposite=[180-self.rotation[0],
                                self.rotation[1],
                                self.rotation[2],
                                ]

            theCurveHelper.rotate_curve(rotation_opposite,flip_z=True)
            bpy.ops.transform.translate(value=(self.offset[0], -self.offset[1], self.offset[2]))
            theCurveHelper.deselect_curve()
            theCurveHelper.add_boolean(self.the_hull.hull_object)
            
            curve_helper.move_object_to_collection(self.view_collection_chines,theCurveHelper.curve_object)
            curve_helper.hide_object(theCurveHelper.curve_object)

            curve_helper.hide_object(self.curve_object_2)

class hull_maker:
    hull_length=11.4
    hull_width=3.9
    hull_height=3.6
    hull_name="hull_object"
    hull_object=None

    longitudal_list=None
    longitudal_slicer_list=None

    bulkheadlist=[]

    #bool_correction_offset=[ 0.0011, 0.0012, 0.0013 ]
    bool_correction_offset=[ 0.00, 0.00, 0.00 ]

    chine_list=None

    def __init__(self,length=11.4,width=3.9,height=3.6):
        self.hull_height=height
        self.hull_length=length
        self.hull_width=width
        chine_list=list()

        self.longitudal_list=list()
        self.longitudal_slicer_list=list()



    def make_bool_cube(self,name,location=(0,0,0),size=(1,1,1)):

        curve_helper.find_and_remove_object_by_name(name)

        # Booleans behave really strange if origin is 0,0,0 - this works
        #bpy.ops.mesh.primitive_cube_add(size=1.0,enter_editmode=False, location=(0.02, 0.02, 0.02))
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(self.bool_correction_offset[0]+location[0], self.bool_correction_offset[1]+location[1], self.bool_correction_offset[2]))

        new_object=bpy.context.view_layer.objects.active

        bpy.ops.transform.resize(value=size)
        bpy.ops.object.transform_apply(scale=True,location=False)

        new_object.name=name

        return new_object

    def make_hull_object(self):
        self.hull_object=self.make_bool_cube(self.hull_name,size=(self.hull_length, self.hull_width, self.hull_height))

        material_helper.assign_material(self.hull_object,material_helper.get_material_hull())

        return self.hull_object

    def make_bulkheads(self,bulkhead_definitions):
        for station_position in bulkhead_definitions:
            bh=bulkhead.bulkhead(self,station_position[0])
            bh.make_bulkhead(station_position[2])

            # If it's not watertight - there is a void in middle
            if station_position[2]==False:
                material_helper.assign_material(bh.bulkhead_void_object,material_helper.get_material_bool())
                if station_position[1]!=False:
                    bh.move_verts_z(bh.bulkhead_void_object,station_position[1])

            self.bulkheadlist.append(bh)

            material_helper.assign_material(bh.bulkhead_object,material_helper.get_material_bulkhead())

            if bh.bulkhead_void_object!=None:
                curve_helper.select_object(bh.bulkhead_void_object,True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')
            

            curve_helper.select_object(bh.bulkhead_object,True)

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')



    def make_longitudal_booleans(self):
        for lg in self.longitudal_slicer_list:

            material_helper.assign_material(lg,material_helper.get_material_stringer())
            
            for bh in self.bulkheadlist:
                modifier=bh.bulkhead_object.modifiers.new(name="bool_slicer", type='BOOLEAN')
                modifier.object=lg
                modifier.operation="DIFFERENCE"
                modifier.double_threshold=0

        for lg in self.longitudal_list:
            material_helper.assign_material(lg,material_helper.get_material_support())

            for bh in self.bulkheadlist:
                modifier=lg.modifiers.new(name="bool_bh", type='BOOLEAN')
                modifier.object=bh.bulkhead_object
                modifier.operation="DIFFERENCE"



    def cleanup_longitudal_ends(self,x_locations):

        view_collection_cleaner=curve_helper.make_collection("cleaner",bpy.context.scene.collection.children)

        end_clean_list=[]

        for index,x_location in enumerate(x_locations):
            # =========================================
            # Clean up ends of longitudal slicers

            block_width=self.hull_width

            adjusted_location=x_location
            if adjusted_location<0:
                adjusted_location=adjusted_location-block_width/2

            if adjusted_location>0:
                adjusted_location=adjusted_location+block_width/2

            object_end_clean = self.make_bool_cube("end_clean_%s"%index,location=[adjusted_location,0,0],size=(block_width,block_width,self.hull_height))

            curve_helper.move_object_to_collection(view_collection_cleaner,object_end_clean)

            material_helper.assign_material(object_end_clean,material_helper.get_material_bool())
            end_clean_list.append(object_end_clean)

        # ===================================================================

        for lg in self.longitudal_list:

            for object_end_clean in end_clean_list:		
                modifier=lg.modifiers.new(name="bool", type='BOOLEAN')
                modifier.object=object_end_clean
                modifier.operation="DIFFERENCE"
                modifier.double_threshold=0
                curve_helper.hide_object(object_end_clean)

        #curve_helper.hide_object(view_collection_cleaner)
