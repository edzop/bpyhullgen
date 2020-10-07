
from bpyhullgen.hullgen import xml_helper
from bpyhullgen.hullgen import hull_maker
from bpyhullgen.hullgen import chine_helper

the_hull=hull_maker.hull_maker(width=3,length=7,height=2)

for v in range(0,3):

    new_chine=chine_helper.chine_helper(the_hull,
	    name="side_%d"%v,length=9+v,width=1.6+v)

    new_chine.extrude_width=v+6
    new_chine.offset=[v,v+1,v+2]
    new_chine.rotation=[v+2,v+3,v+4]
    the_hull.add_chine(new_chine)

filename="test.xml"

xml_helper.write_xml(the_hull,filename)

hull_2 = xml_helper.read_hull(filename)

xml_helper.dump_hull(hull_2)