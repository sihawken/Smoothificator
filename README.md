# Smoothificator (modified for Orcaslicer and Bambu Printers)
Important: Please look at the output of this script in a gcode viewer in order to make sure that this script isn't doing anything silly.
I put a lot of time and effort into making this work, but the work was fast and scrappy. There are no guarantees it'll work!

A script that enables you to 3D print with different Layerheights on the inside and outside of your print

You can use it in Prusaslicer and Orcaslicer. It is not the same as "combine infill every x layer" because the script only changes the outer walls. That means that you can even print top/bottomlayers + inside walls with a bigger layerheight to save a ton of time. 

Make sure that you have Python installed.
To run it use it as a postprocessing script in the slicer like this:

```"C:\Path\To\Python\python.exe" "C:\Path\To\Script\Smoothificator.py" -outerLayerHeight```

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/MffF5_rbtW8/0.jpg)](https://www.youtube.com/watch?v=MffF5_rbtW8)


If you want to go crazy and forexample print the inside with 0.4mm and the outer perimeters with 0.05mm, you should probably consider enabling the "External perimeters first" option.
