import bpy
import imp   
 
curve_helper = imp.load_source('util_lux','curve_helper.py')
geometry_helper = imp.load_source('geometry_helper','geometry_helper.py')

theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("bb")
theCurveHelper.extrude_curve(1)

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
 
info_text="A 2D curve with twist on the second axis"
geometry_helper.add_info_text(info_text)

curve_helper = imp.load_source('util_lux','curve_helper.py')
geometry_helper = imp.load_source('geometry_helper','geometry_helper.py')

theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.curve_twist[0]=12
theCurveHelper.curve_twist[1]=6

theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("mm")
theCurveHelper.extrude_curve(1)

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")

info_text="A 3D curve with twist on the third axis"
geometry_helper.add_info_text(info_text)

 
curve_helper = imp.load_source('util_lux','curve_helper.py')

theCurveHelper = curve_helper.Curve_Helper()
theCurveHelper.asymmetry[1]=1
theCurveHelper.define_curve(11,1.2)

theCurveHelper.generate_curve("nn")
theCurveHelper.extrude_curve(1)

wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
 
