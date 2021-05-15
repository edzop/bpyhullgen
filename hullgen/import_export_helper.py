import bpy

import csv

from ..bpyutils import bpy_helper
from ..bpyutils import measure_helper

def import_plates(filename):

	for obj in bpy.context.selected_objects:
		if obj.type=="MESH":
			bpy_helper.select_object(obj,True)
			
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.remove_doubles()
			bpy.ops.mesh.select_mode(type="EDGE")
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.object.mode_set(mode='OBJECT')

			obj.data.edges[0].select=True
			bpy.ops.object.mode_set(mode='EDIT')
			#bpy.ops.mesh.select_similar(type='FACE', compare='LESS', threshold=1)
			bpy.ops.mesh.select_similar(type='FACE', threshold=1)
			
			# sometime models need to invert this sometimes not - not sure why...
			# Should create toggle?
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.mesh.delete(type='EDGE')
			
			bpy.ops.mesh.select_mode(type="VERT")
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.mesh.select_loose()
			bpy.ops.mesh.delete(type='VERT')

			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.separate(type='LOOSE')
			bpy.ops.mesh.select_mode(type="EDGE")

			bpy.ops.object.mode_set(mode='OBJECT')


def export_plates(filename):
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')

	#bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
	#bpy.ops.uv.export_layout(filepath="plates1.svg", mode='SVG', size=(1024, 1024))

	bpy.ops.uv.smart_project(scale_to_bounds=False,island_margin=0.03)
	bpy.ops.uv.export_layout(filepath=filename, mode='SVG', size=(4800, 4800),opacity=1)

	bpy.ops.object.mode_set(mode='OBJECT')



def exportCSV():

	with open('hull_export.csv', 'w', newline='') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=',',
					quotechar='|', quoting=csv.QUOTE_MINIMAL)

		csv_row = []

		csv_row.append("name")
		csv_row.append("posX")
		csv_row.append("posY")
		csv_row.append("posZ")

		csv_row.append("volume")

		csv_row.append("face_count")
		csv_row.append("surface_area")

		csv_row.append("sizeX")
		csv_row.append("sizeY")
		csv_row.append("sizeZ")

		csvWriter.writerow(csv_row)

		#for obj in bpy.context.selected_objects:
		#for obj in bpy.data.objects:
		for obj in bpy.context.view_layer.objects:

			if obj.type=="MESH":

				print("export: %s %s"%(obj.name,obj.type))

				if bpy_helper.is_object_hidden_from_view(obj)==False:
				#if obj.hide_viewport==False:

					csv_row = []
					csv_row.append(obj.name)
					csv_row.append(obj.location.x)
					csv_row.append(obj.location.y)
					csv_row.append(obj.location.z)

					vol=measure_helper.measure_object_volume(obj)
					csv_row.append(vol)

					face_area=measure_helper.measure_face_area(obj,True)
					csv_row.append(face_area)
					face_count=measure_helper.measure_face_count(obj,True)
					csv_row.append(face_count)

					csv_row.append(obj.dimensions.x)
					csv_row.append(obj.dimensions.y)
					csv_row.append(obj.dimensions.z)

					csvWriter.writerow(csv_row)

		csv_row = [" "]
		csvWriter.writerow(csv_row)

		csv_row = ["mm","0.001"]
		csvWriter.writerow(csv_row)

		csv_row = ["5083 aluminum","2653","KG per M3"]
		csvWriter.writerow(csv_row)

		csv_row = ["steel","7900","KG per M3"]
		csvWriter.writerow(csv_row)

		csv_row = ["wood","400","KG per M3"]
		csvWriter.writerow(csv_row)


