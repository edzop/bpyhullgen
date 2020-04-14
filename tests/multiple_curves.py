import bpy
  
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import geometry_helper

text_offset=(-5,-2.44,0)

theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("bb")
theCurveHelper.extrude_curve(1)

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
 
newtxt=geometry_helper.add_info_text("A 2D curve")
newtxt.parent=theCurveHelper.curve_object
newtxt.location=text_offset

# ==========================================
theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.curve_twist[0]=12
theCurveHelper.curve_twist[1]=6

theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("mm")
theCurveHelper.extrude_curve(1)
theCurveHelper.curve_object.location.y=-3

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")

newtxt=geometry_helper.add_info_text("twist[0]=12 twist[1]=6")
newtxt.parent=theCurveHelper.curve_object
newtxt.location=text_offset


# =========================================
theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.asymmetry[1]=1
theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("nn")
theCurveHelper.extrude_curve(1)
theCurveHelper.curve_object.location.y=3

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
 
newtxt=geometry_helper.add_info_text("asymmetry[1]=1")
newtxt.parent=theCurveHelper.curve_object
newtxt.location=text_offset