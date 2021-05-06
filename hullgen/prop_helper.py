import bpy
from math import radians, degrees

# Props are objects linked (imported) from an external blender file like movie props

class prop_helper:

	prop_rotation=[0,0,0]

	location=None
	rotation=None

	library_path="Collection"
	blend_file="props.blend"
	target_object="myprop"
	parent=None


	def __init__(self,
						rotation=None,
						location=None,
						blend_file="props.blend",
						library_path="Collection",
						target_object="myprop",
						parent=None):

		self.location=location
		self.rotation=rotation

		self.target_object=target_object
		self.library_path=library_path
		self.blend_file=blend_file

	def import_object(self,view_collection):
		full_import_path="%s/%s/"%(self.blend_file,self.library_path)

		bpy.ops.wm.link(directory=full_import_path,
			link=True,
			files=[{'name': self.target_object}], 
			relative_path=False)

		ob = bpy.context.active_object

		if self.location!=None:
			ob.location=self.location

		if self.rotation!=None:
			ob.rotation_euler.x=radians(self.rotation[0])
			ob.rotation_euler.y=radians(self.rotation[1])
			ob.rotation_euler.z=radians(self.rotation[2])

		if self.parent!=None:
			ob.parent=self.parent

		return ob

