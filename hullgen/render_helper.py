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
import os

def create_auto_save_nodes(target_file):
    scene = bpy.context.scene

    scene.render.use_compositing=True

    # make sure we have node tree
    if scene.node_tree==None:
        scene.use_nodes=True

    if scene.node_tree:
        nodes = scene.node_tree.nodes
        auto_save_output_label="auto_save"

        # remove previously auto created denoise nodes to prevent duplicates
        for node in nodes:
            if node.label==auto_save_output_label:
                nodes.remove(node)

        render_layer_node = nodes.new("CompositorNodeRLayers")
        render_layer_node.location=(0,0)
        render_layer_node.label=auto_save_output_label

        output_file_node = nodes.new("CompositorNodeOutputFile")
        output_file_node.location=(600,0)
        output_file_node.inputs[0].name="filename"
        current_path=os.path.split(os.path.abspath(target_file))
        output_file_node.base_path = "%s/output/"%(current_path[0])
        output_file_node.label=auto_save_output_label

        denoise_node = nodes.new("CompositorNodeDenoise")
        denoise_node.location=(300,-300)

        bpy.context.scene.render.use_file_extension=True

        blend_file = os.path.basename(target_file)
        base_output_file=os.path.splitext(blend_file)[0]
    
        output_file_node.file_slots[0].path="%s_"%(base_output_file)
        output_file_node.file_slots[0].use_node_format=False
        output_file_node.file_slots[0].format.file_format="PNG"
        
        doDenoise=True

        if doDenoise==True:
            output_file_node.file_slots.new("%s_##"%(base_output_file))
            output_file_node.file_slots[1].use_node_format=False
            output_file_node.file_slots[1].format.file_format="PNG"
            scene.node_tree.links.new(denoise_node.outputs[0],output_file_node.inputs[1])
        else:
            scene.node_tree.links.new(render_layer_node.outputs['Image'],output_file_node.inputs[0])

        scene.node_tree.links.new(render_layer_node.outputs['Image'],denoise_node.inputs["Image"])



def setup_keyframes(framedata):
    camTarget=None
    camObject=None

    # first find camTarget
    for obj in bpy.data.objects:
        if obj.type=="CAMERA":
            for constraint in obj.constraints:
                if constraint.type == 'TRACK_TO':
                    camTarget=constraint.target
                    camObject=obj
        
    # Create a focus object if not found            
    if camTarget==None:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        camTarget = bpy.context.active_object
        camTarget.name="focus"
        
    # Create a camera if not found
    if camObject==None:
        bpy.ops.object.camera_add(enter_editmode=False, 
            align='VIEW', 
            location=(0, 0, 0), 
            rotation=(0, 0, 0))
        camObject = bpy.context.active_object
        camObject.name="DefaultCam"

    isTracked=False    

    # Make sure trackto constraint set
    for constraint in camObject.constraints:
        if constraint.type == 'TRACK_TO':
            constraint.target=camTarget				
            isTracked=True
                    
    if isTracked==False:
        trackConstraint = camObject.constraints.new(type='TRACK_TO')
        trackConstraint.target = camTarget
        trackConstraint.up_axis='UP_Y'
        trackConstraint.track_axis='TRACK_NEGATIVE_Z'
                    
    camObject.data.dof.focus_object=camTarget
    camObject.data.dof.use_dof=True
    camObject.data.dof.aperture_fstop=8.0
            
    highestFrame=1

    for f in framedata:
        camLoc=f[1]
        targetLoc=f[2]
        curFrame=f[0]
        
        bpy.context.scene.frame_set(curFrame)
        camObject.location=camLoc
        camTarget.location=targetLoc
            
        camObject.keyframe_insert(data_path="location", frame=curFrame, index=0)
        camObject.keyframe_insert(data_path="location", frame=curFrame, index=1)
        camObject.keyframe_insert(data_path="location", frame=curFrame, index=2)
            
        camTarget.keyframe_insert(data_path="location", frame=curFrame, index=0)
        camTarget.keyframe_insert(data_path="location", frame=curFrame, index=1)
        camTarget.keyframe_insert(data_path="location", frame=curFrame, index=2)
            
        if curFrame > highestFrame:
            highestFrame=curFrame
            
    bpy.context.scene.frame_end=highestFrame
        