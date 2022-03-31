import bpy
import bmesh
import math
import mathutils
from mathutils import Matrix
from mathutils import Vector
from . import mapped_mesh
from ..bpyutils import bpy_helper

# project into XY plane, 
#up = Vector((0, 0, 1))

#==================================================



class flatten_helper():

	flattened_collection=None

	# Output position for spacing objects 
	output_pos_X=0
	output_pos_Y=0

	def get_bounding_box(self,bm):

		minX=None
		minY=None
		minZ=None
		maxX=None
		maxY=None
		maxZ=None

		for f in bm.faces:
			print("face")

		for v in bm.verts:
			print("vert")

		dir(bm.verts)

		for v in bm.verts:

			if minX is None:
				minX=v.co[0]
			elif v.co[0]<minX:
				minX=v.co[0]

			if maxX is None:
				maxX=v.co[0]
			elif v.co[0]>maxX:
				maxX=v.co[0]

			if minY is None:
				minY=v.co[1]
			elif v.co[1]<minY:
				minY=v.co[1]

			if maxY is None:
				maxY=v.co[1]
			elif v.co[1]>maxY:
				maxY=v.co[1]

			if minZ is None:
				minZ=v.co[2]
			elif v.co[2]<minZ:
				minZ=v.co[2]

			if maxZ is None:
				maxZ=v.co[2]
			elif v.co[2]<maxZ:
				maxZ=v.co[2]


		sizeX=maxX-minX
		sizeY=maxY-minY
		sizeZ=maxZ-minZ
				
		print("%0.2f %0.2f / %0.2f %0.2f / %0.2f %0.2f size: (%0.2f %0.2f %0.2f)"
			%(minX,maxX,
				minY,maxY,
				minZ,maxZ,
				sizeX,sizeY,sizeZ))


		points = [v.co.xy for v in bm.verts]
		#points = [v.co.xy for v in bm.verts if v.select]
		print(points)
		angle = mathutils.geometry.box_fit_2d(points)

		mat = mathutils.Matrix.Rotation(angle, 2)
		print(mat)

		cos_2d = [co for co in points]
		print(cos_2d)

		cos_2d = [(mat @ co) for co in points]
		print(cos_2d)
		xs = [co.x for co in cos_2d]
		ys = [co.y for co in cos_2d]

		width = max(xs) - min(xs)
		height = max(ys) - min(ys)

		print("Angle: %f %f %f"%(math.degrees(angle),width,height))

		return [width,height,angle]



	def rotate_mesh(self,bm,angle):
		centroid=[0,0,-1]
		#v1=bmesh.BMVert

		#axis = (v2.co - v1.co).normalized()
		rot_matrix = Matrix.Rotation(angle, 3, 'Z')

		bmesh.ops.rotate(bm, 
			cent=(0,0,0), 
			matrix=rot_matrix, 
			verts=bm.verts)










	# Iterate through verts in each face in a shape
	# Print inside angle between two edges
	# different implementation
	def print_inside_angles2(self,ob):

		print("Active object = ",ob.name)

		bm = bmesh.new()   # create an empty BMesh
		bm.from_mesh(ob.data)
		#bm = bmesh.from_edit_mesh(ob.data)

		#selected_faces = [f for f in bm.faces if f.select]
		for f in bm.faces:
			edges = f.edges[:]
			print("Face", f.index, "Edges:", [e.index for e in edges])
			edges.append(f.edges[0])
		
		for e1, e2 in zip(edges, edges[1:]):

			angle = mapped_mesh.edge_angle(e1, e2, f.normal)
			print("Edge Corner", e1.index, e2.index, "angle:", round(math.degrees(angle)))



	# Iterate through verts in each face in a shape
	# Print inside angle between two edges
	def print_inside_angles(self,ob):

		print("Active object = ",ob.name)
		
		me = ob.data
		bm_old = bmesh.new()         # Create a new bmesh container instance
		bm_old.from_mesh(me)         # Pass your mesh into this container
		
		for f in bm_old.faces:
			
			print("Face: %d"%f.index)
			#for e in f.edges:
			#    print("edge angle: %s"%math.degrees(e.calc_face_angle()))
			
			#for v in f.verts:
			#    print("edge angle: %s"%math.degrees(e.calc_face_angle()))
			
			for l in f.loops:
				angle=math.degrees(l.calc_angle())
				length=l.edge.calc_length()
				print("length: %2.02f loop angle: %d "%(length,round(angle)))
			
	# Reproduces shape in flattened form
	def clone_object_faces(self,selected_object):

			scene = bpy.context.scene
			#selected_object = bpy.context.object

			print("Active object = ",selected_object.name)

			me = selected_object.data
			bm_old = bmesh.new()         # Create a new bmesh container instance
			bm_old.from_mesh(me)         # Pass your mesh into this container

			
			# bm_old.verts.ensure_lookup_table()

			mesh_name="%s_flat"%selected_object.name

			# New Mesh
			bm_new = bmesh.new()         # Create a new bmesh container instance
			mesh_data = bpy.data.meshes.new(mesh_name)
			
			

			new_mapped_mesh = mapped_mesh.mapped_mesh(bm_new)

			bm_old.faces.ensure_lookup_table()
			#f=bm_old.faces[0]
			
			#new_mapped_mesh.print_edge_angles(f,bm_old)

			new_mapped_mesh.remap_mesh(bm_old)

			bounding_data=self.get_bounding_box(bm_new)
			width=bounding_data[0]
			height=bounding_data[1]
			angle=bounding_data[2]

			self.rotate_mesh(bm_new,angle)

			#pt=(width/2,height/2,0)
			#bmesh.ops.translate(bm_new,vec=pt,verts=bm_new.verts)

			bm_new.to_mesh(mesh_data)
			bm_new.free()

			mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
			bpy.context.collection.objects.link(mesh_obj)

			mesh_obj.location.z=0 
			#selected_object.location.z+1


			mesh_obj.name=mesh_name

			# For now output single continious line
			mesh_obj.location.x=self.output_pos_X
			#mesh_obj.location.Y=self.output_pos_Y

			placement_spacing=0.1
			self.output_pos_X+=width+placement_spacing
			#self.output_pos_Y+=height

			flattened_collection=bpy_helper.make_collection("flattened",bpy.context.scene.collection.children)
			bpy_helper.move_object_to_collection(flattened_collection,mesh_obj)
  
			



	def flatten_plates(self):

		#self.make_shape()

		#return self.measure_angle()

		ob = bpy.context.object

		if ob is not None:
			self.print_inside_angles(ob)

			self.print_inside_angles2(ob)

		# Reset output position
		self.output_pos_X=0
		self.output_pos_Y=0

		#return
		for obj in bpy.context.selected_objects:
			if obj.type=="MESH":
				self.clone_object_faces(obj)

		


