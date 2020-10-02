import bpy
import time
import functools
import bmesh

class ElapsedTimer:

    start_time=0

    def __init__(self):
        self.start_time=time.time()

    
    def secondsToStr(self,t):
        rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
        return "%d:%02d:%02d.%03d" % tuple(functools.reduce(rediv,[[t*1000,],1000,60,60]))


    def get_elapsed_string(self):
        elapsed_time = time.time() - self.start_time

        elapsed_string="Elapsed time: %s"%(self.secondsToStr(elapsed_time))

        print(elapsed_string)
        #print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

        return elapsed_string


def select_object(theObject,selected):

	if bpy.context.active_object!=None:
		if bpy.context.active_object.mode!='OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')

	bpy.ops.object.select_all(action='DESELECT')
	
	if selected==True:
		bpy.context.view_layer.objects.active = theObject
		theObject.select_set(state=True)
	else:
		bpy.context.view_layer.objects.active = None
		theObject.select_set(state=False)

def deselect_all_objects():

	if bpy.context.active_object!=None:
		if bpy.context.active_object.mode!='OBJECT':
			bpy.ops.object.mode_set(mode='OBJECT')
		
	bpy.ops.object.select_all(action='DESELECT')

def bmesh_recalculate_normals(obj):
	mesh=obj.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
	bm.to_mesh(mesh)
	bm.clear()
	mesh.update()
	bm.free()

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


def secondsToStr(t):
	rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
	return "%d:%02d:%02d.%03d" % tuple(functools.reduce(rediv,[[t*1000,],1000,60,60]))