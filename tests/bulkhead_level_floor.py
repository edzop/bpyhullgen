import bpy
  
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import bulkhead
from bpyhullgen.hullgen import render_helper


def make_chines(the_hull):

	new_chine=chine_helper.chine_helper(the_hull)

	new_chine.rotation=[0,0,0]
	new_chine.offset=[0,0,0]
	new_chine.name="top"
	new_chine.make_chine()

	new_chine.rotation=[25,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="mid"
	new_chine.make_chine()

	new_chine.rotation=[-45,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="upper"
	new_chine.make_chine()

	new_chine.rotation=[72,0,0]
	new_chine.offset=[0,0,-0.5]
	new_chine.name="low"
	new_chine.make_chine()

	new_chine.rotation=[90,0,0]
	new_chine.offset=[0,0,0.3]
	new_chine.name="roof"
	new_chine.curve_width=-0.4
	new_chine.curve_length=13
	new_chine.symmetrical=False
	new_chine.make_chine()

the_hull=hull_maker.hull_maker()

the_hull.make_hull_object()

make_chines(the_hull)


# =========================================
# Make bulkheads
edge_offset=0.18

# can use static station list instead of frange
#hull_stations=[ -the_hull.hull_length/2+edge_offset, -1.7, -1.5, 0, 1.5, 1.7, the_hull.hull_length/2-edge_offset]


bulkhead_definitions=[]
for station_position in bpy_helper.frange(-the_hull.hull_length/2+edge_offset,the_hull.hull_length/2-edge_offset,0.4):

	bulkhead_definitions.append([station_position,-0.9,False,0.1])

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()
	
the_hull.hull_object.hide_viewport=True
#the_hull.hull_object.hide_render=True

framedata=[
[ 1, [8.927623,-10.659976,-0.208632],[1.458442,-0.166389,-0.166539] ],
[ 2, [0.460886,-0.961136,14.928463],[0.095418,-0.164318,-0.010775] ],
[ 3, [10.912931,-1.197941,1.075093],[-0.018434,0.001545,-0.917216] ],
[ 4, [-9.482988,-7.800827,0.150181],[-1.413847,0.379426,-0.492896] ],
[ 5, [3.023221,-0.004060,-0.149050],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)
