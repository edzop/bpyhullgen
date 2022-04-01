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
import math
from math import radians, degrees
import bmesh
import itertools

from ..hullgen import curve_helper
from ..bpyutils import material_helper
from ..hullgen import curve_helper
from ..hullgen import chine_helper
from ..hullgen import bulkhead
from ..hullgen import keel_helper
from ..hullgen import geometry_helper
from ..bpyutils import bpy_helper
from bpyhullgen.hullgen import prop_helper

class hull_maker:
	hull_length=11.4
	hull_width=3.9
	hull_height=3.6

	make_bulkheads=True
	make_keels=True
	make_longitudinals=True
	hide_hull=False
		
	default_floor_height=-0.7

	hull_name="hull_object"
	cleaner_collection_name="cleaner"
	modshape_collection_name="modshapes"

	hull_object=None

	hull_core_object=None

	curve_resolution=24
	
	chine_list=None

	# this will be inherited by members
	structural_thickness=0.06

	# oversize the slicer width slightly so it's not such a tight fit in real life
	# or else you need a hammer to assemble it. 
	slicer_overcut_ratio=1.1

	slot_gap=0

	bulkhead_instances=None
	keel_list=None
	props=None

	bulkhead_definitions=None

	modshapes=None

	# Objects that are subtracted from hull to modify final shape
	subtractive_objects=None


	# longitudinal spacing is based on bulkheads
	bulkhead_spacing=1.0

	start_bulkhead_location=-3
	bulkhead_count=0
	bulkhead_thickness=0.05

	# output scale for fabrication = 1:16 = 1/16 = 0.0625
	hull_output_scale=1

	# screw size in MM
	target_screw_size=10 # target size in output model

	
	def clear_all(self):

		# A temporary list of things to delete
		delete_list=[]

		if self.hull_object != None:
			delete_list.append(self.hull_object)

		if self.hull_core_object != None:
			delete_list.append(self.hull_core_object)

		for modshape in self.modshapes:
			for mod_object in modshape.mod_objects:
				delete_list.append(mod_object)


		for bh in self.bulkhead_instances:
			delete_list.append(bh.bulkhead_floor_object)
			delete_list.append(bh.bulkhead_object)

			if bh.bulkhead_overcut_object!=None:
				delete_list.append(bh.bulkhead_overcut_object)


		for chine in self.chine_list:

			for chine_instance in itertools.chain(chine.chine_instances,chine.chine_core_instances):
				delete_list.append(chine_instance.curve_object)
				delete_list.append(chine_instance.curve_backup)
				
				for lg in chine_instance.longitudinal_slicers:
					delete_list.append(lg)

				for lg in chine_instance.longitudinal_slicers_slot_gap_objects:
					delete_list.append(lg)

				for lg in chine_instance.longitudinal_slicers_end_cut_objects:
					delete_list.append(lg)

				for lg in chine_instance.longitudinal_objects:
					delete_list.append(lg)

		for keel in self.keel_list:
			delete_list.append(keel.keel_slicer_object)
			delete_list.append(keel.keel_object)

			if keel.keel_slicer_slot_gap_object!=None:
				delete_list.append(keel.keel_slicer_slot_gap_object)

		
		if len(delete_list) > 0:
			#print("Delete:%s"%delete_list)
			bpy.ops.object.select_all(action='DESELECT')

			objs = bpy.data.objects

			for ob in delete_list:
				if ob is not None:
					try: 
						objs.remove(ob, do_unlink=True)
					except:
						print("Object already removed!")

		self.hull_object=None
		self.hull_core_object=None

		self.keel_list.clear()
		self.bulkhead_definitions.clear()
		self.chine_list.clear()
		self.props.clear()
		self.bulkhead_instances.clear()
		self.subtractive_objects.clear()

		self.modshapes.clear()
	

	def __init__(self,length=11.4,width=3.9,height=3.6):

		self.keel_list=[]
		self.bulkhead_definitions=[]
		self.chine_list=[]
		self.props=[]
		self.bulkhead_instances=[]
		self.subtractive_objects=[]

		self.modshapes=[]


		self.hull_height=height
		self.hull_length=length
		self.hull_width=width

	def add_chine(self,new_chine):
		self.chine_list.append(new_chine)

	def add_subtractive_object(self,object):
		self.subtractive_objects.append(object)


	def make_hull_object(self):
		self.hull_object=geometry_helper.make_cube(self.hull_name,size=(self.hull_length, self.hull_width, self.hull_height))

		hull_core_name="%s_core"%self.hull_name
		self.hull_core_object=geometry_helper.make_cube(hull_core_name,size=(self.hull_length, self.hull_width, self.hull_height))

		#self.hull_object.display_type="WIRE"
		


		material_helper.assign_material(self.hull_object,material_helper.get_material_hull())
		material_helper.assign_material(self.hull_core_object,material_helper.get_material_bool())


		view_collection_hull=bpy_helper.make_collection("hull",bpy.context.scene.collection.children)
		
		bpy_helper.move_object_to_collection(view_collection_hull,self.hull_object)
		bpy_helper.move_object_to_collection(view_collection_hull,self.hull_core_object)


	def add_modshape(self,modshape):
		self.modshapes.append(modshape)

	def make_modshapes(self):
		for modshape in self.modshapes:
			modshape.generate_modshape(self)

			view_collection_modshape=bpy_helper.make_collection(self.modshape_collection_name,bpy.context.scene.collection.children)

			for mod_object in modshape.mod_objects:
				bpy_helper.move_object_to_collection(view_collection_modshape,mod_object)


	def add_bulkhead_definition(self,bulkhead_definition):
		self.bulkhead_definitions.append(bulkhead_definition)


	def add_auto_bulkheads(self):

		current_bulkhead_location=self.start_bulkhead_location
		for bulkhead_index in range(0,self.bulkhead_count):
			watertight=False
			floor_height=self.default_floor_height

			new_bulkhead_definition=bulkhead.bulkhead_definition(
				station=current_bulkhead_location,
				watertight=watertight,
				floor_height=floor_height,
				thickness=self.bulkhead_thickness
			)

			self.add_bulkhead_definition(new_bulkhead_definition)
			current_bulkhead_location+=self.bulkhead_spacing
			#print("add bulkhead %d station: %f watertight: %d floor: %f"%(bulkhead_index,current_bulkhead_location,watertight,floor_height))


	def make_bulkhead_objects(self,bulkhead_definitions):

		for bulkhead_definition in self.bulkhead_definitions:

			bh=bulkhead.bulkhead(self,bulkhead_definition)
								
			bh.make_bulkhead()

			# If it's not watertight - there is a void in middle
			if bulkhead_definition.watertight==False:
				
				floor_height_z=bulkhead_definition.floor_height

				# floor height
				if floor_height_z!=False:

					floor_bool_name="floor_bool_%0.03f"%bh.bulkhead_definition.station

					ob = bpy.data.objects.get(floor_bool_name)

					if ob is None:
						ob = geometry_helper.make_cube(name=floor_bool_name,
							location=[bulkhead_definition.station,0,0],
							size=[bulkhead_definition.thickness,self.hull_width,self.hull_height])

						ob.location.z=0-(self.hull_height/2)+floor_height_z
						ob.hide_viewport=True
						ob.hide_render=True

						view_collection_cleaner=bpy_helper.make_collection(self.cleaner_collection_name,bpy.context.scene.collection.children)
						bpy_helper.move_object_to_collection(view_collection_cleaner,ob)


					bh.bulkhead_floor_object=ob
						
					modifier=self.hull_core_object.modifiers.new(name="floor", type='BOOLEAN')
					modifier.object=ob
					modifier.operation="DIFFERENCE"

		
			self.bulkhead_instances.append(bh)

			material_helper.assign_material(bh.bulkhead_object,material_helper.get_material_bulkhead())

			#if bh.bulkhead_void_object!=None:
			#	bpy_helper.select_object(bh.bulkhead_void_object,True)
			
			#	bpy_helper.bmesh_recalculate_normals(bh.bulkhead_void_object)
				
			#	bpy_helper.hide_object(bh.bulkhead_void_object)

			if bh.bulkhead_overcut_object!=None:
				bpy_helper.hide_object(bh.bulkhead_overcut_object)
			
			bpy_helper.parent_objects_keep_transform(parent=self.hull_object,child=bh.bulkhead_object)

			bh.bulkhead_object.parent=self.hull_object


	def add_prop(self, rotation=None,
						location=None,
						blend_file="props.blend",
						library_path="Collection",
						target_object="myprop",
						parent=None):
		# this is a bit redundant - passing all the parameters through like this
		# but it allows us to make one call add_prop without having to make the object
		# then add to the hull from the external caller
		new_prop=prop_helper.prop_helper(blend_file=blend_file,
			rotation=rotation, location=location,
			library_path=library_path,
			target_object=target_object,
			parent=parent)
		
		self.props.append(new_prop)

	def integrate_props(self):
		view_collection_props=bpy_helper.make_collection("props",bpy.context.scene.collection.children)

		for prop in self.props:
			ob=prop.import_object(view_collection_props)
			bpy_helper.move_object_to_collection(view_collection_props,ob)

	def integrate_components(self):
		# The order of boolean operations is important... If order not organized correctly strange things happen

		print("Integrate")

		performance_timer = bpy_helper.ElapsedTimer()


		hide_hull=False
		use_subtractive_objects=False
		use_props=False

		#======================================
		# Single configuration area for generation overrides
		#======================================
		use_subtractive_objects=True
		use_props=True
		#======================================
		
		# longitudinal stringers created at same time as chines so as to reuse the curve
		for chine_object in self.chine_list:
				chine_object.longitudinal_elements_enabled=self.make_longitudinals
				chine_object.make_chine()


		self.make_chine_hull_booleans()

		self.make_modshapes()			

		if self.make_keels:
			for keel in self.keel_list:
				keel.make_keel()

			self.merge_keels()

		if self.make_bulkheads:
			self.add_auto_bulkheads()
			self.make_bulkhead_objects(self.bulkhead_definitions)			

		if use_props:
			self.integrate_props()	

		if self.make_keels:
			
			self.make_keel_booleans()

		if self.make_bulkheads:
			self.make_bulkhead_booleans()

		if self.make_longitudinals:
			self.make_longitudinal_booleans()

		if use_subtractive_objects:
			self.apply_subtractive_objects()

		if self.hide_hull:
			self.hull_object.hide_viewport=True

		self.hull_core_object.hide_viewport=True

		time_string = performance_timer.get_elapsed_string()

		return time_string

	def add_keel(self,keel):
		self.keel_list.append(keel)

	def apply_subtractive_objects(self):

		for ob in self.subtractive_objects:

			ob.hide_render=True
			ob.hide_viewport=True
			ob.display_type="WIRE"

			bool_name="subtract_%s"%ob.name
			bool_new = self.hull_object.modifiers.new(type="BOOLEAN", name=bool_name)
			bool_new.object = ob
			bool_new.operation = 'DIFFERENCE'

			for chine in self.chine_list:
				for chine_instance in chine.chine_instances:
					for lg in chine_instance.longitudinal_objects:				
						if geometry_helper.check_intersect(ob,lg):
							modifier=lg.modifiers.new(type='BOOLEAN',name=bool_name)
							modifier.object=ob
							modifier.operation="DIFFERENCE"


	def make_bulkhead_booleans(self):
	
		for bh in self.bulkhead_instances:
			if not bh.bulkhead_definition.watertight:
				bool_void = bh.bulkhead_object.modifiers.new(type="BOOLEAN", name="void.center_%d"%bh.bulkhead_definition.station)
				bool_void.object = self.hull_core_object
				bool_void.operation = 'DIFFERENCE'


	def make_longitudinal_booleans(self):

		for chine in self.chine_list:
			for chine_instance in chine.chine_instances:

				for longitudinal_slicer in chine_instance.longitudinal_slicers:

					for bh in self.bulkhead_instances:
						#print("bh: %s"%bh.bulkhead_object.name,end=" ")
						# TODO for some reason interection code not returning correct result
						if geometry_helper.check_intersect(bh.bulkhead_object,longitudinal_slicer) or True:
							modifier_name=longitudinal_slicer.name
							bulkhead_modifier=bh.bulkhead_object.modifiers.new(name=modifier_name, type='BOOLEAN')
							bulkhead_modifier.object=longitudinal_slicer
							bulkhead_modifier.operation="DIFFERENCE"

							if self.slicer_overcut_ratio>1:
								if bh.bulkhead_overcut_object!=None:
									bulkhead_overcut_modifier=bh.bulkhead_overcut_object.modifiers.new(name=modifier_name, type='BOOLEAN')
									bulkhead_overcut_modifier.object=longitudinal_slicer
									bulkhead_overcut_modifier.operation="DIFFERENCE"


							# If we have a slot gap for CNC operations
							if self.slot_gap>0:

								# Apply modifier to keel object because we are going to further modify bulkhead...
								bpy_helper.select_object(bh.bulkhead_object,True)
								bpy.ops.object.modifier_apply(modifier=modifier_name)

				for longitudinal_object in chine_instance.longitudinal_objects:
						for bh in self.bulkhead_instances:
							# TODO for some reason interection code not returning correct result
							if geometry_helper.check_intersect(bh.bulkhead_object,longitudinal_object) or True:
								modifier_name=bh.bulkhead_object.name
								chine_modifier=longitudinal_object.modifiers.new(name=modifier_name, type='BOOLEAN')

								mod_obj = bh.bulkhead_object

								if self.slicer_overcut_ratio>1:
									if bh.bulkhead_overcut_object!=None:
										mod_obj=bh.bulkhead_overcut_object

								chine_modifier.object=mod_obj
								chine_modifier.operation="DIFFERENCE"

								# If we have a slot gap for CNC operations
								if self.slot_gap>0:

									# Apply modifier to longitudinal object because we are going to further modify bulkhead...
									bpy_helper.select_object(longitudinal_object,True)
									bpy.ops.object.modifier_apply(modifier=modifier_name)

									# Now use stop gap object to create a larger gap
									#bulkhead_modifier.object=keel.keel_slicer_slot_gap_object

				# If we have a slot gap for CNC operations
				if self.slot_gap>0:
					for lg in chine_instance.longitudinal_slicers_slot_gap_objects:

						for bh in self.bulkhead_instances:
							#print("bh: %s"%bh.bulkhead_object.name,end=" ")
							# TODO for some reason interection code not returning correct result
							if geometry_helper.check_intersect(bh.bulkhead_object,lg) or True:
								modifier_name=lg.name
								bulkhead_modifier=bh.bulkhead_object.modifiers.new(name=modifier_name, type='BOOLEAN')
								bulkhead_modifier.object=lg
								bulkhead_modifier.operation="DIFFERENCE"







	def make_longitudinal_elements(self):
		for chine_object in self.chine_list:
			chine_object.make_longitudinal_elements()

	def make_chine_hull_booleans(self):

		for chine_object in self.chine_list:	

			# Add bool modifiers for hull object (exterior walls)
			for chine_instance in chine_object.chine_instances:		
				slicename="slice.%s"%chine_instance.curve_object.name

				bool_new = self.hull_object.modifiers.new(type="BOOLEAN", name=slicename)
				bool_new.object = chine_instance.curve_object
				bool_new.operation = 'DIFFERENCE'

			# Add bool modifiers for hull core (bulkhead void area)
			for chine_instance in chine_object.chine_core_instances:		
				slicename="slice.%s"%chine_instance.curve_object.name

				bool_new = self.hull_core_object.modifiers.new(type="BOOLEAN", name=slicename)
				bool_new.object = chine_instance.curve_object
				bool_new.operation = 'DIFFERENCE'


	def merge_keels(self):


		# Iterate through keels to make groupings
		keel_lateral_offsets=[]

		for keel in self.keel_list:
			if keel.lateral_offset not in keel_lateral_offsets:
				keel_lateral_offsets.append(keel.lateral_offset)

		# Bool Apply does not work as expected if object is hidden...
		# unhide objects before applying boolean modifier

		for lateral_offset in keel_lateral_offsets:

			print("Lateral Offset: %f"%lateral_offset)

			base_keel=None

			for keel in self.keel_list:

				if keel.lateral_offset==lateral_offset:
					
					if base_keel is None:
						base_keel=keel

						base_keel.keel_slicer_object.hide_viewport=False

						if base_keel.keel_slicer_slot_gap_object!=None:
							base_keel.keel_slicer_slot_gap_object.hide_viewport=False
						
					else:

						# Merge keels with same lateral_offset
						keel_modifier_name="merge_keel"

						# Keel Object
						keel_modifier=base_keel.keel_object.modifiers.new(name=keel_modifier_name, type='BOOLEAN')
						keel_modifier.object=keel.keel_object
						keel_modifier.operation="UNION"

						# Keel Slicer Object
						keel.keel_slicer_object.hide_viewport=False
						keel_modifier=base_keel.keel_slicer_object.modifiers.new(name=keel_modifier_name, type='BOOLEAN')
						keel_modifier.object=keel.keel_slicer_object
						keel_modifier.operation="UNION"

						# Keel Slicer Gap Object
						if base_keel.keel_slicer_slot_gap_object!=None:
							if keel.keel_slicer_slot_gap_object!=None:
								keel.keel_slicer_slot_gap_object.hide_viewport=False
								keel_modifier=base_keel.keel_slicer_slot_gap_object.modifiers.new(name=keel_modifier_name, type='BOOLEAN')
								keel_modifier.object=keel.keel_slicer_slot_gap_object
								keel_modifier.operation="UNION"


						#bpy.ops.object.modifier_apply(modifier=keel_modifier_name)

					#bpy_helper.hide_object(keel.keel_object)

						# Add base keel to list so we don't use it twice
					#	base_keel_list.append(base_keel)

			if base_keel!=None:

				geometry_helper.apply_object_bools(base_keel.keel_object)
				geometry_helper.apply_object_bools(base_keel.keel_slicer_object)

				if base_keel.keel_slicer_slot_gap_object!=None:
					geometry_helper.apply_object_bools(base_keel.keel_slicer_slot_gap_object)
				
				for keel_delete in self.keel_list:
					if keel_delete.lateral_offset==lateral_offset:
						if keel_delete!=base_keel:

							bpy.data.objects.remove(keel_delete.keel_object)
							keel_delete.keel_object=None

							bpy.data.objects.remove(keel_delete.keel_slicer_object)
							keel_delete.keel_slicer_object=None
						
							if keel_delete.keel_slicer_slot_gap_object!=None:
								bpy.data.objects.remove(keel_delete.keel_slicer_slot_gap_object)
								keel_delete.keel_slicer_slot_gap_object=None

				base_keel.keel_slicer_object.hide_viewport=True

				if base_keel.keel_slicer_slot_gap_object!=None:
					base_keel.keel_slicer_slot_gap_object.hide_viewport=True

							


	def make_keel_booleans(self):

		for keel in self.keel_list:

			if keel.keel_slicer_object!=None:

				for bh in self.bulkhead_instances:

					# TODO for some reason interection code not returning correct result
					if geometry_helper.check_intersect(bh.bulkhead_object,keel.keel_slicer_object) or True:

						# notch the bulkhead with keel_slicer_object
						bulkhead_modifier_name="%s_%s"%(bh.bulkhead_object.name,keel.keel_slicer_object.name)
						bulkhead_modifier=bh.bulkhead_object.modifiers.new(name=bulkhead_modifier_name, type='BOOLEAN')
						bulkhead_modifier.object=keel.keel_slicer_object
						bulkhead_modifier.operation="DIFFERENCE"

						if self.slicer_overcut_ratio>0:
							if bh.bulkhead_overcut_object!=None:

								bulkhead_overcut_modifier=bh.bulkhead_overcut_object.modifiers.new(name=bulkhead_modifier_name, type='BOOLEAN')
								bulkhead_overcut_modifier.object=keel.keel_slicer_object
								bulkhead_overcut_modifier.operation="DIFFERENCE"


						#bpy_helper.select_object(bh.bulkhead_object,True)
	

						# notch the keel with modified bulkhead 
						
						keel_modifier_name="%s_%s"%(bh.bulkhead_object.name,keel.keel_object.name)
						keel_modifier=keel.keel_object.modifiers.new(name=keel_modifier_name, type='BOOLEAN')

						mod_target=bh.bulkhead_object
		
						if self.slicer_overcut_ratio>1:
							if bh.bulkhead_overcut_object!=None:
								mod_target=bh.bulkhead_overcut_object

						keel_modifier.object=mod_target

						keel_modifier.operation="DIFFERENCE"

						# If we have a slot gap for CNC operations
						if self.slot_gap>0:

							# Apply modifier to keel object because we are going to further modify bulkhead...
							bpy_helper.select_object(keel.keel_object,True)
							bpy.ops.object.modifier_apply(modifier=keel_modifier_name)

							# Now use stop gap object to create a larger gap
							bulkhead_modifier.object=keel.keel_slicer_slot_gap_object



				bpy_helper.select_object(keel.keel_object,True)

				material_helper.assign_material(keel.keel_object,material_helper.get_material_keel())

				keel.keel_object.parent=self.hull_object


	# Cleans up longitudinal framing in center of hull for access to entrance / pilothouse 
	# so longitudinal frames don't block entrance
	def cleanup_center(self,clean_location,clean_size):

		view_collection_cleaner=bpy_helper.make_collection(self.cleaner_collection_name,bpy.context.scene.collection.children)

		object_end_clean = geometry_helper.make_cube("mid_clean_%s"%clean_location[0],location=clean_location,size=clean_size)

		bpy_helper.move_object_to_collection(view_collection_cleaner,object_end_clean)

		material_helper.assign_material(object_end_clean,material_helper.get_material_bool())

		for lg in self.longitudinal_list:

			modifier=lg.modifiers.new(name="bool", type='BOOLEAN')
			modifier.object=object_end_clean
			modifier.operation="DIFFERENCE"
			bpy_helper.hide_object(object_end_clean)

	# Trims the ends of the longitudinal framing where it extends past last bulkhead
	# x_locations is a list of stations where they will be chopped
	# rotations is a corresponding list of rotations in the Y axis. Bulkheads are assumed to be not rotated on X an Z axises. 
	def cleanup_longitudinal_ends(self,x_locations,rotations=None):

		view_collection_cleaner=bpy_helper.make_collection(self.cleaner_collection_name,bpy.context.scene.collection.children)

		end_clean_list=[]

		for index,x_location in enumerate(x_locations):
			# =========================================
			# Clean up ends of longitudinal slicers

			block_width=self.hull_width

			adjusted_location=x_location
			if adjusted_location<0:
				adjusted_location=adjusted_location-block_width/2

			if adjusted_location>0:
				adjusted_location=adjusted_location+block_width/2

			object_end_clean = geometry_helper.make_cube("end_clean_%s"%index,location=[adjusted_location,0,0],size=(block_width,block_width,self.hull_height))

			if rotations!=None:
#				bpy_helper.select_object(object_end_clean,True)
				#bpy.ops.transform.rotate(value=radians(rotations[index]),orient_axis='Y')
				object_end_clean.rotation_euler.y=radians(rotations[index])

			bpy_helper.move_object_to_collection(view_collection_cleaner,object_end_clean)

			material_helper.assign_material(object_end_clean,material_helper.get_material_bool())
			end_clean_list.append(object_end_clean)

		# ===================================================================

			for chine_object in self.chine_list:	
				for chine_instance in chine_object.chine_instances:	
					#print("chine: %s"%chine_instance)
					for lg in chine_instance.longitudinal_objects:
						#print("eval: %s"%lg.name)
						for object_end_clean in end_clean_list:
							#print("clean: %s"%object_end_clean.name)
							if geometry_helper.check_intersect(lg,object_end_clean):
								modifier=lg.modifiers.new(name="bool", type='BOOLEAN')
								modifier.object=object_end_clean
								modifier.operation="DIFFERENCE"
								bpy_helper.hide_object(object_end_clean)

		bpy_helper.hide_object(view_collection_cleaner)
