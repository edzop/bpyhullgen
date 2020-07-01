
from bpyhullgen.hullgen import window_helper
from bpyhullgen.hullgen import render_helper

window_helper.make_window(centerpoint=(-5,-3,0),diameter=2)
window_helper.make_window(centerpoint=(4,-3,0),diameter=1)

window_helper.make_window("w3",centerpoint=(0,3,0),diameter=3)

framedata=[
[ 1, [1.018093,-5.219674,35.031399],[-0.386264,0.628492,0.313842] ],
[ 2, [5.250247,-15.370146,6.993764],[1.146949,0.000000,-0.653979] ]
]

render_helper.setup_keyframes(framedata)
