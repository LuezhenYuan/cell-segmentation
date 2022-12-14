//How to use this macro
//Open fluorescent image
//Open the outline of cell segment when the pop up window show
//Then open the outline of nucleus segment when the pop up window show
img_filename="3-cell-img" //"1-cell-img.tif"

img_path="E:/PSI-backup/2022-08 Hui heterochromatin/batch 4 of model 2 data/01.08.2022 large image 533rH2X, 647aSMA, 488 actin, DAPI/old load/old load 533rH2X, 647aSMA, 488actin002"
run("Stack to Images");
//run("Close");
selectWindow(img_filename+"-0002");
script_path="E:/PSI-backup/2022-08 Hui heterochromatin/cell-segmentation/imageJ_roi_converter.py"
//run("script:"+script_path+"");
runMacro(script_path);
roiManager("Show All without labels");
run("Set Measurements...", "area mean perimeter shape feret's redirect=None decimal=3");
roiManager("Measure");
saveAs("Results", img_path+img_filename+"-cell-measure.csv");
//roiManager("Delete");
//run("Clear Results");