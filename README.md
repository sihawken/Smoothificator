# Smoothificator
A script that enables you to 3D print with different Layerheights on the inside and outside of your print

You can use it in Prusaslicer and Orcaslicer. It is not the same as "combine infill every x layer" because the script only changes the outer walls. That means that you can even print top/bottomlayers + inside walls with a bigger layerheight to save a ton of time. 

Make sure that you have Python installed.
To run it use it as a postprocessing script in the slicer like this:

```"C:\Path\To\Python\python.exe" "C:\Path\To\Script\Smoothificator.py" -outerLayerHeight```

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/MffF5_rbtW8/0.jpg)](https://www.youtube.com/watch?v=MffF5_rbtW8)
