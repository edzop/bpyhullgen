import bpy
import bmesh
import math

from mathutils import Vector

# project into XY plane, 
up = Vector((0, 0, 1))


def edge_angle(e1, e2, face_normal):

	#print("edge angle: %s %s"%(e1,e2))
	
	b = set(e1.verts).intersection(e2.verts).pop()
	a = e1.other_vert(b).co - b.co
	c = e2.other_vert(b).co - b.co
	a.negate()    
	axis = a.cross(c).normalized()
	if axis.length < 1e-5:
		return math.pi # inline vert
	
	if axis.dot(face_normal) < 0:
		axis.negate()
	M = axis.rotation_difference(up).to_matrix().to_4x4()  

	a = (M @ a).xy.normalized()
	c = (M @ c).xy.normalized()

	angle=math.pi - math.atan2(a.cross(c), a.dot(c))
	#print("Edge Corner", e1.index, e2.index, "Angle:", round(math.degrees(angle)))

	return angle




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

	# a list of new mapped faces that have been newly generated
	mapped_faces=None

	# a list of new mapped verts that have been newly generated
	mapped_verts=None

	# a list of faces from bm_old that have been process already
	processed_faces=None

	def __init__(self,bm_new):
		self.mapped_faces=[]
		self.mapped_verts=[]
		self.processed_faces=[]

		self.bm_new=bm_new

	def print_edge_angles(self,f,bm):

		up = Vector((0, 0, 1))

		#ob = bpy.context.object
		#me = ob.data
		#bm = bmesh.from_edit_mesh(me)

		selected_faces = [f for f in bm.faces if f.select]
		for f in selected_faces:
			edges = f.edges[:]
			print("Face", f.index, "Edges:", [e.index for e in edges])
			edges.append(f.edges[0])
			
		for e1, e2 in zip(edges, edges[1:]):

			angle = edge_angle(e1, e2, f.normal)
			print("Edge Corner", e1.index, e2.index, "Angle:", round(math.degrees(angle)))

	def process_face(self,f):

		if f in self.processed_faces:
			# already processed
			return

		flipped=False

		#self.print_edge_angles(f)
	
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

			next_loop=eval_loop.link_loop_next
			prev_loop=eval_loop.link_loop_prev

			normal=eval_loop.calc_normal()

			e1 = eval_loop.edge
			e2 = prev_loop.edge
			angle = edge_angle(e1,e2,f.normal)

			# Calc Angle 
			#angle=eval_loop.calc_angle()
			#angle=edge_angle(eval_loop.edge,next_loop.edge,normal)

			print("Edge Corner", eval_loop.edge.index, next_loop.edge.index, "Angle:", round(math.degrees(angle)))


			angle_degrees=math.degrees(angle)
			length=eval_loop.edge.calc_length()

			is_convex=eval_loop.is_convex
			tangent=eval_loop.calc_tangent()
			


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

		self.processed_faces.append(f)

		# recursively process connected faces
		for face_edge in f.edges:
			for linked_face in face_edge.link_faces:
				self.process_face(linked_face)



		#flipped=not flipped

	def remap_mesh(self,bm_old):

		# First build faces in memory

		bm_old.faces.ensure_lookup_table()

		if len(bm_old.faces)>0:
			first_face=bm_old.faces[0]

			# this function will recursively add other faces connected to original face
			self.process_face(first_face)
			
		#for f in bm_old.faces:


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

