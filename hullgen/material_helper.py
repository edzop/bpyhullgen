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

def make_subsurf_material(name,color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	shader_node = nodes['Principled BSDF']
	#color=[1,0.3,0.3,1]
	shader_node.inputs[0].default_value=color

	# subsurf
	shader_node.inputs[1].default_value=1
	shader_node.inputs[3].default_value=color

	mat.diffuse_color=shader_node.inputs[0].default_value
	return mat


def make_glass_material(name,color):
 
	mat = bpy.data.materials.new(name)
		
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes
	
	delete_all_nodes_except_output_material(nodes)
	
	links = mat.node_tree.links

	nodeGlossy = nodes.new(type='ShaderNodeBsdfGlossy')
	nodeGlossy.location=-200,100
	nodeGlossy.inputs[1].default_value=0
	nodeGlossy.inputs[0].default_value=color
	
	node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
	node_transparent.location = -200,-100
	#node_transparent.inputs[2]=1.01

	node_mix = nodes.new(type='ShaderNodeMixShader')
	node_mix.location=0,0
	node_mix.inputs[0].default_value=0.776
	
	
	links.new(nodeGlossy.outputs[0], node_mix.inputs[1])
	links.new(node_transparent.outputs[0], node_mix.inputs[2])
	
	node_output=nodes['Material Output']
	node_output.location=200,0

	links.new(node_mix.outputs[0], node_output.inputs[0])

	return mat

def make_metalic_material(name,color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes

	shader_node = nodes['Principled BSDF']
	#color=[1,0.3,0.3,1]
	shader_node.inputs[0].default_value=color

	# metalic
	shader_node.inputs[4].default_value=0.67

	# roughness
	shader_node.inputs[7].default_value=0.277

	mat.diffuse_color=shader_node.inputs[0].default_value
	return mat


def make_diffuse_material(name,color):
	delete_material(name)
	new_material = bpy.data.materials.new(name)
	#print(color)
	new_material.diffuse_color = color
	return new_material

def get_material_support(): 
	material_name="support"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_subsurf_material(material_name,[0.8,0.3,0.3,1])

def get_material_stringer(): 
	material_name="cutter"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_subsurf_material(material_name,[0.2,0.8,0.3,1])


def get_material_bolts(): 
	material_name="bolts"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_metalic_material(material_name,[0.7,0.7,0.7,1])

def get_material_window(): 
	material_name="window"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_glass_material(material_name,[0.7,0.7,0.7,1])


def get_material_default():
	material_name="default"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_diffuse_material(material_name,[0.8,0.8,0.8,1])

def get_material_bulkhead(): 
	material_name="bulkhead"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_subsurf_material(material_name,[0.5,0.5,0.9,1])


def get_material_bool(): 
	material_name="bool"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_subsurf_material(material_name,[1,0.3,0.3,1])

def get_material_fueltank(): 
	material_name="fueltank"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_subsurf_material(material_name,[0.6,0.6,0,1])	


def disable_cutaway(mat):
	#mat=bpy.data.materials["hull"]
	#print(mat.name)
	node_tree=mat.node_tree
	nodes=node_tree.nodes
	links = mat.node_tree.links

	#for n in nodes:
	#	print(n)
		
	node_mix_shader = nodes['Mix Shader']

	l = node_mix_shader.inputs[0].links[0]
	node_tree.links.remove(l)

	node_mix_shader.inputs[0].default_value=1


def get_material_hull():
	material_name="hull"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	mat=make_subsurf_material(material_name,[1,1.0,1.0,1])
	
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes
	links = mat.node_tree.links

	node_principled_bsdf = nodes['Principled BSDF']
	node_principled_bsdf.location=100,300


	node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
	node_tex_coord.location=-600,300


	node_separateXYZ = nodes.new(type='ShaderNodeSeparateXYZ')
	node_separateXYZ.location=-400,300
	
	links.new(node_tex_coord.outputs[0], node_separateXYZ.inputs[0])

	
	node_color_math = nodes.new(type='ShaderNodeMath')
	node_color_math.operation = 'GREATER_THAN'
	node_color_math.inputs[1].default_value = 0.5
	node_color_math.location = -200,300
	
	links.new(node_separateXYZ.outputs[1], node_color_math.inputs[0])
	

	node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
	node_transparent.location = 100,-300

	node_mix = nodes.new(type='ShaderNodeMixShader')
	node_mix.location=450,200
	links.new(node_color_math.outputs[0], node_mix.inputs[0])
	
	links.new(node_transparent.outputs[0], node_mix.inputs[1])
	links.new(node_principled_bsdf.outputs[0], node_mix.inputs[2])
	
	node_output=nodes['Material Output']
	node_output.location=800,0

	links.new(node_mix.outputs[0], node_output.inputs[0])

	return mat

def plates_to_aluminum():
	al_mat = get_aluminum_material()

	list_of_prefix=[ 
					 "Bulkhead",
					 "cutterchine",
					 "hull_object",
					 "Keel"
					]

	for o in bpy.data.objects:
		if o.type=="MESH":
			for pre in list_of_prefix:
				if o.name.startswith(pre):
					assign_material(o,al_mat)


def get_aluminum_material(): 
	material_name="aluminum"

	if material_name in bpy.data.materials:
		return bpy.data.materials[material_name]

	return make_aluminum_material(material_name)

def make_aluminum_material(material_name):

	mat = bpy.data.materials.new(material_name)
		
	mat.use_nodes=True
	tree=mat.node_tree
	nodes=tree.nodes
	
	#delete_all_nodes_except_output_material(nodes)
	
	links = mat.node_tree.links

	xpos=-400
	xinc=200



	node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
	node_tex_coord.location=xpos,0

	xpos+=xinc
	
	node_tex_noise = nodes.new(type='ShaderNodeTexNoise')
	node_tex_noise.location=xpos,100
	node_tex_noise.inputs[2].default_value=40
	node_tex_noise.inputs[3].default_value=5

	links.new(node_tex_coord.outputs[3], node_tex_noise.inputs[0])

	node_tex_mapping = nodes.new(type='ShaderNodeMapping')
	node_tex_mapping.location=xpos,-200
	node_tex_mapping.inputs[3].default_value[2]=500

	links.new(node_tex_coord.outputs[0], node_tex_mapping.inputs[0])


	xpos+=xinc

	node_tex_musgrave = nodes.new(type='ShaderNodeTexMusgrave')
	node_tex_musgrave.location=xpos,-200
	node_tex_musgrave.inputs[2].default_value=6
	node_tex_musgrave.inputs[3].default_value=0.3
	node_tex_musgrave.inputs[4].default_value=0
	node_tex_musgrave.inputs[5].default_value=1


	links.new(node_tex_mapping.outputs[0], node_tex_musgrave.inputs[0])

	xpos+=xinc

	node_tex_rampbump = nodes.new(type='ShaderNodeValToRGB')
	node_tex_rampbump.location=xpos,-150
	node_tex_rampbump.name="bump"
	node_tex_rampbump.color_ramp.elements[0].position=0.1
	node_tex_rampbump.color_ramp.elements[1].position=0.3

	links.new(node_tex_musgrave.outputs[0], node_tex_rampbump.inputs[0])

	node_tex_ramp2 = nodes.new(type='ShaderNodeValToRGB')
	node_tex_ramp2.location=xpos,150
	node_tex_ramp2.name="ramp2"
	node_tex_ramp2.color_ramp.elements[0].position=0.49
	node_tex_ramp2.color_ramp.elements[1].position=0.66

	node_tex_ramp2.color_ramp.elements[0].color=[.41,.41,.41,1]
	node_tex_ramp2.color_ramp.elements[1].color=[.51,.51,.51,1]

	links.new(node_tex_noise.outputs[0], node_tex_ramp2.inputs[0])

	xpos+=xinc*1.5

	node_tex_math1 = nodes.new(type='ShaderNodeMath')
	node_tex_math1.location=xpos,-100
	node_tex_math1.name="roughness"
	node_tex_math1.operation="MULTIPLY"
	node_tex_math1.use_clamp=True
	node_tex_math1.inputs[1].default_value=1.2
	

	node_tex_math2 = nodes.new(type='ShaderNodeMath')
	node_tex_math2.location=xpos,100
	node_tex_math2.name="metallic"
	node_tex_math2.operation="MULTIPLY"
	node_tex_math2.use_clamp=True
	node_tex_math2.inputs[1].default_value=2.4

	node_tex_math3 = nodes.new(type='ShaderNodeMath')
	node_tex_math3.location=xpos,-300
	node_tex_math3.name="bump"
	node_tex_math3.operation="MULTIPLY"
	node_tex_math3.use_clamp=True
	node_tex_math3.inputs[1].default_value=0.005


	xpos+=xinc

	links.new(node_tex_ramp2.outputs[0], node_tex_math2.inputs[0])
	links.new(node_tex_ramp2.outputs[0], node_tex_math1.inputs[0])

	links.new(node_tex_rampbump.outputs[0], node_tex_math3.inputs[0])

	xpos+=xinc*1.5

	node_principled_bsdf = nodes['Principled BSDF']
	node_principled_bsdf.location=xpos,200

	links.new(node_tex_math1.outputs[0], node_principled_bsdf.inputs[7])
	links.new(node_tex_math2.outputs[0], node_principled_bsdf.inputs[4])

	links.new(node_tex_ramp2.outputs[0], node_principled_bsdf.inputs[0])


	xpos+=xinc*1.5

	node_output=nodes['Material Output']
	node_output.location=xpos,0

	links.new(node_tex_math3.outputs[0], node_output.inputs[2])



	return mat


def assign_material(ob,mat):
	# Assign it to object
	if ob.data.materials:
	# assign to 1st material slot
		ob.data.materials[0] = mat
	else:
	# no slots
		ob.data.materials.append(mat)


def delete_material(material_name):
	for m in bpy.data.materials:
		if m.name==material_name:
			bpy.data.materials.remove(m)

# delete all nodes except output material
def delete_all_nodes_except_output_material(nodes):
	for node in nodes:
		if node.type != 'OUTPUT_MATERIAL': # skip the material output node as we'll need it later
			nodes.remove(node)
