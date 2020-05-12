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

from .hullgen import geometry_helper as geometry_helper
from .hullgen import boat_curve_2 as boat_curve
from .hullgen import material_helper as material_helper
from .hullgen import window_helper as window_helper
from .hullgen import measure_helper as measure_helper
from .hullgen import curve_helper as curve_helper

from bpy.props import (StringProperty,
					BoolProperty,
					IntProperty,
					FloatProperty,
					FloatVectorProperty,
					EnumProperty,
					PointerProperty,
					)

from bpy.types import (Panel,
					Operator,
					PropertyGroup,
					)



# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------

class MyProperties (PropertyGroup):

	hull_weight : FloatProperty(
		name = "HullWeight",
		description = "Gross Weight of Hull (KG)",
		default = 250,
		min = 0.01,
		max = 50000.0
		)

	output_csv : BoolProperty(
		name="Output CSV",
		description="Output hydro.csv file containing simulation data",
		default = True
    )

	simulate_depth : BoolProperty(
		name="Sim Depth",
		description="Simulate Depth (sinking)",
		default = True
    )

	simulate_pitch : BoolProperty(
		name="Sim Pitch",
		description="Simulate Pitch (Y Axis)",
		default = True
    )

	simulate_roll : BoolProperty(
		name="Sim Roll",
		description="Simulate Roll (X Axis)",
		default = True
    )


# ------------------------------------------------------------------------
#    Build
# ------------------------------------------------------------------------

class GenSceneOperator (bpy.types.Operator):
	"""Quick generate background scene for rendering"""
	bl_idname = "wm.genscene"
	bl_label = "GenScene"

	def execute(self, context):

		backdrop=geometry_helper.make_backdrop()
		mat = material_helper.make_metalic_material("backdrop",[.6,.6,.6,1])
		material_helper.assign_material(backdrop,mat)

		return {'FINISHED'}


# ------------------------------------------------------------------------
#    Apply All Bool
# ------------------------------------------------------------------------

class ApplyAllBoolOperator (bpy.types.Operator):
	"""Applies all boolean modifiers for each object in scene while assigning unique material for each boolean modifer for further identification of faces after modifier is applied"""
	bl_idname = "wm.apply_all_bool"
	bl_label = "ApplyAllBool"

	def execute(self, context):

		print("Apply All Bool")

		geometry_helper.apply_all_bool_modifiers()

	 
		return {'FINISHED'}


### TODO ADD bpy.ops.mesh.separate(type='SELECTED') operator

# ------------------------------------------------------------------------
#    Export Data
# ------------------------------------------------------------------------

class Export_CSV_Operator (bpy.types.Operator):
	"""Exports hull data into CSV file in same directory with name of blender file"""
	bl_idname = "wm.exportcsv"
	bl_label = "exportCSV"

	def execute(self, context):

		measure_helper.exportCSV()

		return {'FINISHED'}



# ------------------------------------------------------------------------
#    DeleteAll
# ------------------------------------------------------------------------

class DeleteAllOperator (bpy.types.Operator):
	"""Delete all objects except Lights, Cameras, and Empty - useful when regenerating new boat from script"""
	bl_idname = "wm.deleteall"
	bl_label = "DeleteAll"

	def execute(self, context):

		print("DeleteAll")

		for obj in bpy.data.objects:
			if obj.type!="CAMERA":
				if obj.type!="LIGHT":
					if obj.type!="EMPTY":
						bpy.data.objects.remove(obj)    
	
		return {'FINISHED'}



# ------------------------------------------------------------------------
#    Measure Area All
# ------------------------------------------------------------------------

class MeasureAreaSelectedOperator (bpy.types.Operator):
	"""Measure the area of all faces in selected object"""
	bl_idname = "wm.measure_area_all"
	bl_label = "AllFaces"

	def execute(self, context):

		obj = bpy.context.active_object
		face_data=measure_helper.measure_selected_faces_area(obj,True)

		self.report({'INFO'}, "faces %d: area %f"%(face_data[0],face_data[1]))

		return {'FINISHED'}

# ------------------------------------------------------------------------
#    Measure Area Selected
# ------------------------------------------------------------------------

class MeasureAreaAllOperator (bpy.types.Operator):
	"""Measure the area of selected faces in selected object"""
	bl_idname = "wm.measure_area_selected"
	bl_label = "SelectedFaces"

	def execute(self, context):

		obj = bpy.context.active_object
		face_data=measure_helper.measure_selected_faces_area(obj,False)

		self.report({'INFO'}, "faces %d: area %f"%(face_data[0],face_data[1]))

		return {'FINISHED'}


class MeasureVolumeOperator (bpy.types.Operator):
	"""Measure the volume of selected object"""
	bl_idname = "wm.measure_volume"
	bl_label = "MeasureVolume"

	def execute(self, context):

		obj = bpy.context.active_object
		volume=measure_helper.measure_object_volume(obj)

		self.report({'INFO'}, "Volume: %f"%volume)

		return {'FINISHED'}


# ------------------------------------------------------------------------
#    SeparateSolidify
# ------------------------------------------------------------------------

class SeparateMaterialOperator (bpy.types.Operator):
	"""Separate active object into new objects based on material"""
	bl_idname = "wm.separatematerial"
	bl_label = "Separate by material"

	def execute(self, context):

		geometry_helper.separate_active_by_material()

		return {'FINISHED'}

class SolidifySelectedObjectsOperator (bpy.types.Operator):
	"""Solidify each selected object"""
	bl_idname = "wm.solidifyselections"
	bl_label = "Solidify Selections"

	def execute(self, context):

		geometry_helper.solidify_selected_objects()

		return {'FINISHED'}


class CutWindowsOperator (bpy.types.Operator):
	"""Cut window holes for all objects in windows collection"""
	bl_idname = "wm.cutwindows"
	bl_label = "Cut Windows"

	def execute(self, context):

		window_helper.cut_windows()

		return {'FINISHED'}		

class ExportPlatesOperator (bpy.types.Operator):
	"""Export plate geometry to SVG file"""
	bl_idname = "wm.exportplates"
	bl_label = "ExportPlates"

	def execute(self, context):

		measure_helper.export_plates("plates2.svg")

		return {'FINISHED'}


class ExportHulldxfOperator (bpy.types.Operator):
	"""Export plate geometry to DXF file"""
	bl_idname = "wm.exporthulldxf"
	bl_label = "ExportDXF"

	def execute(self, context):

		measure_helper.export_dxf("plates2.dxf")

		return {'FINISHED'}



class DeleteNonFrontalOperator (bpy.types.Operator):
	"""Delete non frontal faces"""
	bl_idname = "wm.delete_non_frontal"
	bl_label = "DeleteNonFront"

	def execute(self, context):

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				#geometry_helper.delete_non_forward_faces(obj)
				geometry_helper.mesh_deselect_all()
				geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_front)

		return {'FINISHED'}

class DeleteNonUpOperator (bpy.types.Operator):
	"""Delete non up faces"""
	bl_idname = "wm.delete_non_up"
	bl_label = "DeleteNonUp"

	def execute(self, context):

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				geometry_helper.mesh_deselect_all()
				geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_up)

		return {'FINISHED'}


class CalculateCGOperator (bpy.types.Operator):
	"""Calculate CG of selected objects"""
	bl_idname = "wm.calculate_cg"
	bl_label = "Calc CG"

	def execute(self, context):

		influence_object_list=[]

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				influence_object_list.append(obj)
		
		measure_helper.calculate_cg(influence_object_list)


		return {'FINISHED'}


class RollTestOperator (bpy.types.Operator):
	"""RollTest - Calculate righting moment"""
	bl_idname = "wm.rolltest"
	bl_label = "RollTest"

	def execute(self, context):

		mytool = context.scene.my_tool

		hull_object=bpy.context.active_object

		csv_file=None

		if mytool.output_csv==True:
			csv_file="hydro.csv"

		
		force_roll_max=80
			
		measure_helper.submerge_boat(hull_object,
			mytool.hull_weight,mytool.simulate_depth,
			mytool.simulate_pitch,
			False,
			force_roll_max,
			csv_file)

		return {'FINISHED'}


class SubmergeOperator (bpy.types.Operator):
	"""Float boat according to CG"""
	bl_idname = "wm.submerge"
	bl_label = "Submerge"

	def execute(self, context):

		mytool = context.scene.my_tool

		print("Weight:", mytool.hull_weight)

		hull_object=bpy.context.active_object

		csv_file=None

		if mytool.output_csv==True:
			csv_file="hydro.csv"
		
		measure_helper.submerge_boat(hull_object,
			mytool.hull_weight,mytool.simulate_depth,
			mytool.simulate_pitch,
			mytool.simulate_roll,
			0,
			csv_file)

		return {'FINISHED'}

class ImportPlatesOperator (bpy.types.Operator):
	"""Import plate geometry from SVG file"""
	bl_idname = "wm.importplates"
	bl_label = "ImportPlates"

	def execute(self, context):

		measure_helper.import_plates("plates2.svg")

		return {'FINISHED'}


class AluminumPlatesOperator (bpy.types.Operator):
	"""Import plate geometry from SVG file"""
	bl_idname = "wm.aluminumplates"
	bl_label = "AL Plates"

	def execute(self, context):

		material_helper.plates_to_aluminum()

		return {'FINISHED'}

class InsideShrinkOperator (bpy.types.Operator):
	"""Shrink faces in orient by normals"""
	bl_idname = "wm.insideshrink"
	bl_label = "InShrink"

	def execute(self, context):

		geometry_helper.inside_shrink()

		return {'FINISHED'}

class ShrinkOutlinerOperator (bpy.types.Operator):
	"""Collapse outliner tree hierarchy"""
	bl_idname = "wm.shrinkoutliner"
	bl_label = "OLShrink"

	def execute(self, context):

		geometry_helper.collapse_outliner_hiearchy()

		return {'FINISHED'}



# ------------------------------------------------------------------------
#    my tool in objectmode
# ------------------------------------------------------------------------

class OBJECT_PT_my_panel (Panel):

	bl_label = "bpyHullGen"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "bpyHullGen"


	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		row = layout.row()
		row.label(text="Measure:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.measure_area_selected")
		rowsub.operator( "wm.measure_area_all")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.measure_volume")
		rowsub.operator( "wm.calculate_cg")
		
		
		
		row = layout.row()
		row.label(text="Hydrostatics:")
		rowsub = layout.row(align=True)
		layout.prop( mytool, "hull_weight")
		layout.prop( mytool, "output_csv")
		layout.prop( mytool, "simulate_roll")
		layout.prop( mytool, "simulate_pitch")
		layout.prop( mytool, "simulate_depth")
		rowsub.operator( "wm.submerge")
		rowsub.operator( "wm.rolltest")

		row = layout.row()
		row.label(text="Output:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.exportcsv")
		rowsub.operator( "wm.exportplates")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.exporthulldxf")

		row = layout.row()
		row.label(text="Import:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.importplates")

		row = layout.row()
		row.label(text="Scene:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.deleteall")
		rowsub.operator( "wm.genscene")

		row = layout.row()
		row.label(text="Modify:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.solidifyselections")
		rowsub.operator( "wm.separatematerial")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.apply_all_bool")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.delete_non_frontal")
		rowsub.operator( "wm.delete_non_up")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.cutwindows")
		rowsub.operator( "wm.aluminumplates")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.insideshrink")
		rowsub.operator( "wm.shrinkoutliner")

		#layout.menu( "OBJECT_MT_select_test", text="Presets", icon="SCENE")
		
