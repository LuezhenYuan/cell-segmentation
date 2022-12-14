//How to use this macro
//Open fluorescent image
//Open the outline of cell segment when the pop up window show
//Then open the outline of nucleus segment when the pop up window show
img_filename="1-cell-img" //"1-cell-img.tif"

img_path="E:/PSI-backup/2022-12-13 Vanessa Tissue Image Collagen/M1W3_Col1_DAPI_s29_20X/M1_W_3_DAPI_Col1_s29_40X/M1_W_3_DAPI_Col1_s29_40X_001/"
run("Stack to Images");
//run("Close");
selectWindow(img_filename+"-0002");
script_path="E:/PSI-backup/2022-12-13 Vanessa Tissue Image Collagen/analysis/imageJ_roi_converter.py"
//run("script:"+script_path+"");
runMacro(script_path);
roiManager("Show All without labels");
run("Set Measurements...", "area mean perimeter shape feret's redirect=None decimal=3");
roiManager("Measure");
saveAs("Results", img_path+img_filename+"-cell-measure.csv");
roiManager("Delete");
run("Clear Results");
//run("script:"+script_path);
runMacro(script_path);
selectWindow(img_filename+"-0001");
roiManager("Show All without labels");
roiManager("Measure");
saveAs("Results", img_path+img_filename+"-nucleus-measure.csv");
//roiManager("Delete");
//run("Clear Results");