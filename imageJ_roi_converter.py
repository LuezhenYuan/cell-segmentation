# downloaded from cellpose: https://github.com/Image-Py/cellpose-turbo/blob/master/imagej_roi_converter.py
# Run this code in ImageJ macro, and then select text file containing coordinates of the contour (outline) of each roi.
# The format of the text file is:
# x1,y1,x2,y2,x3,y3 ... for roi 1
# x1,y1,x2,y2,x3,y3 ... for roi 2
from ij import IJ
from ij.plugin.frame import RoiManager
from ij.gui import PolygonRoi
from ij.gui import Roi
from java.awt import FileDialog

fd = FileDialog(IJ.getInstance(), "Open", FileDialog.LOAD)
fd.show()
file_name = fd.getDirectory() + fd.getFile()
print(file_name)

RM = RoiManager()
rm = RM.getRoiManager()

imp = IJ.getImage()

textfile = open(file_name, "r")
for line in textfile:
    xy = map(int, line.rstrip().split(","))
    X = xy[::2]
    Y = xy[1::2]
    imp.setRoi(PolygonRoi(X, Y, Roi.POLYGON))
    # IJ.run(imp, "Convex Hull", "")
    roi = imp.getRoi()
    print(roi)
    rm.addRoi(roi)
textfile.close()
rm.runCommand("Associate", "true")
rm.runCommand("Show All with labels")