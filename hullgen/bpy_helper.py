import bpy

def select_object(theObject,selected):

	bpy.ops.object.select_all(action='DESELECT')
	
	if selected==True:
		bpy.context.view_layer.objects.active = theObject
		theObject.select_set(state=True)
	else:
		bpy.context.view_layer.objects.active = None
		theObject.select_set(state=False)

def deselect_all_objects():

	if bpy.context.active_object!=None:
		print(bpy.context.active_object)

		bpy.ops.object.mode_set(mode='OBJECT')

	bpy.ops.object.select_all(action='DESELECT')

		

def find_and_remove_object_by_name(objname):
	for obj in bpy.data.objects:
	#	print(obj.name)
		if(obj.name==objname):
	#		print("found")
	#        bpy.context.scene.collection.objects.unlink(obj)
			bpy.data.objects.remove(obj)
