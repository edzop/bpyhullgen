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
 
curve_helper = imp.load_source('curve_helper','curve_helper.py')

material_helper = imp.load_source('material_helper','material_helper.py')

hull_maker = imp.load_source('hull_maker','hull_maker.py')
bulkhead = imp.load_source('bulkhead','bulkhead.py')

material_red=material_helper.make_diffuse_material("red",(0.7,0.3,0.3,1))
material_green=material_helper.make_diffuse_material("green",(0.3,0.7,0.3,1))
material_blue=material_helper.make_diffuse_material("blue",(0.3,0.3,0.7,1))

the_hull=hull_maker.hull_maker()
the_hull.make_hull_object()

hull_material = material_helper.make_material_hull()
bulkhead_material = material_helper.make_material_bulkhead()

new_chine=hull_maker.chine_helper(the_hull)

new_chine.rotation=[-75,0,0]
new_chine.offset=[0,0.9,0.3]
new_chine.name="wall_curve"
new_chine.curve_width=-0.5
new_chine.curve_length=the_hull.hull_length+0.05
new_chine.symmetrical=True
new_chine.longitudal_count=1
new_chine.make_chine()

new_chine.rotation=[-45,0,0]
new_chine.offset=[0,1.5,0.0]
new_chine.name="mid_curve"
new_chine.curve_width=-0.5
new_chine.curve_length=the_hull.hull_length+0.05
new_chine.symmetrical=True
new_chine.longitudal_count=1
new_chine.make_chine()



new_chine.rotation=[-90,0,0]
new_chine.offset=[0,0,0.6]
new_chine.name="top_curve"
new_chine.curve_width=-0.5
new_chine.curve_length=the_hull.hull_length+0.5
new_chine.symmetrical=False
new_chine.longitudal_count=1
new_chine.make_chine()

for lg in new_chine.longitudal_list:
    modifier=the_hull.hull_object.modifiers.new(name="bool", type='BOOLEAN')
    modifier.object=lg
    modifier.operation="DIFFERENCE"
    material_helper.assign_material(lg,material_green)
    curve_helper.hide_object(lg)

for lg in new_chine.longitudal_slicer_list:
    material_helper.assign_material(lg,material_red)
    curve_helper.make_rounded(lg,0.2)


print(new_chine.curve_object_1)

wall_curve=new_chine.curve_object_1
material_helper.assign_material(wall_curve,material_blue)
