# Smoothificator (modified for Orcaslicer and Bambu Printers)
Important: Please look at the output of this script in a gcode viewer in order to make sure that this script isn't doing anything silly.
I put a lot of time and effort into making this work, but the work was fast and scrappy. Therefore I am very likely to have missed something. There are no guarantees it'll work! Tested on a P1S with orcaslicer. 

Added features:
- skipLayers <int> : Number of layers to skip. Default is 1.
- feedrateScale <float> : Number from 0 to 1. Feedrate scale of zero keeps the same printing velocity, feedrate scale of one adjusts the velocity to keep the original volumetric flow rate. Default is 0.

Known incompatibilities: 
 - Scarf seams: The implementation of the height adjustment is not optimal, and relies on discreet layer heights coming from the slicer.

A script that enables you to 3D print with different Layerheights on the inside and outside of your print

You can use it in Prusaslicer and Orcaslicer. It is not the same as "combine infill every x layer" because the script only changes the outer walls. That means that you can even print top/bottomlayers + inside walls with a bigger layerheight to save a ton of time. 

Make sure that you have Python installed.
To run it use it as a postprocessing script in the slicer like this:

```"C:\Path\To\Python\python.exe" "C:\Path\To\Script\Smoothificator_Adaptive.py" [-outerLayerHeight] [-skipLayers] [-feedrateScale]```

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/MffF5_rbtW8/0.jpg)](https://www.youtube.com/watch?v=MffF5_rbtW8)


If you want to go crazy and forexample print the inside with 0.4mm and the outer perimeters with 0.05mm, you should probably consider enabling the "External perimeters first" option.
