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
import math

from bpyhullgen.hullgen import geometry_helper 

target_file = os.environ.get("TARGET_FILE")

print("Working file: '%s'"%target_file)

exec(open(target_file).read())

def create_auto_save_nodes(targetfile):
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

        blend_file = os.path.basename(targetfile)
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

def do_render():

    frameIndex=bpy.context.scene.frame_current

    bpy.context.scene.render.resolution_x=2560
    bpy.context.scene.render.resolution_y=1440

    # you can adjust samples and percentage to get higher quality render
    bpy.context.scene.render.resolution_percentage=50

    bpy.context.scene.render.engine="CYCLES"
    bpy.context.scene.cycles.samples=20

    try:
        render_result = bpy.ops.render.render(animation=False, write_still=False, layer="", scene="")
    except Exception as e:
            print("Render Failed")
            return False

    print("Render Result %s"%list(render_result))

backdrop=geometry_helper.make_backdrop()

cam=bpy.data.objects["Camera"]

create_auto_save_nodes(target_file)

# front view
bpy.context.scene.frame_set(1)
cam.location.y=-20
cam.location.z=1
cam.location.x=0

do_render()

# top view
bpy.context.scene.frame_set(2)
cam.location.y=-0.1
cam.location.z=20
cam.location.x=0

do_render()

# right side (front view)
backdrop.rotation_euler.z=math.radians(-94)
bpy.context.scene.frame_set(3)
cam.location.y=-1
cam.location.z=0
cam.location.x=-12

do_render()

# left side (back view)
backdrop.rotation_euler.z=math.radians(98)
bpy.context.scene.frame_set(4)
cam.location.y=-0.1
cam.location.z=1
cam.location.x=13
do_render()

# corner side (front right)
backdrop.rotation_euler.z=math.radians(98)
bpy.context.scene.frame_set(5)
cam.location.y=-10
cam.location.z=10
cam.location.x=5
do_render()
