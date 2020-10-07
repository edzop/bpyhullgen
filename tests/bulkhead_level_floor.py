import bpy
  
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import bulkhead
from bpyhullgen.hullgen import render_helper
from bpyhullgen.hullgen import bpy_helper


the_hull=hull_maker.hull_maker()
the_hull.make_hull_object()


new_chine=chine_helper.chine_helper(the_hull,
	name="side",
	length=the_hull.hull_length*1.02,
	width=1.2
	)

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="mid",
	length=the_hull.hull_length*1.3,
	width=1.2,
	rotation=[25,0,0],
	offset=[0,0,-0.5],
	)

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="upper",
	length=the_hull.hull_length*1.3,
	width=1.2,
	rotation=[-45,0,0],
	offset=[0,0,-0.5],
	)

the_hull.add_chine(new_chine)


new_chine=chine_helper.chine_helper(the_hull,
	name="low",
	length=the_hull.hull_length*1.5,
	width=1.6,
	offset=[0,0,-0.5],
	rotation=[60,0,0],
	)

the_hull.add_chine(new_chine)

new_chine=chine_helper.chine_helper(the_hull,
	name="roof",
	length=the_hull.hull_length*1.4,
	width=-0.4,
	rotation=[90,0,0],
	offset=[0,0,0.3],
	symmetrical=False
	)

the_hull.add_chine(new_chine)

the_hull.default_floor_height=-1.2
the_hull.start_bulkhead_location=-5
the_hull.bulkhead_spacing=0.3
the_hull.bulkhead_count=27

the_hull.integrate_components()
	
the_hull.hull_object.hide_viewport=True

framedata=[
[ 1, [8.927623,-10.659976,-0.208632],[1.458442,-0.166389,-0.166539] ],
[ 2, [0.460886,-0.961136,14.928463],[0.095418,-0.164318,-0.010775] ],
[ 3, [10.912931,-1.197941,1.075093],[-0.018434,0.001545,-0.917216] ],
[ 4, [-9.482988,-7.800827,0.150181],[-1.413847,0.379426,-0.492896] ],
[ 5, [3.023221,-0.004060,-0.149050],[0.990780,0.029352,-0.437069] ]
]

render_helper.setup_keyframes(framedata)
