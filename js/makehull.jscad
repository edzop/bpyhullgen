function make_cutter(length,width,height,curve_depth) {
    var curvedepth=width*curve_depth
    var path=new CSG.Path2D([[-length,0],[length,0]],false);
    
    var curve_margin=length*0.9
    
    path = path.appendPoint([length,width]);
    path = path.appendPoint([curve_margin,width]);
    path = path.appendBezier([[curve_margin,width],[0,curvedepth],[-curve_margin,width]])
    path = path.appendPoint([-curve_margin,width]);
    path = path.appendPoint([-length,width]);
    path = path.close(); // close the path
    
    // close the path and convert to a solid 2D shape:
    path = path.close();
    var cag = path.innerToCAG();
    
    ext=cag.extrude({ offset: [0, 0, height*1.1]});
    ext=ext.setColor(1,0,0);
    
    return ext;
}

function makehull(length,width,height) {
    var h=CSG.cube({radius: [length, width, height]});

    h=h.setColor(0.3,0.3,1);
    return h
}

// Here we define the user editable parameters:
function getParameterDefinitions () {
  return [
    { name: 'hull_length', caption: 'hull_length:', type: 'float', initial: 20, min: 5, max: 100, step: 1 },
    { name: 'hull_width', caption: 'hull_width', type: 'float', initial: 6 },
    { name: 'hull_height', caption: 'hull_height', type: 'float', initial: 5 },
    { name: 'curve_depth', caption: 'curve depth', type: 'float', initial: -0.8 },
    { name: 'curve_offset', caption: 'curve offset', type: 'float', initial: 0.5, step: 0.1 },
  ];
}

function main() {
    var result = [];
    
    centercube=CSG.cube({radius: 0.5});
    centercube.setColor(css2rgb('dodgerblue'));
    result.push(centercube);
    
    cutter=make_cutter(
        params.hull_length,
        params.hull_width,
        params.hull_height,
        params.curve_depth
    );
    
    cutter=cutter.rotateZ(180)
    cutter=cutter.translate([0,params.hull_width,0])
    
    
    // a small slice of cutter to help visualize what it's doing
    cutter_vis=cutter.scale([1,1,0.1])
    cutter_vis=cutter_vis.translate([0,0,params.hull_height*0.7])
    
    cutter_vis=cutter_vis.setColor(0,1,0,0.4)
    result.push(cutter_vis);
    
    var hull = makehull(
        params.hull_length,
        params.hull_width,
        params.hull_height
    );
    
    cutter=cutter.translate([0,params.curve_offset,0])
    cutter2=cutter.rotateZ(180)
    
    output=hull.subtract(cutter);
    output=output.subtract(cutter2);
  
    result.push(output)
    
    return result;
}
