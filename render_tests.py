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
from bpyhullgen.hullgen import render_helper
from bpyhullgen.bpyutils import bpy_helper

target_file = os.environ.get("TARGET_FILE")

print("Working file: '%s'"%target_file)

# Remove the default startup cube so it doesn't show up in the renders.
# A fresh Blender install starts with Camera/Cube/Light; the test scenes build
# their own geometry and never use this cube.
if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

exec(open(target_file).read())

def enable_gpu():
    # Render on the GPU when one is available, preferring OPTIX on NVIDIA and
    # falling back through the other GPU backends, then CPU as a last resort.
    prefs=bpy.context.preferences.addons['cycles'].preferences
    for backend in ('OPTIX','CUDA','HIP','ONEAPI','METAL'):
        try:
            prefs.compute_device_type=backend
        except TypeError:
            continue
        prefs.refresh_devices()
        gpus=[d for d in prefs.devices if d.type==backend]
        if gpus:
            for d in prefs.devices:
                d.use=(d.type==backend)
            print("Cycles rendering on GPU (%s): %s"%(backend,[d.name for d in gpus]))
            return 'GPU'
    print("No GPU found, Cycles rendering on CPU")
    return 'CPU'

cycles_device=enable_gpu()

def do_render():

    frameIndex=bpy.context.scene.frame_current

    bpy.context.scene.render.resolution_x=2560
    bpy.context.scene.render.resolution_y=1440

    # you can adjust samples and percentage to get higher quality render
    bpy.context.scene.render.resolution_percentage=100

    bpy.context.scene.render.engine="CYCLES"
    bpy.context.scene.cycles.device=cycles_device
    bpy.context.scene.cycles.samples=100

    try:
        render_result = bpy.ops.render.render(animation=False, write_still=False, layer="", scene="")
    except Exception as e:
            print("Render Failed")
            return False

    print("Render Result %s"%list(render_result))

backdrop=geometry_helper.make_backdrop()

render_helper.create_auto_save_nodes(target_file)

for f in range(bpy.context.scene.frame_start,bpy.context.scene.frame_end+1):
    bpy.context.scene.frame_set(f)
    do_render()
