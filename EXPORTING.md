# bpyhullgen Exporting

## Introduction
A simple UI with some features to manipulate and export the hull model for production has been provided for testing and experimenting. 
![Quick Hull Plates](images/2019_11_20_export/export.png)

## Status
The export workflow is is work in progress and there is not a single button to do everything so it's split into separate steps to make further development and debugging easier. 

#### ApplyAllBool 
This function will apply all boolean modifers and assign a unique (name hash based) color to each face based on which boolean object was used for the boolean modifier (chine panel). This step is necessary before exporting. Having different colors assigned to each chine panel is useful for separating the panels after the boolean modifier is applied and also visualizing which panels are contiguous.

#### Separate by material
After the ApplyAllBool function is performed Separate by Material function will split the hull into separate panels based on the colors assigned during the apply all bool step.

#### ExportPlates
If you select all the plates and use this function it will export a SVG file showing all the individual plates separated with crease lines. You must first ApplyAllBool and SeparateByMaterial before you use this function or it may fail.

#### ImportPlates
This function imports the previously exported SVG file as a set of curves then removes all the crease lines and converts to a mesh.

#### ExportDXF
This function exports a set of plates to DXF for CAD/CAM cutting. You must first do the previous steps (up to ImportPlates) before doing this step. 


#### GenScene
This function is used to add a generic curved backdrop to the scene for rendering and visualization purposes. 

#### DeleteAll 
This function deletes all the mesh objects but leaves lights, empties and camera. It was used during the development process and remains for convenience and debugging.

#### Solidify Selections
This assigns a solidify modifer to each selected panel for visualization and rendering purposes. The current thickness is 0.1 but should be adjustable in the future. For now if you want a different thickness you can modify the code.

#### exportCSV
This function will export a hull_export.csv file showing the area and volume of each face for calculating material weight and cost.

![Quick Hull](images/2019_11_20_export/csv_export.png)

You can use a spreadsheet program to calculate total weight based on the chosen material. The numbers displayed are cubic meters (m3).

## Example exported hull model
![Quick Hull](images/2019_11_20_export/quick_hull.png)
Quick Hull sample model from included tests directory

![Quick Hull Plates](images/2019_11_20_export/export_plate_svg.png)
Plate file SVG showing bend creases

![Quick Hull Plates](images/2019_11_20_export/export_dxf.png)
Preview of DXF file output for CAD/CAM cutting

[Exported DXF file](images/2019_11_20_export/export.dxf) 


## TODO
Laser cut a paper or wood sheet model to produce a real object to validate the model is working correctly and all the panels fit together correctly.

I have not tested exporting bulkheads and stringers yet... This work focuses on the exterior panel sheets only for now.
