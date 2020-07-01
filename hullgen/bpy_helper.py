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

	if bpy.context.view_layer.objects.active!=None:
		bpy.ops.object.mode_set(mode='OBJECT')
		
	bpy.ops.object.select_all(action='DESELECT')

	
def find_and_remove_object_by_name(objname):
	for obj in bpy.data.objects:
	#	print(obj.name)
		if(obj.name==objname):
	#		print("found")
	#        bpy.context.scene.collection.objects.unlink(obj)
			bpy.data.objects.remove(obj)


# works on object or collection
def hide_object(ob):
	ob.hide_viewport = True
	ob.hide_render = True

def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step
		

def move_object_to_collection(new_collection,the_object):

	C_collection = find_collection(bpy, the_object)
	C_collection.objects.unlink(the_object)

	new_collection.objects.link(the_object)


def find_collection(context, item):
	collections = item.users_collection
	if len(collections) > 0:
		return collections[0]
	return context.scene.collection


def make_collection(collection_name, parent_collection):
	if collection_name in bpy.data.collections:
		return bpy.data.collections[collection_name]
	else:
		new_collection = bpy.data.collections.new(collection_name)
		bpy.context.scene.collection.children.link(new_collection)
		return new_collection

def is_object_hidden_from_view(the_object):
	if the_object.hide_viewport==True:
		return True

	C_collection = find_collection(bpy, the_object)
	if C_collection.hide_viewport==True:
		return True

	return False


