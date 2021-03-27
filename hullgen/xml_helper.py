import xml.etree.ElementTree as ET
import xml.dom.minidom
import os

from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import chine_helper
from bpyhullgen.hullgen import keel_helper
from bpyhullgen.hullgen import bulkhead
from bpyhullgen.hullgen import modshape_helper


def pretty_print_xml_given_root(root, output_xml):
    """
    Useful for when you are editing xml data on the fly
    """
    xml_string = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()
    xml_string = os.linesep.join([s for s in xml_string.splitlines() if s.strip()]) # remove the weird newline issue
    with open(output_xml, "w") as file_out:
        file_out.write(xml_string)

def pretty_print_xml_given_file(input_xml, output_xml):
    """
    Useful for when you want to reformat an already existing xml file
    """
    tree = ET.parse(input_xml)
    root = tree.getroot()
    pretty_print_xml_given_root(root, output_xml)


def dump_hull(the_hull):
    print("Size: (L: %f W: %f H: %f)"%(the_hull.hull_length,
        the_hull.hull_width,
        the_hull.hull_height))

    print("bulkhead: (start: %f count: %f thickness: %f)"%(the_hull.start_bulkhead_location,
        the_hull.bulkhead_count,
        the_hull.bulkhead_thickness))

    for chine in the_hull.chine_list:
        print("chine '%s': curve(%f %f %f) extrude_width: %f offset(%f %f %f) rotation(%f %f %f) symmetrical %d A0 %f A1 %f"%(
            chine.name,
            chine.curve_length,
            chine.curve_width,
            chine.curve_height,
            chine.extrude_width,
            chine.offset[0],
            chine.offset[1],
            chine.offset[2],
            chine.rotation[0],
            chine.rotation[1],
            chine.rotation[2],
            chine.symmetrical,
            chine.asymmetry[0],
            chine.asymmetry[1]))

def parse_int_val(elem,name,default=0):
    val=default
    if name in elem.attrib:
        if elem.attrib[name]!=None:
            val = int(elem.attrib[name])
    return val

def parse_float_val(elem,name,default=0):
    val=default
    if name in elem.attrib:
        if elem.attrib[name]!=None:
            val = float(elem.attrib[name])
    return val

def parse_str_val(elem,name,default="?"):
    val=default
    if name in elem.attrib:
        if elem.attrib[name]!=None:
            val = elem.attrib[name]
    return val    

def read_hull(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    newhull=hull_maker.hull_maker(0,0,0)


    for elem in root:

        #================================================================
        if elem.tag=="size":
            newhull.hull_width=parse_float_val(elem,"width",0)
            newhull.hull_length=parse_float_val(elem,"length",0)
            newhull.hull_height=parse_float_val(elem,"height",0)

        #================================================================
        if elem.tag=="materials":
            newhull.structural_thickness=parse_float_val(elem,"structural_thickness",0.1)
            newhull.slicer_overcut_ratio=parse_float_val(elem,"slicer_overcut_ratio",1.1)
            newhull.slot_gap=parse_float_val(elem,"slot_gap",0.1)

        #================================================================
        if elem.tag=="generate":
            newhull.make_bulkheads=parse_int_val(elem,"bulkheads",default=True)
            newhull.make_keels=parse_int_val(elem,"keels",default=True)
            newhull.make_longitudals=parse_int_val(elem,"longitudals",default=True)
            newhull.hide_hull=parse_int_val(elem,"hide_hull",default=False)


        #================================================================
        if elem.tag=="bulkheads":

            for bulkhead_elem in elem:
                floor_height=parse_float_val(bulkhead_elem,"floor_height",0)
                watertight=parse_int_val(bulkhead_elem,"watertight",default=True)
                station=parse_float_val(bulkhead_elem,"station",0)
                thickness=parse_float_val(bulkhead_elem,"thickness",0)

                bulkhead_definition=bulkhead.bulkhead_definition(
                    station=station,
                    watertight=watertight,
                    floor_height=floor_height,
                    thickness=thickness)

                newhull.add_bulkhead_definition(bulkhead_definition)

        #================================================================
        if elem.tag=="modshapes":

            for modshape_elem in elem:

                name=parse_str_val(modshape_elem,"name",0)
                mod_type=parse_str_val(modshape_elem,"mod_type","add")
                mod_mode=parse_str_val(modshape_elem,"mod_mode","cube")
                mod_shape=parse_str_val(modshape_elem,"mod_shape","trapezoid")
                symmetrical=parse_int_val(modshape_elem,"symmetrical",default=True)

                size=[0,0,0]
                rotation=[0,0,0]
                location=[0,0,0]
                deform=[0,0,0]

                for subelem in modshape_elem:

                    if subelem.tag=="rotation":
                        rotation[0]=parse_float_val(subelem,"x",0)
                        rotation[1]=parse_float_val(subelem,"y",0)
                        rotation[2]=parse_float_val(subelem,"z",0)

                    if subelem.tag=="location":
                        location[0]=parse_float_val(subelem,"x",0)
                        location[1]=parse_float_val(subelem,"y",0)
                        location[2]=parse_float_val(subelem,"z",0)

                    if subelem.tag=="size":
                        size[0]=parse_float_val(subelem,"x",0)
                        size[1]=parse_float_val(subelem,"y",0)
                        size[2]=parse_float_val(subelem,"z",0)

                    if subelem.tag=="deform":
                        deform[0]=parse_float_val(subelem,"p1",0)
                        deform[1]=parse_float_val(subelem,"p2",0)
                        deform[2]=parse_float_val(subelem,"p3",0)

                modshape=modshape_helper.modshape(
                    name=name,
                    rotation=rotation,
                    location=location,
                    size=size,
                    mod_mode=mod_mode,
                    deform=deform,
                    mod_shape=mod_shape,
                    symmetrical=symmetrical)

                newhull.add_modshape(modshape)

        #================================================================
        if elem.tag=="keels":

            for keel_elem in elem:

                station_start=parse_float_val(keel_elem,"station_start",0)
                station_end=parse_float_val(keel_elem,"station_end",0)
                lateral_offset=parse_float_val(keel_elem,"lateral_offset",0)
                top_height=parse_float_val(keel_elem,"top_height",0)

                keel = keel_helper.keel(newhull,lateral_offset,top_height,station_start,station_end)

                newhull.add_keel(keel)


        #================================================================
        if elem.tag=="chines":

            for chine_elem in elem:

                name=parse_str_val(chine_elem,"name")
                symmetrical=parse_int_val(chine_elem,"symmetrical",default=True)
                length=11
                width=1.2
                height=1.2
                extrude_width=1.2
                
                offset=[0,0,0]
                rotation=[0,0,0]
                asymmetry=[0,0]

                longitudal_defs=[]

                for subelem in chine_elem:

                    if subelem.tag=="curve":
                        length=parse_float_val(subelem,"length",length)
                        width=parse_float_val(subelem,"width",width)
                        height=parse_float_val(subelem,"height",height)
                        extrude_width=parse_float_val(subelem,"extrude_width",extrude_width)

                    if subelem.tag=="asymmetry":
                        asymmetry[0]=parse_float_val(subelem,"a0",0)
                        asymmetry[1]=parse_float_val(subelem,"a1",0)


                    if subelem.tag=="offset":
                        offset[0]=parse_float_val(subelem,"x",0)
                        offset[1]=parse_float_val(subelem,"y",0)
                        offset[2]=parse_float_val(subelem,"z",0)

                    if subelem.tag=="rotation":
                        rotation[0]=parse_float_val(subelem,"x",0)
                        rotation[1]=parse_float_val(subelem,"y",0)
                        rotation[2]=parse_float_val(subelem,"z",0)

                    if subelem.tag=="longitudals":

                        for longitudal_elem in subelem:
                            z_offset=0
                            longitudal_width=1
                            x_min=-3
                            x_max=3

                            z_offset=parse_float_val(longitudal_elem,"z_offset",z_offset)
                            longitudal_width=parse_float_val(longitudal_elem,"width",width)
                            x_min=parse_float_val(longitudal_elem,"x_min",x_min)
                            x_max=parse_float_val(longitudal_elem,"x_max",x_max)

                            longitudal_definition=chine_helper.longitudal_definition(
                                width=longitudal_width,z_offset=z_offset
                            )

                            longitudal_definition.set_limit_x_length(x_min,x_max)

                            longitudal_defs.append(longitudal_definition)


                new_chine=chine_helper.chine_helper(newhull,
                    name=name,length=length,width=width,
                    symmetrical=symmetrical,
                    asymmetry=asymmetry)

                new_chine.curve_height=height
                new_chine.offset=offset
                new_chine.rotation=rotation
                new_chine.extrude_width=extrude_width

                for ld in longitudal_defs:
                    new_chine.add_longitudal_definition(ld)

                newhull.add_chine(new_chine)
  
    return newhull


def write_xml(the_hull,filename):
    # create the file structure
    hull = ET.Element('hull')

    #data.set('data','vvv')


    #================================================================
    size = ET.SubElement(hull, "size")
    size.set('length',str(the_hull.hull_length))
    size.set("width", str(the_hull.hull_width))
    size.set("height", str(the_hull.hull_height))

    #================================================================
    size = ET.SubElement(hull, "materials")
    size.set('structural_thickness',str(the_hull.structural_thickness))
    size.set('slicer_overcut_ratio',str(the_hull.slicer_overcut_ratio))
    size.set('slot_gap',str(the_hull.slot_gap))


    #================================================================
    size = ET.SubElement(hull, "generate")
    size.set('bulkheads',str(int(the_hull.make_bulkheads)))
    size.set("keels", str(int(the_hull.make_keels)))
    size.set("longitudals", str(int(the_hull.make_longitudals)))
    size.set("hide_hull", str(int(the_hull.hide_hull)))

    #================================================================
    node_bulkheads = ET.SubElement(hull, "bulkheads")

    for bulkhead_definition in the_hull.bulkhead_definitions:
        node_bulkhead=ET.SubElement(node_bulkheads, 'bulkhead')

        node_bulkhead.set("station", str(bulkhead_definition.station))
        node_bulkhead.set("floor_height", str(bulkhead_definition.floor_height))
        node_bulkhead.set("watertight", str(int(bulkhead_definition.watertight)))
        node_bulkhead.set("thickness", str(bulkhead_definition.thickness))


    #================================================================
    node_keels = ET.SubElement(hull, 'keels')

    for keel in the_hull.keel_list:
        node_keel=ET.SubElement(node_keels, 'keel')

        node_keel.set('lateral_offset',str(keel.lateral_offset))
        node_keel.set('top_height',str(keel.top_height))

        node_keel.set('station_start',str(keel.station_start))
        node_keel.set('station_end',str(keel.station_end))


    #================================================================
    node_modshapes = ET.SubElement(hull, 'modshapes')

    for modshape in the_hull.modshapes:
        node_modshape=ET.SubElement(node_modshapes, 'modshape')

        node_modshape.set("name",modshape.name)
        node_modshape.set("mod_mode",modshape.mod_mode)
        node_modshape.set("mod_type",modshape.mod_type)
        node_modshape.set("mod_shape",modshape.mod_shape)
        node_modshape.set("symmetrical",str(int(modshape.symmetrical)))

        node_location = ET.SubElement(node_modshape, "location")
        node_location.set('x',str(modshape.location[0]))
        node_location.set("y", str(modshape.location[1]))
        node_location.set("z", str(modshape.location[2]))

        node_rotation = ET.SubElement(node_modshape, "rotation")
        node_rotation.set('x',str(modshape.rotation[0]))
        node_rotation.set("y", str(modshape.rotation[1]))
        node_rotation.set("z", str(modshape.rotation[2]))

        node_size = ET.SubElement(node_modshape, "size")
        node_size.set('x',str(modshape.size[0]))
        node_size.set("y", str(modshape.size[1]))
        node_size.set("z", str(modshape.size[2]))

        node_deform = ET.SubElement(node_modshape, "deform")
        node_deform.set('p1',str(modshape.deform[0]))
        node_deform.set("p2", str(modshape.deform[1]))
        node_deform.set("p3", str(modshape.deform[2]))


    #================================================================
    node_chines = ET.SubElement(hull, 'chines')

    for chine in the_hull.chine_list:
        node_chine=ET.SubElement(node_chines, 'chine')

        node_chine.set("name",chine.name)
        node_chine.set("symmetrical", str(int(chine.symmetrical)))

        node_curve = ET.SubElement(node_chine, "curve")
        node_curve.set('length',str(chine.curve_length))
        node_curve.set("width", str(chine.curve_width))
        node_curve.set("height", str(chine.curve_height))
        node_curve.set("extrude_width", str(chine.extrude_width))

        node_offset = ET.SubElement(node_chine, "offset")
        node_offset.set('x',str(chine.offset[0]))
        node_offset.set("y", str(chine.offset[1]))
        node_offset.set("z", str(chine.offset[2]))

        node_rotation = ET.SubElement(node_chine, "rotation")
        node_rotation.set('x',str(chine.rotation[0]))
        node_rotation.set("y", str(chine.rotation[1]))
        node_rotation.set("z", str(chine.rotation[2]))

        node_asymmetry = ET.SubElement(node_chine, "asymmetry")
        node_asymmetry.set('a0',str(chine.asymmetry[0]))
        node_asymmetry.set("a1", str(chine.asymmetry[1]))

        node_longitudals = ET.SubElement(node_chine, 'longitudals')

        for longitudal_definition in chine.longitudal_definitions:
            node_longitudal=ET.SubElement(node_longitudals, 'longitudal')

            node_longitudal.set("z_offset", str(longitudal_definition.z_offset))
            node_longitudal.set("width", str(longitudal_definition.width))
            node_longitudal.set("x_min", str(longitudal_definition.limit_x_min))
            node_longitudal.set("x_max", str(longitudal_definition.limit_x_max))



    pretty_print_xml_given_root(hull,filename)


