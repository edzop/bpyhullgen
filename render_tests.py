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
import imp
import math

geometry_helper = imp.load_source('geometry_helper','geometry_helper.py')

target_file = os.environ.get("TARGET_FILE")

target_file_without_extension=os.path.splitext(target_file)[0]

print("Target file: '%s'"%target_file_without_extension)

#output_path=
#    if not os.path.exists(d):
#        os.makedirs(d)

exec(open(target_file).read())

def do_render():

    frameIndex=bpy.context.scene.frame_current

    bpy.context.scene.render.resolution_x=1920
    bpy.context.scene.render.resolution_y=1080

    # you can adjust samples and percentage to get higher quality render
    bpy.context.scene.render.resolution_percentage=25
    bpy.context.scene.cycles.samples=30

    try:
        render_result = bpy.ops.render.render(animation=False, write_still=False, layer="", scene="")
    except Exception as e:
            print("Render Failed")
            return False

    print("Render Result")
    print(list(render_result))

    if 'FINISHED' in render_result:
        print('Frame ' + str(frameIndex) + ' rendered OK')

        target_path=os.path.split(os.path.abspath(target_file))

        full_output_image_path="%s/output/%s_%d.png"%(target_path[0],target_path[1],frameIndex)

        bpy.data.images['Render Result'].save_render(filepath=full_output_image_path)


backdrop=geometry_helper.make_backdrop()

cam=bpy.data.objects["Camera"]


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
cam.location.y=-0.1
cam.location.z=0
cam.location.x=-20

do_render()

# left side (back view)
backdrop.rotation_euler.z=math.radians(98)
bpy.context.scene.frame_set(4)
cam.location.y=-0.1
cam.location.z=1
cam.location.x=20
do_render()
