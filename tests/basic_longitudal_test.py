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


the_hull=hull_maker.hull_maker()

the_hull.hull_height=0.4
the_hull.hull_width=0.4
the_hull.make_hull_object()

new_chine=hull_maker.chine_helper(the_hull)

new_chine.rotation=[180,0,0]
new_chine.offset=[0,0,0]
new_chine.name="top"
new_chine.longitudal_count=1
new_chine.longitudal_thickness=0.02
new_chine.longitudal_width=-0.15
new_chine.symmetrical=False
new_chine.make_chine()