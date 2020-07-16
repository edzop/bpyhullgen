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

import bpy
  
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import material_helper
from bpyhullgen.hullgen import curve_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import geometry_helper
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.hullgen import render_helper
from bpyhullgen.hullgen import bpy_helper

from math import radians

the_hull=hull_maker.hull_maker(width=3,length=7,height=3)

the_hull.make_hull_object()

new_chine=chine_helper.chine_helper(the_hull)

new_chine.curve_width=1
#new_chine.curve_height=4
new_chine.curve_length=the_hull.hull_length*1.2
new_chine.rotation=[0,0,0]
new_chine.offset=[0,0.35,0]
new_chine.asymmetry[0]=1







#new_longitudal=chine_helper.longitudal_element(z_offset=-0.2,width=-0.13,thickness=0.1)
#new_longitudal.set_limit_x_length(start_bulkhead_location+bulkhead_spacing*bulkhead_count,start_bulkhead_location+end_segment)
#new_chine.add_longitudal_element(new_longitudal)

new_chine.name="side"


new_chine.make_segmented_longitudals(z_offset=-0.2)

#new_chine.clear_longitudal_elements()
#new_chine.curve_twist=[0,-25,-25]
#new_chine.make_chine(twist=[0,1,2])
new_chine.make_chine()



def make_screws():

	screw_objects=[]

	for chine_curve in new_chine.curve_backups:
		for screw_position in new_chine.longitudal_screw_positions:
			bpy.ops.mesh.primitive_cylinder_add(radius=0.0656/2, depth=5, enter_editmode=False, location=[0,0,0])
			screw_object=bpy.context.view_layer.objects.active
			screw_object.name="screw_object_%d_%s"%(screw_position,chine_curve.name)
			print(chine_curve.name)
			screw_object.location.y=0.065
			screw_object.hide_viewport=True
			screw_objects.append(screw_object)

			bpy_helper.move_object_to_collection(new_chine.view_collection_longitudals,screw_object)


			path_follow = screw_object.constraints.new(type='FOLLOW_PATH')
			path_follow.target=chine_curve
			path_follow.use_fixed_location=True

			#curve_overlap=new_chine.curve_length-the_hull.hull_length

			
			curve_length=new_chine.curve_length
			curve_hull_ratio=curve_length/the_hull.hull_length
			
			translated_screw_position=(curve_length/2)+(screw_position*curve_hull_ratio)
			translated_hull_start=curve_length*(curve_hull_ratio-1)/2
			offset_translated_position=translated_screw_position+translated_hull_start

			print("curve length: %f curve extra ratio: %f"%(curve_length,curve_hull_ratio))
			print("screw position: %f tr_screw_pos: %f tr hull start: %f offset tr screw: %f"%(
													screw_position,
													translated_screw_position,
													translated_hull_start,												
													offset_translated_position))

			offset_factor=offset_translated_position/curve_length
			
			path_follow.offset_factor=offset_factor

	for longitudal_element_object in new_chine.longitudal_element_objects:

		for screw_object in screw_objects:
			modifier_name="screwhole_%s"%screw_object.name

			bool_new = longitudal_element_object.modifiers.new(type="BOOLEAN", name=modifier_name)
			bool_new.object = screw_object
			bool_new.operation = 'DIFFERENCE'

make_screws()

new_chine.clear_longitudal_elements()



new_chine.curve_length=the_hull.hull_length*1.1

new_chine.rotation=[-36,0,0]
new_chine.offset=[0,0,-0.84]
new_chine.name="upper"
new_chine.curve_length=the_hull.hull_length*1.3
new_chine.make_chine()

new_chine.curve_length=the_hull.hull_length*1.3
new_chine.rotation=[39,0,0]
new_chine.offset=[0,-0.2,0.331]
new_chine.name="mid"
#new_chine.curve_twist=[0,0,0]
new_chine.make_chine()



new_chine.rotation=[82,0,0]
new_chine.offset=[0,0,0]
new_chine.name="low"
new_chine.curve_length=the_hull.hull_length*1.4
#new_chine.curve_width=1.6
new_chine.asymmetry[1]=0
new_chine.make_chine()
new_chine.asymmetry[1]=0
#new_chine.curve_length=the_hull.hull_length*1.0


new_chine.rotation=[-90,0,0]
new_chine.offset=[0,0,-0.5]
new_chine.name="roof"
new_chine.curve_width=0.8
#new_chine.curve_angle=10
#new_chine.curve_length=13
new_chine.symmetrical=False

#new_chine.longitudal_width=0.15
new_chine.make_chine()


# ================ modify hull


	# ================ Add Pilot House
def add_pilot_house():
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.27) )

	bpy.ops.transform.resize(value=(1,0.9,1))
	bpy.ops.object.transform_apply(scale=True,location=False)


	ob = bpy.context.active_object

	ob.name="Pilot House"

	bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.mode_set(mode='OBJECT')

	for face in ob.data.polygons:
		face.select = geometry_helper.GoingUp( face.normal )

	bpy.ops.object.mode_set(mode='EDIT')

	bpy.ops.transform.resize(value=(1, 0.6, 1))

	bpy.ops.transform.translate(value=(-0.4, 0, 0))

	bpy.ops.mesh.bevel(offset=0.1)

	bpy.ops.object.mode_set(mode='OBJECT')

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(ob)

add_pilot_house()

def add_extras():
	# ================ Add Rudder
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-5.3, 0, -1.25) )

	rudder_object = bpy.context.active_object

	rudder_object.name="Rudder"

	bpy.ops.transform.resize(value=(0.7,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = rudder_object
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(rudder_object)

	# ================ Add Keel
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, 0, -1.25) )

	ob = bpy.context.active_object

	ob.name="Keel"

	bpy.ops.transform.resize(value=(7,0.05,0.8))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_join")
	bool_new.object = ob
	bool_new.operation = 'UNION'

	bpy_helper.hide_object(ob)

	# ================ Add deck cockpit
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.2, 0, 0) )

	ob = bpy.context.active_object

	ob.name="deck_cockpit"

	bpy.ops.transform.resize(value=(3,1,1))
	bpy.ops.object.transform_apply(scale=True,location=False)

	bool_new = the_hull.hull_object.modifiers.new(type="BOOLEAN", name="hull_cut")
	bool_new.object = ob
	bool_new.operation = 'DIFFERENCE'

	bpy_helper.hide_object(ob)


def add_props():
	view_collection_props=bpy_helper.make_collection("props",bpy.context.scene.collection.children)

	import_library_path="assets/actors.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"man.sit_chair",(0,0,-0.6),view_collection_props,rotation=(0,0,0))

	import_library_path="assets/boat_assets.blend/Collection/"
	ob = geometry_helper.import_object(import_library_path,"wheel_axle.8ft",(0,0,-0.96),view_collection_props,rotation=(0,0,0))

#add_props()



levels=[ -0.7]


bulkhead_definitions = []


current_bulkhead_location=the_hull.start_bulkhead_location
for bulkhead_index in range(0,the_hull.bulkhead_count):
	bulkhead_definitions.append([current_bulkhead_location,-0.7,False,the_hull.bulkhead_thickness])
	current_bulkhead_location+=the_hull.bulkhead_spacing


#bulkhead_definitions = [

					#	(5	,False		,False	,bulkhead_thickness),
					#	(4	,levels[1]	,True	,bulkhead_thickness),
					#	(3	,levels[1]	,False	,bulkhead_thickness),
#						(-3	,levels[0]	,False	,bulkhead_thickness),
#						(-2	,levels[0]	,False	,bulkhead_thickness),	
#						(-1	,levels[0]	,False	,bulkhead_thickness),
						
#						(0	,levels[0]	,False	,bulkhead_thickness),
#						(1	,levels[0]	,False	,bulkhead_thickness),
#						(2	,levels[0]	,False	,bulkhead_thickness),
					#	(-3	,levels[1]	,False	,bulkhead_thickness),						
					#	(-4	,levels[1]	,True	,bulkhead_thickness)

					#	(-5,False,False)
#]

#the_hull.cleanup_center(clean_location=[0.0,0,0],clean_size=[4-bulkhead_thickness+the_hull.bool_coplaner_hack,1,1])

station_start=bulkhead_definitions[0][0]-the_hull.bulkhead_thickness
station_end=bulkhead_definitions[len(bulkhead_definitions)-1][0]+the_hull.bulkhead_thickness



#x_locations=[	
#				bulkhead_definitions[0][0],
#				bulkhead_definitions[len(bulkhead_definitions)-1][0]
#			]

#the_hull.cleanup_longitudal_ends(x_locations)

the_hull.make_bulkheads(bulkhead_definitions)
the_hull.make_longitudal_booleans()
the_hull.hull_object.hide_viewport=True

def make_keels():

	overlap_factor=0.2  # 20% overlap

	overlap_distance=the_hull.bulkhead_spacing*overlap_factor #actual overlap distance
	half_overlap_distance=overlap_distance/2
	end_segment_length=the_hull.bulkhead_spacing*1.5+half_overlap_distance
	full_segment_length=the_hull.bulkhead_spacing*2+overlap_distance


	finish_eval_location=2+the_hull.bulkhead_thickness
	current_eval_location=the_hull.start_bulkhead_location-the_hull.bulkhead_thickness
	odd_spacing=True

	keel_middle_space=0.3
	keel_thickness=0.1

	lateral_offset=0
	segment_index=0

	#print("overlap: %f")

	screw_positions=[]
	keel_screws=[]

	while current_eval_location<finish_eval_location:

		if odd_spacing==True:
			lateral_offset=keel_middle_space/2
			odd_spacing=False
		else:
			lateral_offset=keel_middle_space/2-keel_thickness/2
			odd_spacing=True

		if (current_eval_location+full_segment_length<=finish_eval_location) and segment_index!=0:
			print("keelfull length: %f"%current_eval_location)

			the_keel = keel_helper.keel(the_hull,
					lateral_offset=lateral_offset,
					top_height=levels[0],
					station_start=current_eval_location,
					station_end=current_eval_location+full_segment_length)

			the_keel.make_keel(keel_thickness)
			the_hull.integrate_keel(the_keel)

			the_keel = keel_helper.keel(the_hull,
					lateral_offset=-lateral_offset,
					top_height=levels[0],
					station_start=current_eval_location,
					station_end=current_eval_location+full_segment_length)

			the_keel.make_keel(keel_thickness)
			the_hull.integrate_keel(the_keel)

			current_eval_location+=full_segment_length-overlap_distance

			screw_positions.append(current_eval_location+half_overlap_distance)

			print("keelafter length: %f"%current_eval_location)

			# screw_positions.append(current_eval_location-half_overlap_distance)

		elif current_eval_location+end_segment_length<=finish_eval_location: # try end segment
			print("keelhalf length: %f"%current_eval_location)

			if segment_index==0:
				station_end=current_eval_location+end_segment_length
			else:
				station_end=finish_eval_location
				
			the_keel = keel_helper.keel(the_hull,
					lateral_offset=lateral_offset,
					top_height=levels[0],
					station_start=current_eval_location,
					station_end=station_end)

			the_keel.make_keel(keel_thickness)
			the_hull.integrate_keel(the_keel)	

			the_keel = keel_helper.keel(the_hull,
					lateral_offset=-lateral_offset,
					top_height=levels[0],
					station_start=current_eval_location,
					station_end=station_end)

			the_keel.make_keel(keel_thickness)
			the_hull.integrate_keel(the_keel)	

			print("keelafter length: %f"%current_eval_location)

			if segment_index==0:
				current_eval_location+=end_segment_length-overlap_distance
				screw_positions.append(current_eval_location+half_overlap_distance)
			else:
				current_eval_location=finish_eval_location

			#if current_eval_location+end_segment_length>=finish_eval_location:
				
			#else:
				
			#	screw_positions.append(current_eval_location-half_overlap_distance)
	#	else:
	#		# fill the gap with whatever is left and finish
	#		new_longitudal=chine_helper.longitudal_element(z_offset=z_offset,width=-0.13,thickness=segment_thickness)
	#		new_longitudal.set_limit_x_length(current_eval_location,finish_eval_location)
	#		new_chine.add_longitudal_element(new_longitudal)
	#		current_eval_location=finish_eval_location

		segment_index+=1

	for screw_position in screw_positions:
		bpy.ops.mesh.primitive_cylinder_add(radius=0.0656/2, depth=5, enter_editmode=False, location=[0,0,0])
		screw_object=bpy.context.view_layer.objects.active
		screw_object.name="screw_keel_%02.2f"%(screw_position)
		screw_object.location.x=screw_position
		screw_object.location.z=levels[0]-0.1
		bpy.ops.transform.rotate(value=radians(90),orient_axis='X')
		keel_screws.append(screw_object)

		bpy_helper.move_object_to_collection(the_keel.view_keel_collection,screw_object)

		for keel in the_hull.keels:
			if keel.keel_object!=None:

				bool_new = keel.keel_object.modifiers.new(type="BOOLEAN", name="screw%02.2f"%screw_position)
				bool_new.object = screw_object
				bool_new.operation = 'DIFFERENCE'

		screw_object.hide_viewport=True




def disabled_keel():

		keel_middle_space=0.3
		the_keel = keel_helper.keel(the_hull,
				lateral_offset=keel_middle_space/2,
				top_height=levels[0],
				station_start=station_start,
				station_end=station_end)

		the_keel.set_limit_x_length(-1-thickness,1+thickness)

		the_keel.make_keel(keel_thickness)
		the_hull.integrate_keel(the_keel)	

		the_keel = keel_helper.keel(the_hull,
				lateral_offset=-keel_middle_space/2,
				top_height=levels[0],
				station_start=station_start,
				station_end=station_end)

		the_keel.set_limit_x_length(-1-thickness,1+thickness)

		the_keel.make_keel(keel_thickness)
		the_hull.integrate_keel(the_keel)				

def make_fuel_tanks():

	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[0][0]+bulkhead_definitions[0][3]/2,
					x2=bulkhead_definitions[1][0]-bulkhead_definitions[1][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_1L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[0][0]+bulkhead_definitions[0][3]/2,
					x2=bulkhead_definitions[1][0]-bulkhead_definitions[1][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_1R")


	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[1][0]+bulkhead_definitions[1][3]/2,
					x2=bulkhead_definitions[2][0]-bulkhead_definitions[2][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_2L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[1][0]+bulkhead_definitions[1][3]/2,
					x2=bulkhead_definitions[2][0]-bulkhead_definitions[2][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_2R")				


	fuel_tank_1L=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[4][0]+bulkhead_definitions[4][3]/2,
					x2=bulkhead_definitions[5][0]-bulkhead_definitions[5][3]/2,
					y_offset=-(keel_middle_space/2)-the_keel.thickness/2,
					name="fuel_3L")

	fuel_tank_1R=geometry_helper.create_bilgetank(the_hull,
					top=levels[0],
					x1=bulkhead_definitions[4][0]+bulkhead_definitions[4][3]/2,
					x2=bulkhead_definitions[5][0]-bulkhead_definitions[5][3]/2,
					y_offset=(keel_middle_space/2)+the_keel.thickness/2,
					name="fuel_3R")								


make_keels()

framedata=[
[ 1, [2.256688,-9.173357,4.958309],[0.000000,0.000000,0.000000] ],
[ 2, [0.315304,-0.819446,10.211541],[0.000000,0.000000,0.000000] ],
[ 3, [7.223459,-0.424494,0.439452],[0.000000,0.000000,-0.409564] ],
[ 4, [-8.400036,-1.356833,0.990534],[-2.644429,-0.102626,-0.230217] ],
[ 5, [-3.368380,-0.004060,-0.279753],[0.028123,0.029352,-0.230217] ]
]

render_helper.setup_keyframes(framedata)