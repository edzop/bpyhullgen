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
from ..hullgen import bpy_helper

class bulkhead:
    station=0
    the_hull_definition=None
    thickness=0.05
    bulkhead_object=None
    bulkhead_void_object=None
    bulkhead_collection=None
    bulkhead_void_collection=None
    watertight=False

    def __init__(self,the_hull_definition,station,watertight=False,thickness=0.05):
        self.station=station
        self.thickness=thickness
        self.watertight=watertight

        self.the_hull_definition=the_hull_definition
        self.bulkhead_collection=bpy_helper.make_collection("bulkheads",bpy.context.scene.collection.children)
        self.bulkhead_void_collection=bpy_helper.make_collection("bulkhead_void",bpy.context.scene.collection.children)

        #bpy_helper.hide_object(self.bulkhead_void_collection)

    def move_verts_z(self,ob,new_val):

        vert_list=[]

        for v in ob.data.vertices:
            #print(v.index)  
            #print(v.co.z)
            
            vert_list.append([v.index,v.co.z])
            
    #    print("presort")
    #    for v in vert_list:
    #        print("%d %f" % (v[0],v[1]))
            

        def secondVal(val):
            return val[1]

        vert_list.sort(key=secondVal)

    #    print("postsort")
    #    for v in vert_list:
    #        print("%d %f" % (v[0],v[1]))

        mat_world = ob.matrix_world
        #print("world: %s"%mat_world)
            
        for i in range(0,len(vert_list)):
    #    for i in range(0,filter_lowest):
            #print(" ")
            vert=ob.data.vertices[vert_list[i][0]].co
            #print("vert %d: %s"%(i,vert_list[i]))
            #vert.z=0
            
            pos_world = mat_world @ vert
            #print("world original: %s"%pos_world)
            
            if pos_world.z<new_val:
                pos_world.z=new_val
            #print("world modified: %s"%pos_world)
            
            new_vert=mat_world.inverted() @ pos_world
            #print("new_vert modified: %s"%new_vert)
            
            vert.z=new_vert.z
            #vert.x=new_vert.x
            #vert.y=new_vert.y
            
            #print("vert modified: %s"%vert)
        

    def make_bulkhead(self):
        bpy.ops.mesh.primitive_cube_add(size=2.0, 
            enter_editmode=False, 
            location=(  self.the_hull_definition.bool_correction_offset[0]+self.station, 
                        self.the_hull_definition.bool_correction_offset[1], 
                        self.the_hull_definition.bool_correction_offset[2]))

        bpy.ops.transform.resize(value=(self.thickness/2, self.the_hull_definition.hull_width, self.the_hull_definition.hull_height))
        bpy.ops.object.transform_apply(scale=True)
        
        self.bulkhead_object=bpy.context.view_layer.objects.active
        self.bulkhead_object.name="Bulkhead.s%06.2f"%(self.station)

        bpy_helper.select_object(self.bulkhead_object,True)

        bool_new = self.bulkhead_object.modifiers.new(type="BOOLEAN", name="slice")
        bool_new.object = self.the_hull_definition.hull_object
        bool_new.operation = 'INTERSECT'
        bool_new.name="bool.hull_shape"

        bpy.ops.object.modifier_apply(modifier="bool.hull_shape")

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.object.mode_set(mode='OBJECT')


        if self.watertight==False:

            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, 
                                            TRANSFORM_OT_translate={"value":(0, 0, 0)})

            self.bulkhead_void_object=bpy.context.view_layer.objects.active

            bpy_helper.select_object(self.bulkhead_void_object,True)

            

            self.bulkhead_void_object.name="Bulkhead.s%06.2f_void"%(self.station)

            mod_remesh = self.bulkhead_void_object.modifiers.new(type="REMESH", name="remesh")
            mod_remesh.mode = 'SHARP'
            mod_remesh.octree_depth = 4
            mod_remesh.scale = 0.99
            bpy.ops.object.modifier_apply(modifier="remesh")


            # get truple of current size
            bulkhead_size=self.bulkhead_void_object.dimensions.xyz

            if bulkhead_size[0]==0 or bulkhead_size[1]==0 or bulkhead_size[2]==0:
                print("Something went wrong... bulkhead size==0")
                return None

            minimum_support_size=0.2
            rescale_factor=[1,1,1]

            rescale_factor[0]=1.3
            rescale_factor[1]=(bulkhead_size[1]-(minimum_support_size*2))*1/bulkhead_size[1]
            rescale_factor[2]=(bulkhead_size[2]-(minimum_support_size*2))*1/bulkhead_size[2]

            bpy.ops.transform.resize(value=rescale_factor)

            bpy.ops.object.transform_apply(scale=True)

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

            bpy_helper.select_object(self.bulkhead_object,True)

            bool_void = self.bulkhead_object.modifiers.new(type="BOOLEAN", name="void.center")
            bool_void.object = self.bulkhead_void_object
            bool_void.operation = 'DIFFERENCE'
            bool_void.double_threshold=0

            bpy_helper.move_object_to_collection(self.bulkhead_void_collection,self.bulkhead_void_object)


        bpy_helper.move_object_to_collection(self.bulkhead_collection,self.bulkhead_object)

        return self.bulkhead_object
