import bpy
  
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import render_helper
from bpyhullgen.hullgen import bpy_helper

text_offset=(-5,-2.44,0)


for a in bpy_helper.frange(0,1,0.2):
    # =========================================
    theCurveHelper = curve_helper.Curve_Helper()
    theCurveHelper.asymmetry[1]=a
    theCurveHelper.define_curve(11,1)

    print(a)

    theCurveHelper.generate_curve("nn"+str(a))
    theCurveHelper.extrude_curve(1)
    theCurveHelper.curve_object.location.y=-3+a*10
    
    wireframe = theCurveHelper.curve_object.modifiers.new(type="WIREFRAME", name="wireframe")
    
framedata=[
[ 1, [0.000000,-1.362492,27.603287],[0.000000,0.196316,-0.509545] ],
[ 2, [19.154360,5.335245,12.450815],[1.170676,-0.401701,-0.356683] ]
]

render_helper.setup_keyframes(framedata)
