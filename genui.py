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

# bpy.ops.script.reload()

import bpy
import math
import glob
import os

from .hullgen import geometry_helper as geometry_helper
from .hullgen import material_helper as material_helper
from .hullgen import window_helper as window_helper
from .hullgen import measure_helper as measure_helper
from .hullgen import bulkhead as bulkhead
from .hullgen import modshape_helper as modshape_helper
from .hullgen import curve_helper as curve_helper
from .hullgen import keel_helper as keel_helper
from .hullgen import xml_helper as xml_helper
from bpyhullgen.hullgen import bpy_helper

from .hullgen import chine_helper as chine_helper

from bpy.props import (StringProperty,
					BoolProperty,
					IntProperty,
					FloatProperty,
					FloatVectorProperty,
					EnumProperty,
					PointerProperty,
					CollectionProperty
					)

from bpy.types import (Panel,
					Operator,
					PropertyGroup,
					UIList
					)



class hullgendef_file_Properties(PropertyGroup): 
	"""Group of properties representing a configuration file.""" 

	filename: StringProperty( 
		name="filename", 
		description="A filename for this item", 
		default="Untitled") 

	exists: BoolProperty(default=False)



class hullgendef_bulkhead_Properties(PropertyGroup):

	station : FloatProperty(
		name = "station",
		description = "Station X Position",
		default = -2
		)

	thickness : FloatProperty(
		name = "thickness",
		description = "Bulkhead Thickness",
		default = 0.1
		)

	floor_height : FloatProperty(
		name = "floor_height",
		description = "Floor Height",
		default = 0.1
		)


	watertight : BoolProperty(
		name = "Watertight",
		default = False,
		description = "If true bulkhead is watertight"
	)




class hullgendef_modshape_Properties(PropertyGroup): 
	"""Group of properties representing a Modifier Shape.""" 

	name: StringProperty( 
		name="Name", 
		description="A name for this item", 
		default="modshape")

	type: StringProperty( 
		name="Type", 
		description="type", 
		default="cube")

	rotation : FloatVectorProperty(
		name = "Rot",
		description = "Rotation",
		subtype = "EULER"
		)

	location : FloatVectorProperty(
		name = "Loc",
		description = "Location",
		subtype = "XYZ"
		)

	size : FloatVectorProperty(
		name = "Size",
		description = "Size",
		default = [1,1,1],
		subtype = "XYZ"
		)

	mod_mode: EnumProperty(
		name="Mode:",
		description="Mode",
		items=[ ('add', "Add", ""),
				('subtract', "Subtract", ""),
			   ]
		)

	deform : FloatVectorProperty(
		name = "Def",
		description = "Rotation",
		default= [1,1,1]
		)



class hullgendef_keel_Properties(PropertyGroup): 
	"""Group of properties representing a Keel.""" 

	name: StringProperty( 
		name="Name", 
		description="A name for this item", 
		default="Untitled")

	station_start : FloatProperty(
		name = "start",
		description = "Station Start",
		default = -3
		)

	station_end : FloatProperty(
		name = "start",
		description = "Station End",
		default = 3
		)

	lateral_offset : FloatProperty(
		name = "lateral_offset",
		description = "Lateral Offset",
		default = 0
		)

	top_height : FloatProperty(
		name = "top_height",
		description = "Top Height",
		default = -0.5
		)


class hullgendef_longitudal_Properties(PropertyGroup): 
	"""Group of properties representing a longitudal stringer.""" 

	name: StringProperty( 
		name="Name", 
		description="A name for this item", 
		default="Untitled")

	z_offset : FloatProperty(
		name = "z_offset",
		description = "Z Offset",
		default = 0
		)

	width : FloatProperty(
		name = "width",
		description = "width",
		default = -0.2
		)

	x_min : FloatProperty(
		name = "x_min",
		description = "X Min",
		default = -3
		)

	x_max : FloatProperty(
		name = "x_max",
		description = "X Max",
		default = 3
		)




class hullgendef_chine_Properties(PropertyGroup): 
	"""Group of properties representing an single Chine.""" 

	name: StringProperty( 
		name="Name", 
		description="A name for this item", 
		default="Untitled") 
		
	rot : FloatVectorProperty(
		name = "Rot",
		description = "Rotation",
		subtype = "EULER"
		)

	pos : FloatVectorProperty(
		name = "Pos",
		description = "Position",
		subtype = "XYZ"
		)

	width : FloatProperty(
		name = "width",
		description = "Width of Curve (m))",
		default = 1.2,
		min = 0.1,
		max = 200
		)

	symmetrical : BoolProperty(
		name = "Symmetrical",
		default = True,
		description = "If true make two Symmetrical chines (L + R)"
	)

	length : FloatProperty(
		name = "length",
		description = "Length of Curve (m)",
		default = 11,
		min = 0.01,
		max = 200
		)

	active_longitudal_index: IntProperty(default=-1)

	longitudals: CollectionProperty(
		name = "Longitudals",
		type = hullgendef_longitudal_Properties		
	)



class hullgendef_hull_Properties(PropertyGroup): 
	"""Group of properties representing Hull.""" 

	curve_resolution : IntProperty(
		name = "Resolution",
		description = "Curve Resolution",
		default = 5,
		min = 1,
		max = 256
		)


	thickness : FloatProperty(
		name = "thickness",
		description = "Material thickness",
		default = 0.1,
		min = 0.0001,
		max = 256
		)

	overcut : FloatProperty(
		name = "overcut",
		description = "Slicer Overcut",
		default = 1.1
		)

	slot_gap : FloatProperty(
		name = "slotgap",
		description = "Slot Gap",
		default = 0.05
		)


	hull_length : FloatProperty(
		name = "HullLength",
		description = "Length of Hull (m)",
		default = 10,
		min = 1,
		max = 500.0
		)


	hull_width : FloatProperty(
		name = "HullWidth",
		description = "Width of Hull (m)",
		default = 3,
		min = 1,
		max = 250.0
		)

	# ========= Chines ==========

	active_chine_index: IntProperty(default=-1)

	chines: CollectionProperty(
		name = "chines",
		type = hullgendef_chine_Properties)


	# ========= Bulkheads ==========

	active_bulkhead_index: IntProperty(default=-1)

	bulkheads: CollectionProperty(
		name = "bulkheads",
		type = hullgendef_bulkhead_Properties)

	# ========= ModShapes ==========

	active_modshape_index: IntProperty(default=-1)

	modshapes: CollectionProperty(
		name = "modshapes",
		type = hullgendef_modshape_Properties)


	# ========= Keels =============

	active_keel_index: IntProperty(default=-1)
	keels: CollectionProperty(
		name = "keels",
		type = hullgendef_keel_Properties)

	# ========= Generate Toggles =============

	make_bulkheads : BoolProperty(
		name = "Make Bulkheads",
		default = True,
		description = "Generate Bulkheads"
	)

	make_keels : BoolProperty(
		name = "Make Keels",
		default = True,
		description = "Generate Keels"
	)

	make_longitudals : BoolProperty(
		name = "Make Longitudals",
		default = True,
		description = "Generate Longitudals"
	)

	hide_hull : BoolProperty(
		name = "Hide Hull",
		default = True,
		description = "Hide Hull from view after generation (to see structure more clearly)"
	)

	


class STATION_UL_List(UIList): 
	"""Station UIList.""" 
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
		# We could write some code to decide which icon to use here... 
		custom_icon = 'OBJECT_DATAMODE' 
		
		# Make sure your code supports all 3 layout types 
		if self.layout_type in {'DEFAULT', 'COMPACT'}: 
			layout.label(text=str(item.station), icon = custom_icon) 
		elif self.layout_type in {'GRID'}: 
			layout.alignment = 'CENTER' 
			layout.label(text="", icon = custom_icon) 

class FILE_UL_List(UIList): 
	"""File UIList.""" 
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
		# We could write some code to decide which icon to use here... 
		custom_icon = 'OBJECT_DATAMODE' 
		
		# Make sure your code supports all 3 layout types 
		if self.layout_type in {'DEFAULT', 'COMPACT'}: 
			layout.label(text=item.filename, icon = custom_icon) 
		elif self.layout_type in {'GRID'}: 
			layout.alignment = 'CENTER' 
			layout.label(text="", icon = custom_icon) 


class MY_UL_NameList(UIList): 
	"""hullgen UIList.""" 
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index): 
		# We could write some code to decide which icon to use here... 
		custom_icon = 'OBJECT_DATAMODE' 
		
		# Make sure your code supports all 3 layout types 
		if self.layout_type in {'DEFAULT', 'COMPACT'}: 
			layout.label(text=item.name, icon = custom_icon) 
		elif self.layout_type in {'GRID'}: 
			layout.alignment = 'CENTER' 
			layout.label(text="", icon = custom_icon) 


def ensure_dir(f):
	d = os.path.dirname(f)
	if not os.path.exists(d):
		print("Directory %s not found - Creating"%(d))
		os.makedirs(d)



defaults_path="bpyhullgen_defaults"
file_extension="xml"

def get_selected_file_path(context):
	file_properties = context.scene.hullgen_file_properties
	index = context.scene.hullgen_file_index

	file_property=file_properties[index]
	return "%s/%s.%s"%(defaults_path,file_property.filename,file_extension)



class LIST_OT_SaveConfig(Operator): 
	"""Save configuuration settings""" 
	bl_idname = "genui.saveconfig" 
	bl_label = "Save" 

	@classmethod 
	def poll(cls, context): 
		return context.scene.hullgen_file_properties 
	
	def execute(self, context): 

		the_hull = context.scene.the_hull
		#update_hull_from_properties(the_hull,context)



		selected_filepath=get_selected_file_path(context)

		ensure_dir(selected_filepath)
		xml_helper.write_xml(the_hull,selected_filepath)

		bpy.context.workspace.status_text_set("Saved %s"%get_selected_file_path(context))	

		context.scene.hullgen_file_properties[context.scene.hullgen_file_index].exists=True

		return{'FINISHED'} 

class LIST_OT_Newconfig(Operator): 
	"""New configuration settings""" 
	bl_idname = "genui.newconfig" 
	bl_label = "New" 
	
	def execute(self, context): 
		file_properties = context.scene.hullgen_file_properties

		newfile=file_properties.add()

		prop_count=len(file_properties)
		newfile.filename="File_%d"%prop_count

		return{'FINISHED'} 

class LIST_OT_LoadConfig(Operator): 
	"""Load configuration settings""" 
	bl_idname = "genui.loadconfig" 
	bl_label = "Load" 

	@classmethod 
	def poll(cls, context): 
		if context.scene.hullgen_file_index>=0:
			if context.scene.hullgen_file_properties[context.scene.hullgen_file_index].exists==True:
				return True

		return False
	
	def execute(self, context): 
		#file_properties = context.scene.hullgen_file_properties

		the_hull = context.scene.the_hull
		new_hull = xml_helper.read_hull(get_selected_file_path(context))

		xml_helper.dump_hull(new_hull)

		update_properties_from_hull(new_hull,context)


		return{'FINISHED'} 


class LIST_OT_RefreshConfig(Operator): 
	"""Refresh configuration files from default path """ 
	bl_idname = "genui.refreshconfig" 
	bl_label = "Refresh Files" 
	
	def execute(self, context): 

		search_path="%s/*.%s"%(defaults_path,file_extension)

		file_list = glob.glob(search_path)
		#print("searching: %s found: %d"%(search_path,len(file_list)))

		context.scene.hullgen_file_properties.clear() 

		props = context.scene.hullgen_file_properties

		for file in file_list:

			newfile=props.add()

			file_without_path=os.path.basename(file)
			file_without_extension=os.path.splitext(file_without_path)[0]

			newfile.filename=file_without_extension
			newfile.exists=True

		
		#print(context.scene.the_hull.hull_length)

		return{'FINISHED'} 



#===============================================================================

class LIST_OT_NewLongitudalItem(Operator): 
	"""Add a new item to the list.""" 
	bl_idname = "genui.new_longitudal" 
	bl_label = "Add Longutidal" 

	@classmethod 
	def poll(cls, context): 
		if context.scene.hull_properties.active_chine_index>=0:
			if context.scene.hull_properties.chines[context.scene.hull_properties.active_chine_index]!=None:
				return True

		return False

	
	
	def execute(self, context): 
		hull_props = context.scene.hull_properties 

		chine_index=hull_props.active_chine_index
		#longitudal_index=context.scene.hullgen_longitudal_index
		#longitudal_props=context.scene.longitudal_properties

		chine_props=hull_props.chines[chine_index]

		new_longitudal=chine_props.longitudals.add()

		prop_count=len(chine_props.longitudals)
		new_longitudal.name="Longitudal_%d"%prop_count

		#hull_props.chines[chine_index].active_longitudal_index=prop_count

		chine_props.active_longitudal_index=prop_count-1

		#longitudal_props[prop_count-1].chine_index=chine_index
		#print(context.scene.the_hull.hull_length)
		return{'FINISHED'} 


class LIST_OT_DeleteLongitudalItem(Operator): 
	"""Delete the selected item from the list.""" 
	bl_idname = "genui.delete_longitudal" 
	bl_label = "Delete Longitudal" 


	@classmethod 
	def poll(cls, context): 

		hull_props = context.scene.hull_properties 

		if context.scene.hull_properties.active_chine_index>=0:
			chine_prop=hull_props.chines[hull_props.active_chine_index]
			if chine_prop.active_longitudal_index>=0:
				return True

		return False
		
	def execute(self, context): 
		hull_props = context.scene.hull_properties 

		chine_index=hull_props.active_chine_index

		chine_prop=hull_props.chines[hull_props.active_chine_index]

		longitudal_props=hull_props.chines[chine_index].longitudals

		longitudal_index = hull_props.chines[chine_index].active_longitudal_index 

		longitudal_props.remove(longitudal_index)

		chine_prop.active_longitudal_index= min(max(0, longitudal_index - 1), len(longitudal_props) - 1) 
		return{'FINISHED'}



#===============================================================================

class LIST_OT_NewKeelItem(Operator): 
	"""Add a new item to the list.""" 
	bl_idname = "genui.new_keel" 
	bl_label = "Add Keel" 
	
	def execute(self, context): 
		keel_props = context.scene.hull_properties.keels
		new_keel=keel_props.add()

		prop_count=len(keel_props)
		new_keel.name="Keel_%d"%prop_count
		#print(context.scene.the_hull.hull_length)

		context.scene.hull_properties.active_keel_index=prop_count-1
		return{'FINISHED'} 


class LIST_OT_DeleteKeelItem(Operator): 
	"""Delete the selected item from the list.""" 
	bl_idname = "genui.delete_keelitem" 
	bl_label = "Delete Keel" 
	
	@classmethod 
	def poll(cls, context): 
		return context.scene.hull_properties.active_keel_index>=0
		
	def execute(self, context): 
		keel_props = context.scene.hull_properties.keels
		index = context.scene.hull_properties.active_keel_index
		keel_props.remove(index) 
		context.scene.hull_properties.active_keel_index = min(max(0, index - 1), len(keel_props) - 1) 
		return{'FINISHED'}


#===============================================================================

class LIST_OT_NewChineItem(Operator): 
	"""Add a new item to the list.""" 
	bl_idname = "genui.new_chine" 
	bl_label = "Add Chine" 
	
	def execute(self, context):

		chine_props=context.scene.hull_properties.chines
		chine_props.add()

		prop_count=len(chine_props)
		chine_props[prop_count-1].name="Chine_%d"%prop_count


		context.scene.hull_properties.active_chine_index=len(chine_props)-1
		#print(context.scene.the_hull.hull_length)
		return{'FINISHED'} 


class LIST_OT_DeleteChineItem(Operator): 
	"""Delete the selected item from the list.""" 
	bl_idname = "genui.delete_chineitem" 
	bl_label = "Delete Chine" 
	
	@classmethod 
	def poll(cls, context): 
		active_chine_index=context.scene.hull_properties.active_chine_index
		if active_chine_index>=0:
			if context.scene.hull_properties.chines[active_chine_index]!=None:
				return True

		return False
		
	def execute(self, context):
		hull_properties = context.scene.hull_properties 
		chine_index = hull_properties.active_chine_index
		hull_properties.chines.remove(chine_index) 
		hull_properties.active_chine_index = min(max(0, chine_index - 1), len(hull_properties.chines) - 1) 


		#for idx,longitudal_prop in enumerate(context.scene.longitudal_properties):
		#	if longitudal_prop.chine_index>chine_index:
		#		longitudal_prop.chine_index=longitudal_prop.chine_index-1
		#	elif longitudal_prop.chine_index==chine_index:
		#		context.scene.longitudal_properties.remove(idx)



		return{'FINISHED'}

#===============================================================================



class WM_OT_auto_bulkheads(bpy.types.Operator):
	"""Auto populate bulkheads"""
	bl_label = "Auto Bulkheads"
	bl_idname = "wm.auto_bulkheads"
	
	station_start: bpy.props.FloatProperty(name="station_start", default=(-3))

	station_end: bpy.props.FloatProperty(name="station_end", 
		description="Station End",default=(3))

	spacing: bpy.props.FloatProperty(name="spacing", default=(0.6))
	floor_height: bpy.props.FloatProperty(name="floor_height", default=(-0.5))
	watertight: bpy.props.BoolProperty(name="watertight", default=False)

		   
	def execute(self, context):
		
		start=self.station_start
		end=self.station_end
		watertight=self.watertight
		
		bulkhead_props=context.scene.hull_properties.bulkheads


		current_bulkhead_location=self.station_start

		while current_bulkhead_location<=self.station_end:

			bulkhead_props.add()
			prop_count=len(bulkhead_props)
			newprop=bulkhead_props[prop_count-1]

			newprop.station=current_bulkhead_location
			newprop.watertight=self.watertight
			newprop.floor_height=self.floor_height

			current_bulkhead_location+=self.spacing


		context.scene.hull_properties.active_bulkhead_index=len(bulkhead_props)-1
		
		return {'FINISHED'}
	
	def invoke(self, context, event):
		
		return context.window_manager.invoke_props_dialog(self)



class LIST_OT_NewBulkheadItem(Operator): 
	"""Add a new bulkhead to the list.""" 
	bl_idname = "genui.new_bulkhead" 
	bl_label = "Add Bulkhead" 
	
	def execute(self, context):

		bulkhead_props=context.scene.hull_properties.bulkheads
		bulkhead_props.add()

		prop_count=len(bulkhead_props)
		#bulkhead_props[prop_count-1].name="Chine_%d"%prop_count


		context.scene.hull_properties.active_bulkhead_index=len(bulkhead_props)-1
		#print(context.scene.the_hull.hull_length)
		return{'FINISHED'} 


class LIST_OT_DeleteBulkheadItem(Operator): 
	"""Delete the selected bulkhead from the list.""" 
	bl_idname = "genui.delete_bulkhead" 
	bl_label = "Delete Bulkhead" 
	
	@classmethod 
	def poll(cls, context): 
		active_bulkhead_index=context.scene.hull_properties.active_bulkhead_index
		if active_bulkhead_index>=0:
			if context.scene.hull_properties.bulkheads[active_bulkhead_index]!=None:
				return True

		return False
		
	def execute(self, context):
		hull_properties = context.scene.hull_properties 
		active_bulkhead_index = hull_properties.active_bulkhead_index
		hull_properties.bulkheads.remove(active_bulkhead_index) 
		hull_properties.active_bulkhead_index = min(max(0, active_bulkhead_index - 1), len(hull_properties.bulkheads) - 1) 


		#for idx,longitudal_prop in enumerate(context.scene.longitudal_properties):
		#	if longitudal_prop.chine_index>chine_index:
		#		longitudal_prop.chine_index=longitudal_prop.chine_index-1
		#	elif longitudal_prop.chine_index==chine_index:
		#		context.scene.longitudal_properties.remove(idx)


		return{'FINISHED'}


#===============================================================================

class LIST_OT_NewModshapeItem(Operator): 
	"""Add a new modshape to the list.""" 
	bl_idname = "genui.new_modshape" 
	bl_label = "Add Modshape" 
	
	def execute(self, context):

		modshape_props=context.scene.hull_properties.modshapes
		modshape_props.add()

		prop_count=len(modshape_props)
		#bulkhead_props[prop_count-1].name="Chine_%d"%prop_count


		context.scene.hull_properties.active_modshape_index=len(modshape_props)-1
		#print(context.scene.the_hull.hull_length)
		return{'FINISHED'} 


class LIST_OT_DeleteModshapeItem(Operator): 
	"""Delete the selected modshape from the list.""" 
	bl_idname = "genui.delete_modshape" 
	bl_label = "Delete Modshape" 
	
	@classmethod 
	def poll(cls, context): 
		active_modshape_index=context.scene.hull_properties.active_modshape_index
		if active_modshape_index>=0:
			if context.scene.hull_properties.modshapes[active_modshape_index]!=None:
				return True

		return False
		
	def execute(self, context):
		hull_properties = context.scene.hull_properties 
		active_modshape_index = hull_properties.active_modshape_index
		hull_properties.modshapes.remove(active_modshape_index) 
		hull_properties.active_modshape_index = min(max(0, active_modshape_index - 1), len(hull_properties.modshapes) - 1) 


		#for idx,longitudal_prop in enumerate(context.scene.longitudal_properties):
		#	if longitudal_prop.chine_index>chine_index:
		#		longitudal_prop.chine_index=longitudal_prop.chine_index-1
		#	elif longitudal_prop.chine_index==chine_index:
		#		context.scene.longitudal_properties.remove(idx)


		return{'FINISHED'}



#===============================================================================


def update_properties_from_hull(the_hull,context):
	hull_properties = context.scene.hull_properties 
	
	hull_properties.hull_width=the_hull.hull_width
	hull_properties.hull_length=the_hull.hull_length
	hull_properties.curve_resolution=the_hull.curve_resolution
	hull_properties.thickness=the_hull.structural_thickness
	hull_properties.overcut=the_hull.slicer_overcut_ratio
	hull_properties.slot_gap=the_hull.slot_gap

	hull_properties.make_keels=the_hull.make_keels
	hull_properties.make_bulkheads=the_hull.make_bulkheads
	hull_properties.make_longitudals=the_hull.make_longitudals
	hull_properties.hide_hull=the_hull.hide_hull

	hull_properties.bulkheads.clear()
	hull_properties.active_bulkhead_index=-1

	for bulkhead_definition in the_hull.bulkhead_definitions:
		bulkhead_prop=hull_properties.bulkheads.add()

		bulkhead_prop.station=bulkhead_definition.station
		bulkhead_prop.watertight=bulkhead_definition.watertight
		bulkhead_prop.floor_height=bulkhead_definition.floor_height


	hull_properties.modshapes.clear()
	hull_properties.active_modshape_index=-1

	for modshape in the_hull.modshapes:
		modshape_prop=hull_properties.modshapes.add()

		modshape_prop.name=modshape.name
		modshape_prop.location=modshape.location

		modshape_prop.rotation=[math.radians(modshape.rotation[0]),
				math.radians(modshape.rotation[1]),
				math.radians(modshape.rotation[2])]

		#modshape_prop.rotation=modshape.rotation
		modshape_prop.size=modshape.size
		modshape_prop.mod_mode=modshape.mod_mode
		modshape_prop.deform=modshape.deform

		
	hull_properties.chines.clear()
	hull_properties.active_chine_index=-1

	for chine in the_hull.chine_list:
		chine_prop=hull_properties.chines.add()

		#chine_prop=chine_properties[len(chine_properties) - 1]

		chine_prop.name=chine.name
		chine_prop.rot=[math.radians(chine.rotation[0]),
				math.radians(chine.rotation[1]),
				math.radians(chine.rotation[2])]

		chine_prop.width=chine.curve_width
		chine_prop.length=chine.curve_length

		chine_prop.pos=chine.offset

		chine_prop.symmetrical=chine.symmetrical


		for longitudal_definition in chine.longitudal_definitions:
			longitudal_prop=chine_prop.longitudals.add()

			#longitudal_prop=longitudal_properties[len(longitudal_properties) - 1]

			longitudal_prop.x_min=longitudal_definition.limit_x_min
			longitudal_prop.x_max=longitudal_definition.limit_x_max

			longitudal_prop.z_offset=longitudal_definition.z_offset

			longitudal_prop.width=longitudal_definition.width

	#keel_properties.clear()

	hull_properties.keels.clear()
	hull_properties.active_keel_index=-1

	for keel in the_hull.keel_list:
		keel_prop=hull_properties.keels.add()

		#keel_prop=keel_properties[len(keel_properties) - 1]

		keel_prop.lateral_offset=keel.lateral_offset

		keel_prop.station_start=keel.station_start
		keel_prop.station_end=keel.station_end

		keel_prop.top_height=keel.top_height

		


def update_hull_from_properties(the_hull,context):

	the_hull.clear_all()

	hull_properties = context.scene.hull_properties 

	the_hull.hull_width=hull_properties.hull_width
	the_hull.hull_length=hull_properties.hull_length

	the_hull.curve_resolution=hull_properties.curve_resolution
	the_hull.structural_thickness=hull_properties.thickness
	the_hull.slicer_overcut_ratio=hull_properties.overcut
	the_hull.slot_gap=hull_properties.slot_gap

	the_hull.make_keels=hull_properties.make_keels
	the_hull.make_bulkheads=hull_properties.make_bulkheads
	the_hull.make_longitudals=hull_properties.make_longitudals
	the_hull.hide_hull=hull_properties.hide_hull

	for modshapeprop in hull_properties.modshapes:

		rot = [ math.degrees(modshapeprop.rotation[0]),
			math.degrees(modshapeprop.rotation[1]),
			math.degrees(modshapeprop.rotation[2]) ]

		deform = [ 	modshapeprop.deform[0], 
					modshapeprop.deform[1], 
					modshapeprop.deform[2]
		]

		new_modshape=modshape_helper.modshape(
			name=modshapeprop.name,
			location=modshapeprop.location,
			rotation=rot,
			size=modshapeprop.size,
			mod_mode=modshapeprop.mod_mode,
			deform=deform
		)

		the_hull.add_modshape(new_modshape)

	for bulkheadprop in hull_properties.bulkheads:
		new_bulkhead_definition=bulkhead.bulkhead_definition(
			station=bulkheadprop.station,
			watertight=bulkheadprop.watertight,
			floor_height=bulkheadprop.floor_height,
			thickness=hull_properties.thickness
		)

		the_hull.add_bulkhead_definition(new_bulkhead_definition)

		
	for chineprop in hull_properties.chines:

		rot = [ math.degrees(chineprop.rot[0]),
			math.degrees(chineprop.rot[1]),
			math.degrees(chineprop.rot[2]) ]

		width=chineprop.width
		length=chineprop.length

		new_chine=chine_helper.chine_helper(the_hull,
			name=chineprop.name,
			length=length,
			width=width,
			rotation=rot,
			offset=chineprop.pos,
			symmetrical=chineprop.symmetrical
		)

		the_hull.add_chine(new_chine)

		for longitudal_prop in chineprop.longitudals:
			
			new_longitudal=chine_helper.longitudal_definition(z_offset=longitudal_prop.z_offset,
				width=longitudal_prop.width,
				thickness=hull_properties.thickness)

			new_longitudal.set_limit_x_length(
						longitudal_prop.x_min,
						longitudal_prop.x_max)

			new_chine.add_longitudal_definition(new_longitudal)

	for keelprop in hull_properties.keels:

		print("keel")

		new_keel=keel_helper.keel(the_hull,
			lateral_offset=keelprop.lateral_offset,
			top_height=keelprop.top_height,
			station_start=keelprop.station_start,
			station_end=keelprop.station_end,
			thickness=hull_properties.thickness
		)

		the_hull.add_keel(new_keel)


	return the_hull

#===============================================================================

class LIST_OT_GenHull(Operator): 
	"""Generate the Hull""" 
	bl_idname = "genui.genhull" 
	bl_label = "GenHull" 
	
#	bl_idname = "wm.submerge"
#	bl_label = "Submerge"
	
	def execute(self, context): 

		the_hull = context.scene.the_hull

		update_hull_from_properties(the_hull,context)

		the_hull.make_hull_object()

		the_hull.integrate_components()
		
		return{'FINISHED'}


class LIST_OT_DeleteHull(Operator): 
	"""Delete all hull objects""" 
	bl_idname = "genui.deletehull" 
	bl_label = "Delete Hull" 
	
	def execute(self, context): 

		the_hull = context.scene.the_hull
		the_hull.clear_all()
		
		return{'FINISHED'} 


#===============================================================================

min_rows = 2

class OBJECT_PT_bpyhullgendef_load_save_panel (Panel):

	bl_label = "File Operations"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "bpyHullGen"

	def draw(self, context): 
		layout = self.layout 
		scene = context.scene 

		row = layout.row()
		row.operator('genui.refreshconfig') 
		row.operator('genui.newconfig') 

		if len(scene.hullgen_file_properties)>0:
			row = layout.row() 
			layout.label(text="Files") 
			row = layout.row() 
			row.template_list(listtype_name="FILE_UL_List", 
				list_id="File_List", 
				dataptr=scene, 
				propname="hullgen_file_properties", 
				active_dataptr=scene, 
				active_propname="hullgen_file_index",
				rows=min_rows) 

			if scene.hullgen_file_index >= 0 and scene.hullgen_file_properties: 
				item = scene.hullgen_file_properties[scene.hullgen_file_index] 
				row = layout.row() 
				row.prop(item, "filename") 

			#layout.template_list("MATERIAL_UL_matslots_example", "compact", obj, "material_slots",
			#                     obj, "active_material_index", type='COMPACT')

			row = layout.row()
			row.operator('genui.saveconfig') 
			row.operator('genui.loadconfig') 
		
		#if scene.list_index >= 0 and scene.chine_properties: 
		#	item = scene.chine_properties[scene.list_index] 
			



class OBJECT_PT_bpyhullgendef_panel (Panel):

	bl_label = "bpyHullDef"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "bpyHullGen"

	def draw(self, context): 
		layout = self.layout 
		scene = context.scene 
		hull_props=context.scene.hull_properties


		row = layout.row()
		layout.prop( hull_props, "hull_length")
		layout.prop( hull_props, "hull_width")

		row = layout.row()
		layout.prop( hull_props, "curve_resolution")
		layout.prop( hull_props, "thickness")
		layout.prop( hull_props, "overcut")
		layout.prop( hull_props, "slot_gap")

		row = layout.row()
		layout.prop( hull_props, "make_bulkheads")
		layout.prop( hull_props, "make_keels")		
		layout.prop( hull_props, "make_longitudals")
		layout.prop( hull_props, "hide_hull")	

		row = layout.row()
		row.operator('genui.genhull') 
		row.operator('genui.deletehull') 



		# ======== Modshapes ==============

		if len(hull_props.modshapes)>0:
			row = layout.row() 
			layout.label(text="Modshapes") 
			row = layout.row() 
			row.template_list(listtype_name="MY_UL_NameList", 
				list_id="Modshape_List", 
				dataptr=hull_props, 
				propname="modshapes", 
				active_dataptr=hull_props, 
				active_propname="active_modshape_index",
				rows=min_rows) #,type='COMPACT') 

		row = layout.row() 
		row.operator('genui.new_modshape') 
		row.operator('genui.delete_modshape')

		if hull_props.active_modshape_index >= 0:
			if hull_props.modshapes[hull_props.active_modshape_index]: 
				modshape_item = hull_props.modshapes[hull_props.active_modshape_index] 
				row = layout.row() 
				row.prop(modshape_item, "name") 

				row = layout.row() 
			
				row = layout.row() 
				row.prop(modshape_item, "location") 

				row = layout.row() 
				row.prop(modshape_item, "size") 

				row = layout.row() 
				row.prop(modshape_item, "rotation") 

				row = layout.row() 
				row.prop(modshape_item, "mod_mode") 

				row = layout.row() 
				row.prop(modshape_item, "deform") 





				


		# ======== Bulkheads ==============

		if len(hull_props.bulkheads)>0:
			row = layout.row() 
			layout.label(text="Bulkheads") 
			row = layout.row() 
			row.template_list(listtype_name="STATION_UL_List", 
				list_id="Bulkhead_List", 
				dataptr=hull_props, 
				propname="bulkheads", 
				active_dataptr=hull_props, 
				active_propname="active_bulkhead_index",
				rows=min_rows) #,type='COMPACT') 

		row = layout.row() 
		row.operator('genui.new_bulkhead') 
		row.operator('genui.delete_bulkhead')
		row.operator('wm.auto_bulkheads')

		if hull_props.active_bulkhead_index >= 0:
			if hull_props.bulkheads[hull_props.active_bulkhead_index]: 
				bulkhead_item = hull_props.bulkheads[hull_props.active_bulkhead_index] 
				row = layout.row() 
				row.prop(bulkhead_item, "station")

				row = layout.row() 
				row.prop(bulkhead_item, "watertight")

				row = layout.row() 
				row.prop(bulkhead_item, "floor_height")


		# ======== Chines ==============

		if len(hull_props.chines)>0:
			row = layout.row() 
			layout.label(text="Chines") 
			row = layout.row() 
			row.template_list(listtype_name="MY_UL_NameList", 
				list_id="Chine_List", 
				dataptr=hull_props, 
				propname="chines", 
				active_dataptr=hull_props, 
				active_propname="active_chine_index",
				rows=min_rows) #,type='COMPACT') 

		row = layout.row() 
		row.operator('genui.new_chine') 
		row.operator('genui.delete_chineitem') 

				
		if hull_props.active_chine_index >= 0:
			if hull_props.chines[hull_props.active_chine_index]: 
				chine_item = hull_props.chines[hull_props.active_chine_index] 
				row = layout.row() 
				row.prop(chine_item, "name") 

				row = layout.row() 

				row.prop(chine_item, "length") 
				row.prop(chine_item, "width") 
				
				row = layout.row() 
				row.prop(chine_item, "pos") 

				row = layout.row() 
				row.prop(chine_item, "rot") 

				row = layout.row()
				row.prop(chine_item,"symmetrical")

				if len(chine_item.longitudals)>0:

					row = layout.row() 
					layout.label(text="Longitudals") 
					row = layout.row() 
					row.template_list(listtype_name="MY_UL_NameList", 
								list_id="Longitudal_List", 
								dataptr=chine_item,
								propname="longitudals",
								active_dataptr=chine_item, 
								active_propname="active_longitudal_index",
								rows=min_rows
					)

				row = layout.row() 
				row.operator('genui.new_longitudal') 
				row.operator('genui.delete_longitudal') 
			#			scene, "longitudal_properties", scene, "hullgen_longitudal_index") #,type='COMPACT') 

				if chine_item.active_longitudal_index >= 0:
					
					longitudal_item=chine_item.longitudals[chine_item.active_longitudal_index]

					row = layout.row() 
					row.prop(longitudal_item, "name") 

					row = layout.row() 

					row.prop(longitudal_item, "x_min") 
					row.prop(longitudal_item, "x_max") 
					
					row = layout.row() 
					row.prop(longitudal_item, "z_offset") 
					row.prop(longitudal_item, "width") 

		if len(hull_props.keels)>0:
			row = layout.row() 
			layout.label(text="Keels") 
			row = layout.row() 
			row.template_list(listtype_name="MY_UL_NameList", 
						list_id="Keel_List", 
						dataptr=hull_props,
						propname="keels",
						active_dataptr=hull_props, 
						active_propname="active_keel_index",
						rows=min_rows
			)

		#row.template_list("MY_UL_NameList", "Keel_List", scene, "keel_properties", scene, "hullgen_keel_index",type='COMPACT') 
		row = layout.row() 
		row.operator('genui.new_keel') 
		row.operator('genui.delete_keelitem') 

		
		if hull_props.active_keel_index >= 0 and hull_props.keels[hull_props.active_keel_index]: 
			keel_item = hull_props.keels[hull_props.active_keel_index] 

			row = layout.row() 
			row.prop(keel_item, "name") 

			row = layout.row() 
			row.prop(keel_item, "station_start") 
			row.prop(keel_item, "station_end") 

			row = layout.row() 
			row.prop(keel_item, "lateral_offset") 

			row = layout.row()
			row.prop(keel_item, "top_height") 


			

