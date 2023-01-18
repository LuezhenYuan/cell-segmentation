import sys
import numpy as np
from skimage import io
import numpy as np
import nd2

pixel_size = 0.1817195 # um/px
z_step_size = 1.5 # um/px

   
file_name = sys.argv[1] # "../data/Confocal/LC561_1_Confocal_Hoechst_20221119_A4.nd2"
output_pre = file_name.rsplit('.', 1)[0]

## read image
if file_name.rsplit('.', 1)[1]=="nd2":
    img_0 = nd2.imread(file_name).astype(np.uint16)

if len(img_0.shape) == 4:
    img_0 = img_0[:,0,:,:] # select nucleus channel
elif len(img_0.shape) == 3:
    ...
else:
    print("Is this a z stack image?")
    exit()

## reshape the image to make the pixel size into 0.5 um/px and z step size 0.5 um/px
from skimage.transform import rescale, resize
img_0_resize = rescale(img_0, (z_step_size/0.5,pixel_size/0.5,pixel_size/0.5), anti_aliasing=False,preserve_range=True)


## stardist segmentation for 3D image
from stardist.models import StarDist3D
from csbdeep.utils import normalize # https://github.com/CSBDeep/CSBDeep/blob/master/csbdeep/utils/utils.py

model = StarDist3D.from_pretrained('3D_demo')

#model = StarDist2D.from_pretrained('2D_versatile_fluo')
labels, details = model.predict_instances(normalize(img_0_resize),axes='ZYX')

## reshape the image back
labels_resize = resize(labels,img_0.shape,order=0,anti_aliasing=False,preserve_range=True)

## save the result
io.imsave(output_pre+'-nucleus-label-stardist.tif',labels_resize.astype('uint16'))
