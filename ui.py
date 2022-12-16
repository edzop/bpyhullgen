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
from .bpyutils import material_helper as material_helper
from .hullgen import window_helper as window_helper
from .bpyutils import measure_helper as measure_helper
from .hullgen import import_export_helper as import_export_helper
from .hullgen import unfold_helper as unfold_helper
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
					PropertyGroup
					)



# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------


class hullgen_Properties (PropertyGroup):


	cleanup_options=[ 
				('auto', 'Auto', ""),
				('front', 'Front', ""),
				('back', 'Back', ""),
				('left', "Left", ""),
				('right', "Right", ""),
				('up', "Up", ""),
				('down', "Down", "")
			   ]

	cleanup_choice: EnumProperty(
		items=cleanup_options,
		description="Keep faces facing this direction",
		name="keep",
		default="auto"
	)

	hull_weight : FloatProperty(
		name = "HullWeight",
		description = "Gross Weight of Hull (KG)",
		default = 250,
		min = 0.01,
		max = 50000.0
		)

	scale_to_distance : FloatProperty(
		name = "ScaleTo",
		description = "Scale all objects so distance between 2 vertices is exactly this number",
		default = 1,
		min = 0.01,
		max = 50000.0
		)

	solidify_thickness : FloatProperty(
		name = "Thickness",
		description = "Solidify Thickness",
		default = 0.003,
		min = -10,
		max = 10
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
#    Apply All Bool
# ------------------------------------------------------------------------

class ApplyAllBoolOperator (bpy.types.Operator):
	"""Applies all boolean modifiers for each object in scene while assigning unique material for each boolean modifier for further identification of faces after modifier is applied"""
	bl_idname = "wm.apply_all_bool"
	bl_label = "ApplyAllBool"

	def execute(self, context):

		geometry_helper.apply_all_bool_modifiers()

	 
		return {'FINISHED'}


# ------------------------------------------------------------------------
#    Export Data
# ------------------------------------------------------------------------

class Export_CSV_Operator (bpy.types.Operator):
	"""Exports hull data into CSV file in same directory with name of blender file"""
	bl_idname = "wm.exportcsv"
	bl_label = "exportCSV"

	def execute(self, context):

		import_export_helper.exportCSV()

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
#    DeleteAll
# ------------------------------------------------------------------------

class CleanupMeshesOperator (bpy.types.Operator):
	"""Delete all loose vertices and recalculate normals for all meshes"""
	bl_idname = "wm.cleanupmeshes"
	bl_label = "CleanupAll"

	def execute(self, context):

		geometry_helper.cleanup()

		return {'FINISHED'}


class HollowOutOperator (bpy.types.Operator):
	"""Hollow out a mesh by deleting any edges that are not exterior"""
	bl_idname = "wm.hollowout"
	bl_label = "Hollow"

	@classmethod
	def poll(cls, context):
		return context.selected_objects is not None

	def execute(self, context):

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				geometry_helper.hollowout_mesh(obj)

		return {'FINISHED'}


# ------------------------------------------------------------------------
#    SeparateSolidify
# ------------------------------------------------------------------------

class SeparateMaterialOperator (bpy.types.Operator):
	"""Separate active object into new objects based on material"""
	bl_idname = "wm.separatematerial"
	bl_label = "SeparateMat"

	@classmethod
	def poll(cls, context):
		return context.selected_objects is not None

	def execute(self, context):

		geometry_helper.separate_active_by_material()

		return {'FINISHED'}

class SolidifySelectedObjectsOperator (bpy.types.Operator):
	"""Solidify each selected object to hull material thickness"""
	bl_idname = "wm.solidifyselections"
	bl_label = "Solidify Selections"

	@classmethod
	def poll(cls, context):
		return context.selected_objects is not None

	def execute(self, context):

		mytool = context.scene.hullgen_Props

#		print("Weight:", mytool.scale_to_distance)

		geometry_helper.solidify_selected_objects(thickness=mytool.solidify_thickness)

		return {'FINISHED'}


class CutWindowsOperator (bpy.types.Operator):
	"""Cut window holes for all objects in windows collection"""
	bl_idname = "wm.cutwindows"
	bl_label = "Cut Windows"

	def execute(self, context):

		window_helper.cut_windows()

		return {'FINISHED'}		



class UnfoldOperator (bpy.types.Operator):

	"""Flatten plate for fabrication (laser cut or CNC router)"""
	bl_idname = "wm.unfold"
	bl_label = "Unfold"

	@classmethod
	def poll(cls, context):
		return context.selected_objects is not None

	def execute(self, context):

		unfolder = unfold_helper.flatten_helper()

		summary = unfolder.unfold_plates()

		self.report({'INFO'}, "-  %s"%(summary))

		return {'FINISHED'}




class ExportHulldxfOperator (bpy.types.Operator):
	"""Export plate geometry to DXF file"""
	bl_idname = "wm.exporthulldxf"
	bl_label = "ExportDXF"

	def execute(self, context):

		if measure_helper.export_dxf("plates2.dxf") is False:
			self.report({'INFO'}, "DXF export failed - check export DXF addon is installed?")

		return {'FINISHED'}


class DeleteFacesOperator (bpy.types.Operator):
	"""LaserClean - Delete all faces not complying with normal direction in preparation for laser cutting"""
	bl_idname = "wm.flatten_faces"
	bl_label = "LaserClean"

	def execute(self, context):

		mytool = context.scene.hullgen_Props

		cleanup_choice=mytool.cleanup_choice

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				geometry_helper.mesh_deselect_all()

				if cleanup_choice=="left":
					geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_left)
				if cleanup_choice=="right":
					geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_right)
				elif cleanup_choice=="up":
					geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_up)
				elif cleanup_choice=="front":
					geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_front)
				elif cleanup_choice=="back":
					geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_back)
				elif cleanup_choice=="auto":
					if obj.name.startswith("Keel."):
						geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_left)
					elif obj.name.startswith("Bulkhead."):
						geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_front)
					elif obj.name.startswith("cutterchine_"):
						geometry_helper.delete_non_aligned_faces(obj,geometry_helper.select_going_up)


		return {'FINISHED'}


class BendStressOperator (bpy.types.Operator):
	"""Calculate and show bend stress on plates"""
	bl_idname = "wm.bendstress"
	bl_label = "BendStress"

	def execute(self, context):

		vertex_material=material_helper.get_material_vertex_colors()

		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				measure_helper.calculate_bend_stress(obj)
				material_helper.assign_material(obj,vertex_material)

		return {'FINISHED'}


class AluminumPlatesOperator (bpy.types.Operator):
	"""Assign aluminum material to plates"""
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

class MeasureDistanceBetweenVerticesOperator (bpy.types.Operator):
	"""Measure distance between 2 selected points"""
	bl_idname = "wm.measure_two_vertice_distance"
	bl_label = "MeasurePoints"

	def execute(self, context):

		distance = measure_helper.get_distance_between_two_selected_points()

		self.report({'INFO'}, "Distance %f: "%(distance))

		return {'FINISHED'}

class MeasureEdgesOperator (bpy.types.Operator):
	"""Measure edges for all selected objects"""
	bl_idname = "wm.measureedges"
	bl_label = "MeasureEdges"

	@classmethod
	def poll(cls, context):
		return context.selected_objects is not None

	def execute(self, context):

		length = measure_helper.measure_selected_edges()

		self.report({'INFO'}, "Length %f: "%(length))

		return {'FINISHED'}

class ScaleToSizeOperator (bpy.types.Operator):
	"""Scale all mesh objects so distance between 2 selected points is specific size"""
	bl_idname = "wm.scale_to_size"
	bl_label = "ScaleTo"

	def execute(self, context):

		mytool = context.scene.hullgen_Props

#		print("Weight:", mytool.scale_to_distance)

		measure_helper.scale_to_size(mytool.scale_to_distance)

		return {'FINISHED'}



# ------------------------------------------------------------------------
# Utility Panel
# ------------------------------------------------------------------------

class OBJECT_PT_utility_panel (Panel):

	bl_label = "Utility"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "bpyHullGen"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.hullgen_Props
		
		row = layout.row()
		row.label(text="Measure:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.measureedges")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.measure_two_vertice_distance")
		layout.prop( mytool, "scale_to_distance")
		rowsub.operator( "wm.scale_to_size")
		

		row = layout.row()
		row.label(text="Scene:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.deleteall")

		row = layout.row()
		row.label(text="Modify:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.solidifyselections")
		layout.prop( mytool, "solidify_thickness")


		rowsub = layout.row(align=True)
		rowsub.operator( "wm.bendstress")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.insideshrink")
		rowsub.operator( "wm.shrinkoutliner")

		rowsub = layout.row(align=True)
		rowsub.operator( "wm.cutwindows")
		rowsub.operator( "wm.aluminumplates")





# ------------------------------------------------------------------------
# Production Panel
# ------------------------------------------------------------------------

class OBJECT_PT_production_panel (Panel):

	bl_label = "Production"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "bpyHullGen"

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.hullgen_Props
		
		row = layout.row()
		row.label(text="Output:")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.apply_all_bool")		
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.separatematerial")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.unfold")
		rowsub = layout.row(align=True)
		rowsub.operator("wm.flatten_faces")
		layout.prop( mytool, "cleanup_choice", text="Keep") 

		rowsub = layout.row(align=True)
		rowsub.operator( "wm.cleanupmeshes")
		rowsub.operator( "wm.hollowout")
		
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.exportcsv")
		rowsub = layout.row(align=True)
		rowsub.operator( "wm.exporthulldxf")

