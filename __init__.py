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



bl_info = {
    "name": "bpyhullgen",
    "description": "Parametric BoatCurve",
    "author": "Ed Kraus",
    "version": (0, 0, 4),
    "blender": (2, 90, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "https://edzop.github.io/bpyhullgen/",
    "tracker_url": "",
    "category": "Development"
}

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

from . import hullgen


if "bpy" in locals():
    import importlib
    importlib.reload(ui)
else:

    import bpy

    from bpy.props import PointerProperty,CollectionProperty,IntProperty

    from . import (
            ui,
            genui
            )

classes = (

    ui.hullgen_Properties,

    genui.hullgendef_keel_Properties,
    genui.hullgendef_longitudal_Properties,
    genui.hullgendef_chine_Properties,
    genui.hullgendef_bulkhead_Properties,
    genui.hullgendef_modshape_Properties,
    genui.hullgendef_hull_Properties,


    genui.WM_OT_auto_bulkheads,
    
    genui.LIST_OT_NewModshapeItem,
    genui.LIST_OT_DeleteModshapeItem,

    genui.hullgendef_file_Properties,

    genui.LIST_OT_NewChineItem,
    genui.LIST_OT_DeleteChineItem,

    genui.LIST_OT_DeleteLongitudalItem,
    genui.LIST_OT_NewLongitudalItem,

    genui.LIST_OT_NewKeelItem,
    genui.LIST_OT_DeleteKeelItem,

    genui.LIST_OT_NewBulkheadItem,
    genui.LIST_OT_DeleteBulkheadItem,

    genui.MY_UL_NameList,
    genui.FILE_UL_List,
    genui.STATION_UL_List,
    genui.OBJECT_PT_bpyhullgendef_panel,
    genui.OBJECT_PT_bpyhullgendef_load_save_panel,
    genui.LIST_OT_GenHull,
    genui.LIST_OT_DeleteHull,
    genui.LIST_OT_SaveConfig,
    genui.LIST_OT_LoadConfig,
    genui.LIST_OT_Newconfig,
    genui.LIST_OT_RefreshConfig,

    ui.OBJECT_PT_bpyhullgen_panel,
    ui.SolidifySelectedObjectsOperator,
    ui.SeparateMaterialOperator,
    ui.GenSceneOperator,
    ui.ApplyAllBoolOperator,
    ui.DeleteAllOperator,
    ui.Export_CSV_Operator,
    ui.ExportPlatesOperator,
    ui.ImportPlatesOperator,
    ui.FlattenPlatesOperator,
    ui.ExportHulldxfOperator,
    ui.DeleteFacesOperator,
    ui.CutWindowsOperator,
    ui.InsideShrinkOperator,
    ui.AluminumPlatesOperator,
    ui.ShrinkOutlinerOperator,
    ui.MeasureDistanceBetweenVerticesOperator,
    ui.ScaleToSizeOperator,
    ui.CleanupMeshesOperator,
    ui.MeasureEdgesOperator
)

from .hullgen import geometry_helper as geometry_helper
from .bpyutils import material_helper as material_helper
from .hullgen import window_helper as window_helper
from .bpyutils import measure_helper as measure_helper
from .hullgen import curve_helper as curve_helper
from .hullgen import hull_maker as hull_maker

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.hullgen_Props = PointerProperty( type = ui.hullgen_Properties )

    the_hull = hull_maker.hull_maker()

    bpy.types.Scene.the_hull = the_hull

    bpy.types.Scene.hull_properties = PointerProperty( type = genui.hullgendef_hull_Properties )

    bpy.types.Scene.hullgen_file_properties = CollectionProperty( type = genui.hullgendef_file_Properties )
    bpy.types.Scene.hullgen_file_index = IntProperty(name = "Index for hullgen_file_properties", default = 0)



def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hull_properties
    del bpy.types.Scene.hullgen_file_properties
    del bpy.types.Scene.the_hull
