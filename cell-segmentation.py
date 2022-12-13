import nd2
import sys
import numpy as np
import cv2 as cv
from skimage import io
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

segmentation_predictions = app.predict(im, image_mpp=pixel_size)

# output the segmentation result

label_img_shuffle = shuffle_labels_notcontinuous(segmentation_predictions[0,:,:,0])
io.imsave(output_pre+'-cell-label.tif',label_img_shuffle.astype('uint16'))
io.imsave(output_pre+'-cell-img.tif',img.astype('uint16'))
## save the outline (can be opened in ImageJ with https://github.com/Image-Py/cellpose-turbo/blob/master/imagej_roi_converter.py)

result_nd_outline = mask_to_contour_ImageJ_ROI(label_img_shuffle)
with open(output_pre+'-nucleus-label-outlines_ImageJ.txt', 'w') as f:
    f.write(result_nd_outline)
    