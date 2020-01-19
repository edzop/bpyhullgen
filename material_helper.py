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
 
    mat=mat = bpy.data.materials.new(name)
        
    mat.use_nodes=True
    tree=mat.node_tree
    nodes=tree.nodes
    
    delete_all_nodes_except_output_material(nodes)
    
    links = mat.node_tree.links

    nodeGlossy = nodes.new(type='ShaderNodeBsdfGlossy')
    nodeGlossy.location=-200,100
    nodeGlossy.inputs[1].default_value=0
    
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

	node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
	node_color_ramp.color_ramp.elements[0].position=0.49
	node_color_ramp.color_ramp.elements[1].position=0.51
	node_color_ramp.location = -200,300
	
	links.new(node_separateXYZ.outputs[1], node_color_ramp.inputs[0])
	

	node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
	node_transparent.location = 100,-300

	node_mix = nodes.new(type='ShaderNodeMixShader')
	node_mix.location=450,200
	links.new(node_color_ramp.outputs[0], node_mix.inputs[0])
	
	links.new(node_transparent.outputs[0], node_mix.inputs[1])
	links.new(node_principled_bsdf.outputs[0], node_mix.inputs[2])
	
	node_output=nodes['Material Output']
	node_output.location=800,0

	links.new(node_mix.outputs[0], node_output.inputs[0])

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
