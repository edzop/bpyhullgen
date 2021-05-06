
from bpyhullgen.bpyutils import bpy_helper

t = bpy_helper.ElapsedTimer()

for i in range(1,10):
    for b in range(1,1000):
        v=i*b
        for c in range(1,1000):
            z=i*b*c

print(t.get_elapsed_string())


