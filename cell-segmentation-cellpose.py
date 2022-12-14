import nd2
import sys
import numpy as np
import cv2 as cv
from skimage import io
from scipy import ndimage

file_name = sys.argv[1] # "../batch 4 of model 2 data/01.08.2022 large image 533rH2X, 647aSMA, 488 actin, DAPI/old load/old load 533rH2X, 647aSMA, 488actin002/3.nd2"

#model_path = sys.argv[2] # "models/MultiplexSegmentation"
output_pre = file_name.rsplit('.', 1)[0]

pixel_size = 0.2999424 # 0.4315837 # checked in imageJ
cell_size = 30 # um
cell_size_px = int(np.ceil(cell_size/pixel_size))

def read_nd2_confocal(path):
    return np.max(nd2.imread(path), axis=0).astype(np.uint16)

def shuffle_labels_notcontinuous(labels):
    random_label_dict = np.unique(labels)
    random_label_dict = random_label_dict[random_label_dict!=0]
    random_label_dict = dict(zip(random_label_dict, np.random.permutation(np.arange(1,len(random_label_dict)+1))))
    random_labels = np.zeros_like(labels)
    for i in random_label_dict:
        random_labels[labels==i] = random_label_dict[i]
    return random_labels

def mask_to_contour_ImageJ_ROI(labels):
    "use https://github.com/Image-Py/cellpose-turbo/blob/master/imagej_roi_converter.py to import into ROI manager"
    labels_list = np.unique(labels)
    labels_list = labels_list[labels_list!=0]
    cnts_list = []
    for i in labels_list:
        cnts,_ = cv.findContours((labels==i).astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnts_list.append(cnts)
    xy_list = []
    for i in range(len(cnts_list)):
        xy_list_current = []
        if len(cnts_list[i][0])<3:
            continue
        for j_point in range(len(cnts_list[i][0])):
            xy_list_current.append(cnts_list[i][0][j_point][0][0])
            xy_list_current.append(cnts_list[i][0][j_point][0][1])
        xy_list.append(xy_list_current)
    ## convert into text
    xy_text = ""
    for i in range(len(xy_list)):
        xy_text = xy_text+",".join(str(i) for i in xy_list[i])+"\n"
    return xy_text

def normalize(img, pmin=1, pmax=99.9):
    min_ = np.percentile(img, pmin)
    max_ = np.percentile(img, pmax)
    return (np.clip((img - min_)/(max_ - min_), 0, 1)*255).astype(np.uint8)

def smooth(img, size):
    return ndimage.median_filter(img, size=int(size))

img = read_nd2_confocal(file_name)

img_cyto = smooth(normalize(img[1]), size=int(np.ceil(1/pixel_size)))
img_nuc = smooth(normalize(img[0]), size=int(np.ceil(1/pixel_size)))
im = np.stack((img_cyto,img_cyto,img_cyto,img_nuc), axis=-1)


from cellpose import models
# model_type='cyto' or 'nuclei' or 'cyto2'
model = models.Cellpose(model_type='cyto')

# define CHANNELS to run segementation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
channels = [[2,3]]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

masks, flows, styles, diams = model.eval(im, diameter=cell_size_px, channels=channels)

# output the segmentation result

label_img_shuffle = shuffle_labels_notcontinuous(masks) # cell

io.imsave(output_pre+'-cell-label.tif',label_img_shuffle.astype('uint16'))
io.imsave(output_pre+'-cell-img.tif',img.astype('uint16'))

cell_outline = mask_to_contour_ImageJ_ROI(label_img_shuffle)
with open(output_pre+'-cell-label-outlines_ImageJ.txt', 'w') as f:
    f.write(cell_outline)
