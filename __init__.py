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
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
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

    from bpy.props import PointerProperty

    from . import (
            ui
            )



classes = (
    ui.hullgen_Properties,
    ui.OBJECT_PT_bpyhullgen_panel,
    ui.SolidifySelectedObjectsOperator,
    ui.SeparateMaterialOperator,
    ui.GenSceneOperator,
    ui.ApplyAllBoolOperator,
    ui.DeleteAllOperator,
    ui.Export_CSV_Operator,
    ui.ExportPlatesOperator,
    ui.ImportPlatesOperator,
    ui.ExportHulldxfOperator,
    ui.DeleteFacesOperator,
    ui.CutWindowsOperator,
    ui.InsideShrinkOperator,
    ui.AluminumPlatesOperator,
    ui.ShrinkOutlinerOperator,
    ui.MeasureDistanceBetweenVerticesOperator,
    ui.ScaleToSizeOperator
)

from .hullgen import geometry_helper as geometry_helper
from .hullgen import boat_curve_2 as boat_curve
from .hullgen import material_helper as material_helper
from .hullgen import window_helper as window_helper
from .hullgen import measure_helper as measure_helper
from .hullgen import curve_helper as curve_helper

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.hullgen_Props = PointerProperty( type = ui.hullgen_Properties )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hullgen_Props
