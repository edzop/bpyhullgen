import bpy
import bmesh
import math

def get_bmvert_coords_text(bmvert):
	text="%f,%f,%f"%(bmvert.co[0],bmvert.co[1],bmvert.co[2])
	return text

# expects an array of 2 verts (x,y) [ v1[x,y], v2[x,y] ]
# returns angle in radians between verts and reference in zero (3 o clock position)
def measure_angle_between_verts(verts):

	diffX = verts[0][0]-verts[1][0]
	diffY = verts[0][1]-verts[1][1]

	flipped=False

	if verts[1][0]<verts[0][0]:
		flipped=True

	# TODO
	# find min X

	third_vert=[ verts[1][0], verts[0][1] ]

	verts.append(third_vert)

	#opp_length=verts[1][1]-verts[0][1]
	#adj_length=verts[1][0]-verts[0][0]

	angle=0
	angle_degrees=0
	base_angle=0

	if diffX==0:
		# 90 degrees

		if verts[0][1]<verts[1][1]:
			base_angle=math.pi/2
			angle_degrees=90
		else:
			base_angle=math.pi+math.pi/2
			angle_degrees=270
	else:
		base_angle = math.atan(diffY/diffX)
		angle=base_angle

		if flipped==True:
			# add 180 degrees
			angle=angle+math.pi

		angle_degrees=math.degrees(angle)

	status="(%0.2f,%0.2f) - (%0.2f,%0.2f) Angle: %f (base %f) Diff(%0.2f,%0.2f) Flipped: %s"%(
		verts[0][0],verts[0][1],
		verts[1][0],verts[1][1],
		angle_degrees,
		math.degrees(base_angle),
		diffX,diffY,
		flipped)

	print(status)

	return angle


#Compute the third point of a triangle when two points and all edge lengths are given
def getThirdPoint(v0, v1, l01, l12, l20):
	v2rotx = (l01 ** 2 + l20 ** 2 - l12 ** 2) / (2 * l01)
	v2roty0 = math.sqrt((l01 + l20 + l12) * (l01 + l20 - l12) * (l01 - l20 + l12) * (-l01 + l20 + l12)) / (2 * l01)

	v2roty1 = - v2roty0

	theta = math.atan2(v1[1] - v0[1], v1[0] - v0[0])

	v2trans0 = (v2rotx * math.cos(theta) - v2roty0 * math.sin(theta), v2rotx * math.sin(theta) + v2roty0 * math.cos(theta), 0)
	v2trans1 = (v2rotx * math.cos(theta) - v2roty1 * math.sin(theta), v2rotx * math.sin(theta) + v2roty1 * math.cos(theta), 0)

	print("trans0:",end=" ")
	print(v2trans0)        
	print("trans1:",end=" ")
	print(v2trans1)
	
	ret = ((v2trans0[0]+v0[0],v2trans0[1]+v0[1],v2trans0[2]+v0[2]),
		(v2trans1[0]+v0[0],v2trans1[1]+v0[1],v2trans1[2]+v0[2]))
	
	return ret

class triface:
	index=0
	verts=None
	
	flatverts=None
	
	distAB=0
	distBC=0
	distAC=0
	
	def __init__(self,index,verts):
		self.index=index
		self.verts=verts
		
	def store_lengths(self):
		self.distAB=(self.verts[0]-self.verts[1]).length
		self.distBC=(self.verts[1]-self.verts[2]).length
		self.distAC=(self.verts[0]-self.verts[2]).length
		
	def make_flatverts(self):
		self.flatverts=[]
		
		newA=(0,0,0)
		newB=(0,self.distBC,0)
		newC=(self.distAC,self.distBC,0)
		
		self.flatverts.append(newA)
		self.flatverts.append(newB)
		self.flatverts.append(newC)
		
	def print_summary(self):
			
		print("index=%d distAB=%f distBC=%f distAC=%f"%(self.index,self.distAB,self.distBC,self.distAC))


# calculates new position from X,Y + distance in direction angle (radians)
def get_vector_position(x,y,angle,distance,reciprocal=False,flipped=False):

	angle_used=angle

	if flipped:
		angle_used=-angle_used

	if reciprocal==True:
		angle_used+=math.pi
	
	#angle=math.radians(270)+angle2
	xx = x+( distance*math.cos(angle_used) )
	yy = y+( distance*math.sin(angle_used) )

	return [ xx,yy ]


#==================================================

class mapped_vert:

	# type bmesh.types.BMVert
	original_vert=None

	# type bmesh.types.BMVert
	mapped_vert=None

	def __init__(self,original_vert):
		self.original_vert=original_vert
		#self.mapped_vert=

class mapped_face:

	# type mapped_vert
	mapped_verts=None

	total_angle=0
	
	last_angle=0
	last_distance=0

	flipped=False

	reused_verts=0
	created_verts=0

	def __init__(self,flipped=False):
		self.mapped_verts=[]
		self.flipped=flipped

	def add_vert(self,new_vert,is_reused_vert=False):
		self.mapped_verts.append(new_vert)

		if is_reused_vert:
			self.reused_verts+=1
		else:
			self.created_verts+=1


	def get_vert_count(self):
		return len(self.mapped_verts)

	def increment_angle(self,angle):
		#self.total_angle=self.total_angle-(angle)
		self.total_angle=self.total_angle+(angle)

	def find_reusable_pair(self):
		print("find reusable pair")

	# mapped_face.generate_remapped_bmvert - returns new BMvert
	def generate_remapped_bmvert(self,bm_new,angle,distance):

		new_vert=None


		#vert_count=len(self.mapped_verts)
		vert_count=self.reused_verts+self.created_verts

		if vert_count==0:
			# New Face
			print("Reference Zero Vert")
			new_vert=bm_new.verts.new([0,0,0])
			#self.increment_angle(angle)
		else:
			# get last vert as reference
			last_vert=self.mapped_verts[vert_count-1]
			x=last_vert.mapped_vert.co.x
			y=last_vert.mapped_vert.co.y

			newpos=None
			
			if vert_count==1:
				newpos=[-self.last_distance,0]
				#angle_used=math.radians(angle)
			else:
				print("generate_remapped_bmvert - vert count: %d"%vert_count,end=" ")


				# TODO - increment actual angle 
				# interpret angle 180 / 0 flip odd even from vector position function

				use_reciprocal=False

				if self.reused_verts==0:
					if vert_count%2!=0:
						use_reciprocal=True
				else:
					if vert_count%2==0:
						use_reciprocal=True
				

				#if self.reused_verts>0:
				#	use_reciprocal=True

				reciprocal_text="+0"

				if use_reciprocal:
					reciprocal_text="+180"
				
					#self.increment_angle(self.last_angle)
				self.increment_angle(self.last_angle)

				print("last angle: %d %s ld: %f"%(
					round(math.degrees(self.last_angle)),
					reciprocal_text,
					self.last_distance),
					end=" ")

				print("total angle: %d"%(round(math.degrees(self.total_angle))))

				newpos=get_vector_position(x,y,
					self.total_angle,
					self.last_distance,
					reciprocal=use_reciprocal,
					flipped=self.flipped)

			if newpos!=None:
				new_vert=bm_new.verts.new([newpos[0],newpos[1],0])

		self.last_angle=angle
		self.last_distance=distance

		return new_vert

 
class mapped_mesh:

	bm_new=None

	mapped_faces=None
	mapped_verts=None

	def __init__(self,bm_new):
		self.mapped_faces=[]
		self.mapped_verts=[]

		self.bm_new=bm_new

	def remap_mesh(self,bm_old):

		# First build faces in memory

		flipped=False

		for f in bm_old.faces:
				
			#vertcount=len(f.verts)

			newface = mapped_face(flipped=flipped)
			center_median=f.calc_center_median()

			print("=============================================================")
			print("New Face starting: %d Normal: %s center_median: %s"%(f.index,f.normal,center_median))

			self.mapped_faces.append(newface)

			loopcount=len(f.loops)

			
			# We must not make any assumption on which order loops are given to us...

			# We need to search to find a pair of subsequental loops that have already been mapped in 
			# order to determine start reference angle
			subsequent_mapped_loop_start=None

			if loopcount>1:
				start_loop=f.loops[0]
				eval_loop = start_loop

				continue_search=True

				print("Searching for subsequent mapped loop pairs...",end="")

				while continue_search:

					next_loop=eval_loop.link_loop_next

					first_mapping=self.lookup_vert(eval_loop.vert)
					second_mapping=self.lookup_vert(next_loop.vert)

					if first_mapping==None or second_mapping==None:

						# increment to next loop
						eval_loop=next_loop

						if eval_loop==start_loop:
							print("No pairs found!")
							continue_search=False

					else:
						# We found a match - two subsequental loops that have already been mapped
						subsequent_mapped_loop_start=eval_loop
						continue_search=False

						verts=[]

						print("Found pair")

						verts.append( [ first_mapping.mapped_vert.co[0],  first_mapping.mapped_vert.co[1]  ] )
						verts.append( [ second_mapping.mapped_vert.co[0], second_mapping.mapped_vert.co[1] ] )

						angle_diff=measure_angle_between_verts(verts)

						print(" diff angle: %d"%round(math.degrees(angle_diff)))

						newface.increment_angle(angle_diff)



			continue_search=True

			eval_loop=subsequent_mapped_loop_start
			
			if eval_loop==None:
				eval_loop=f.loops[0]

			start_loop=eval_loop

			while continue_search:

				angle=eval_loop.calc_angle()
				angle_degrees=math.degrees(eval_loop.calc_angle())
				length=eval_loop.edge.calc_length()

				is_convex=eval_loop.is_convex
				tangent=eval_loop.calc_tangent()
				normal=eval_loop.calc_normal()

				next_loop=eval_loop.link_loop_next
				prev_loop=eval_loop.link_loop_prev

				next_angle=next_loop.calc_angle()
				next_angle_degrees=math.degrees(next_angle)
				
				next_length=next_loop.edge.calc_length()

				prev_angle=prev_loop.calc_angle()
				prev_angle_degrees=math.degrees(prev_angle)
				prev_length=prev_loop.edge.calc_length()

				status="?"

				mapped_vert=self.lookup_vert(eval_loop.vert)

				#mapped_vert=None # Force reuse of all verts - for debugging

				#angle_used=angle

				#if normal[2]>0:
				#	angle_used=next_angle
					
				#if normal[2]<0:
				#	angle_used=angle

				is_reused_vert=False

				if mapped_vert==None:
					mapped_bm_vert=newface.generate_remapped_bmvert(self.bm_new,angle,length)

					status="created"

					mapped_vert=self.add_mapped_bmvert(eval_loop.vert,mapped_bm_vert)
				else:
					status="reused"
					is_reused_vert=True
					#if newface.get_vert_count()>1:
					#newface.increment_angle(angle)

					newface.last_angle=angle
					newface.last_distance=length

				#if newface.get_vert_count()>0:
				#newface.increment_angle(angle_used)
				#else:
				#	print("skip increment")

				newface.add_vert(mapped_vert,is_reused_vert)

				vert_info="Original: (%f,%f,%f) Mapped: (%f,%f,%f) %s  total: %d"%(
					
					mapped_vert.original_vert.co[0],
					mapped_vert.original_vert.co[1],
					mapped_vert.original_vert.co[2],

					mapped_vert.mapped_vert.co[0],
					mapped_vert.mapped_vert.co[1],
					mapped_vert.mapped_vert.co[2],
					status,
					round(math.degrees(newface.total_angle)))
				
				print("loop angle: %d length: %f - %s"%(round(angle_degrees),length,vert_info))

				eval_loop=next_loop

				# check to see if we have made a complete pass on all loops
				if eval_loop==start_loop:
					continue_search=False


			#flipped=not flipped

		# Add faces to new BMesh (bm_new)
		faces_added=0
					
		for mf in self.mapped_faces:
						
				newverts=[]

				for mapped_vert in mf.mapped_verts:

					newverts.append(mapped_vert.mapped_vert)

				if len(newverts)>0:
					self.bm_new.faces.new(newverts)
					faces_added+=1
				
		print("Added %d faces"%faces_added)
				

	
	def lookup_vert(self,search_vert):

		for v in self.mapped_verts:

			if v.original_vert.co[0]==search_vert.co[0] and v.original_vert.co[1]==search_vert.co[1] and v.original_vert.co[2]==search_vert.co[2]:
				return v

		return None


	def add_mapped_bmvert(self,original_vert,new_mapped_bmvert):
		new_mapped_vert=mapped_vert(original_vert)

		new_mapped_vert.mapped_vert=new_mapped_bmvert

		self.mapped_verts.append(new_mapped_vert)

		return new_mapped_vert

	def generate_mapped_vert(self,original_vert):

		#old_location=vert(x,y,z)

		# For now just use identity location
		new_mapped_bmvert=self.bm_new.verts.new([original_vert.co.x,original_vert.co.y,original_vert.co.z])

		new_mapped_vert=self.add_mapped_bmvert(original_vert,new_mapped_bmvert)

		return new_mapped_vert



class flatten_helper():

	   
	def print_angles(self):
		scene = bpy.context.scene
		ob = bpy.context.object

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
				print("loop angle: %f length: %f"%(angle,length))
			

	def clone_object_faces(self):

			scene = bpy.context.scene
			selected_object = bpy.context.object

			print("Active object = ",selected_object.name)

			me = selected_object.data
			bm_old = bmesh.new()         # Create a new bmesh container instance
			bm_old.from_mesh(me)         # Pass your mesh into this container
			
			# bm_old.verts.ensure_lookup_table()

			# New Mesh
			bm_new = bmesh.new()         # Create a new bmesh container instance
			mesh_data = bpy.data.meshes.new("cloned")

			new_mapped_mesh = mapped_mesh(bm_new)

			new_mapped_mesh.remap_mesh(bm_old)

			bm_new.to_mesh(mesh_data)
			bm_new.free()

			mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)
			bpy.context.collection.objects.link(mesh_obj)

			mesh_obj.location.z=selected_object.location.z+1


	def make_shape(self):

		bm_new = bmesh.new()         # Create a new bmesh container instance
		mesh_data = bpy.data.meshes.new("cloned")

		newverts=[]

		new_vert=bm_new.verts.new([0,0,0])

		newverts.append(new_vert)

		total_distance=0

		for i in range(0,30):
			angle=math.radians(3)
			distance=0.3

			newpos=get_vector_position(new_vert.co[0],new_vert.co[1],total_distance,distance)
			total_distance+=angle
			new_vert=bm_new.verts.new([newpos[0],newpos[1],0])
			newverts.append(new_vert)

		#bm_new.faces.new(newverts)

		bm_new.to_mesh(mesh_data)

		mesh_obj = bpy.data.objects.new(mesh_data.name, mesh_data)

		bpy.context.collection.objects.link(mesh_obj)






	# returns degrees between first two verts in selected object
	def measure_angle(self):
		scene = bpy.context.scene
		selected_object = bpy.context.object

		me = selected_object.data
		bm_old = bmesh.new()         # Create a new bmesh container instance
		bm_old.from_mesh(me)         # Pass your mesh into this container

		verts=[]

		for v in bm_old.verts:
			print("Vert %d: (%f,%f,%f)"%(v.index,
				v.co[0],
				v.co[1],
				v.co[2]))

			if v.index<2:
				verts.append([v.co[0],v.co[1]])


		if len(verts)==2:
			return measure_angle_between_verts(verts)
		else:
			return 0

				



	def flatten_plates(self):

		#self.make_shape()

		#return self.measure_angle()

		self.clone_object_faces()
		#self.print_angles()
