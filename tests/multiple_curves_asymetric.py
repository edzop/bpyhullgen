import bpy
  
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import geometry_helper

text_offset=(-5,-2.44,0)


for a in curve_helper.frange(0,1,0.2):
    # =========================================
    theCurveHelper = curve_helper.Curve_Helper()
    theCurveHelper.asymmetry[1]=a
    theCurveHelper.define_curve(11,1)

    print(a)

    theCurveHelper.generate_curve("nn"+str(a))
    theCurveHelper.extrude_curve(1)
    theCurveHelper.curve_object.location.y=-3+a*10
    
    wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
    
    #newtxt=geometry_helper.add_info_text("asymmetry[1]=1")
    #newtxt.parent=theCurveHelper.curve_object
    #text_offset[1]=a*2
    #newtxt.location=text_offset
    