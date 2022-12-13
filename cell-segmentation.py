import nd2
import sys
import numpy as np
import cv2 as cv
from skimage import io
from scipy import ndimage
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

file_name = sys.argv[1] # "../M1W3_Col1_DAPI_s29_20X/M1_W_3_DAPI_Col1_s29_40X/M1_W_3_DAPI_Col1_s29_40X_001/4.nd2"
model_path = sys.argv[2] # "models/MultiplexSegmentation"
output_pre = file_name.rsplit('.', 1)[0]

img = read_nd2_confocal(file_name)

pixel_size = 0.4315837 # checked in imageJ

# change the input image into required format
# Input images are required to have 4 dimensions [batch, x, y, channel]

# Combined together and expand to 4D
im = np.stack((img[0], img[1]), axis=-1)
im = np.expand_dims(im,0)

from deepcell.applications import Mesmer
# method one: download pretrained model from internect
#app = Mesmer()
# method two: point to the local model
# local model downloaded from https://deepcell-data.s3-us-west-1.amazonaws.com/saved-models/MultiplexSegmentation-9.tar.gz
import tensorflow as tf
mesmer_model_pretrained = tf.keras.models.load_model(model_path)
app = Mesmer(mesmer_model_pretrained)

segmentation_predictions = app.predict(im, image_mpp=pixel_size, compartment = "both")

# output the segmentation result

label_img_shuffle = shuffle_labels_notcontinuous(segmentation_predictions[0,:,:,1]) # nucleus

label_img_shuffle_0 = shuffle_labels_notcontinuous(segmentation_predictions[0,:,:,0]) # cell

io.imsave(output_pre+'-nucleus-label.tif',label_img_shuffle.astype('uint16'))
io.imsave(output_pre+'-cell-label.tif',label_img_shuffle_0.astype('uint16'))
io.imsave(output_pre+'-cell-img.tif',img.astype('uint16'))

nucleus_outline = mask_to_contour_ImageJ_ROI(label_img_shuffle)
with open(output_pre+'-nucleus-label-outlines_ImageJ.txt', 'w') as f:
    f.write(nucleus_outline)

cell_outline = mask_to_contour_ImageJ_ROI(label_img_shuffle_0)
with open(output_pre+'-cell-label-outlines_ImageJ.txt', 'w') as f:
    f.write(cell_outline)

    
## find the mapping from nucleus id to cell id:
label_img_shuffle_list = np.unique(label_img_shuffle)
label_img_shuffle_list = label_img_shuffle_list[label_img_shuffle_list!=0]
nucleus_cell_label_map = np.zeros((len(label_img_shuffle_list),2),dtype='uint16')
for i in range(len(label_img_shuffle_list)):
    tmp_nucleus = label_img_shuffle == label_img_shuffle_list[i]
    tmp_cell_label_list = np.unique(label_img_shuffle_0[tmp_nucleus])
    tmp_cell_label_list = tmp_cell_label_list[tmp_cell_label_list!=0]
    if len(tmp_cell_label_list) == 0:
        # no mapping
        nucleus_cell_label_map[i,:] = [label_img_shuffle_list[i],0]
    elif len(tmp_cell_label_list) == 1:
        nucleus_cell_label_map[i,:] = [label_img_shuffle_list[i],tmp_cell_label_list[0]]
    else:
        tmp_cell = np.multiply(label_img_shuffle_0,tmp_nucleus)
        tmp_cell_area = ndimage.sum(tmp_nucleus,tmp_cell,tmp_cell_label_list)
        nucleus_cell_label_map[i,:] = [label_img_shuffle_list[i],tmp_cell_label_list[tmp_cell_area.argmax()]]


np.savetxt(output_pre+'-nucleus-cell-label-map.csv', nucleus_cell_label_map, delimiter=",", fmt="%d")

"""
## filter the cell segment (contain the nucleus)
label_img_shuffle_list = np.unique(label_img_shuffle)
label_img_shuffle_list = label_img_shuffle_list[label_img_shuffle_list!=0]
cell_label = np.zeros_like(segmentation_predictions[0,:,:,0])
for i in label_img_shuffle_list:
    tmp_nucleus = label_img_shuffle == i
    tmp_cell_label_list = np.unique(segmentation_predictions[0,:,:,0][tmp_nucleus])
    tmp_cell_label_list = tmp_cell_label_list[tmp_cell_label_list!=0]
    if len(tmp_cell_label_list) == 0:
        # no cell segment for the current nucleus segment
        # use the current nucleus segment as the cell segment
        # may add expansion for this
        cell_label[tmp_nucleus] = i # use the nucleus label
    elif len(tmp_cell_label_list) == 1:
        # one cell segment that contain current nucleus
        cell_label[segmentation_predictions[0,:,:,0]==tmp_cell_label_list[0]] = i
    else:
        # more than one cell segment contain current nucleus
        # merge into one cell segment
        for j in tmp_cell_label_list:
            cell_label[segmentation_predictions[0,:,:,0]==j] = i

io.imsave(output_pre+'-nucleus-label.tif',label_img_shuffle.astype('uint16'))
io.imsave(output_pre+'-cell-label.tif',cell_label.astype('uint16'))
io.imsave(output_pre+'-cell-img.tif',img.astype('uint16'))
## save the outline (can be opened in ImageJ with https://github.com/Image-Py/cellpose-turbo/blob/master/imagej_roi_converter.py)

nucleus_outline = mask_to_contour_ImageJ_ROI(label_img_shuffle)
with open(output_pre+'-nucleus-label-outlines_ImageJ.txt', 'w') as f:
    f.write(nucleus_outline)

cell_outline = mask_to_contour_ImageJ_ROI(cell_label)
with open(output_pre+'-cell-label-outlines_ImageJ.txt', 'w') as f:
    f.write(cell_outline)
"""
