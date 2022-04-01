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

from ..hullgen import curve_helper
from ..bpyutils import bpy_helper

class bulkhead_definition:
    station=0
    watertight=False
    floor_height=0
    thickness=0.1

    def __init__(self,station,watertight,floor_height,thickness):
        self.station=station
        self.watertight=watertight
        self.floor_height=floor_height
        self.thickness=thickness

class bulkhead:

    the_hull_definition=None

    bulkhead_object=None

    bulkhead_overcut_object=None

    bulkhead_floor_object=None
    bulkhead_collection=None
    #bulkhead_void_collection=None
    bulkhead_definition=None


    def __init__(self,the_hull_definition,bulkhead_definition):
        self.bulkhead_definition=bulkhead_definition

        self.the_hull_definition=the_hull_definition
        self.bulkhead_collection=bpy_helper.make_collection("bulkheads",bpy.context.scene.collection.children)

    def move_verts_z(self,ob,new_val):

        vert_list=[]

        for v in ob.data.vertices:
            
            vert_list.append([v.index,v.co.z])
            
            

        def secondVal(val):
            return val[1]

        vert_list.sort(key=secondVal)

        mat_world = ob.matrix_world

            
        for i in range(0,len(vert_list)):

            vert=ob.data.vertices[vert_list[i][0]].co
            
            pos_world = mat_world @ vert
            
            if pos_world.z<new_val:
                pos_world.z=new_val
            
            new_vert=mat_world.inverted() @ pos_world
            
            vert.z=new_vert.z
        

    def make_bulkhead(self):
        bpy.ops.mesh.primitive_cube_add(size=2.0, 
            enter_editmode=False, 
            location=(  self.bulkhead_definition.station, 0, 0))

        bpy.ops.transform.resize(value=(self.bulkhead_definition.thickness/2, self.the_hull_definition.hull_width, self.the_hull_definition.hull_height))
        bpy.ops.object.transform_apply(scale=True)
        
        self.bulkhead_object=bpy.context.view_layer.objects.active
        self.bulkhead_object.name="Bulkhead.s%06.2f"%(self.bulkhead_definition.station)

        bpy_helper.select_object(self.bulkhead_object,True)

        bool_new = self.bulkhead_object.modifiers.new(type="BOOLEAN", name="hull_slice")
        bool_new.object = self.the_hull_definition.hull_object
        bool_new.operation = 'INTERSECT'
        bool_new.name="bool.hull_shape"

        bpy.ops.object.modifier_apply(modifier="bool.hull_shape")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        if self.the_hull_definition.slicer_overcut_ratio>0:
            
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, 
				TRANSFORM_OT_translate={"value":(0, 0, 0)})

            self.bulkhead_overcut_object=bpy.context.view_layer.objects.active
            self.bulkhead_overcut_object.name="Bulkhead.s%06.2f_overcut"%(self.bulkhead_definition.station)

            #self.bulkhead_overcut_object.parent=self.bulkhead_object


            #bpy_helper.parent_objects_keep_transform(self.bulkhead_object,self.bulkhead_overcut_object)

            bpy_helper.select_object(self.bulkhead_overcut_object,True)

            #self.bulkhead_overcut_object.parent=self.bulkhead_object
            bpy.ops.transform.resize(value=[self.the_hull_definition.slicer_overcut_ratio,1,1])

            bpy_helper.move_object_to_collection(self.bulkhead_collection,self.bulkhead_overcut_object)

        bpy_helper.select_object(self.bulkhead_object,True)


        bpy_helper.move_object_to_collection(self.bulkhead_collection,self.bulkhead_object)

        return self.bulkhead_object
