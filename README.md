# bpyhullgen
bpyhullgen is a Blender based Parametric Hull Generator

NOTE: bpyhullgen in it's current state will only work with 2.91 development or later. 

Versions of blender prior to 2.91 have a bug with boolean modifier - coplanar overlapping faces would cause irratic results. 

[New Boolean](https://blenderartists.org/t/new-boolean/1245336) implementation fixed this problem and will be part of blender 2.91 - not yet released as of today (Oct 7th 2020)

bpyhullgen has just undergone a major refactor to use the newboolean modifier that will be released with 2.91.



bpyhullgen was started for the purpose of generating parametric boat hull designs that can easily converted to real world objects. 

One of the design goals of the project is to generate hulls with curves and surfaces that result in easily developable faces that can be cut from plate surfaces such as plywood, steel plate or aluminum plate and will bend and assemble together with minimal distortion and manipulation. 

## Documentation
For further information please refer to [bpyhullgen Github Wiki](https://github.com/edzop/bpyhullgen/wiki)

![](images/2019_10_15_v05.png)
Example showing bulkheads and stringers and one stringer removed to show notching in both bulkhead and stringer.

See related project: [bpyhullsim](https://github.com/edzop/bpyhullsim)

