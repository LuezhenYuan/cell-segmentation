# Cell and Nucleus Segmentation


## Cell segmentation in Tissue images with deepcell (mesmer model)

Install the packages:

First install anaconda in the system.

```
conda create --no-default-packages --name mesmer_image_py3 python=3.9
source activate mesmer_image_py3
conda install -n mesmer_image_py3 numpy jupyter opencv scikit-image
conda install -n mesmer_image_py3 nd2
pip install deepcell

```

To run the python code for cell segmentation:

`python cell-segmentation-deepcell.py ND2_FILE_PATH MODEL_PATH`

### Quantify intensity and shape features in ImageJ

Macro code to run this analysis is `Macro-cell-nucleus-analysis-cell-nucleus.ijm`

To get the outline of the segmented nucleus/cells using ImageJ ROI manager, check `imageJ_roi_converter.py`, which is downloaded from https://github.com/Image-Py/cellpose-turbo/blob/master/imagej_roi_converter.py

## Cell segmentation in cell culture images with cellpose

Install:

```
conda create --name cellpose python=3.8
conda activate cellpose
python -m pip install cellpose[gui]
conda install -n cellpose numpy jupyter opencv scikit-image nd2 matplotlib
```

To run the python code for cell segmentation:

`python cell-segmentation-cellpose.py ND2_FILE_PATH`

To quantify intensity and shape features in ImageJ: `Macro-cell-nucleus-analysis-onlycells.ijm`

## Nucleus segmentation in 2D or 3D 

Install:

```
conda create --no-default-packages --name stardist_py3 python=3.9
conda activate stardist_py3
conda install -n stardist_py3 numpy scipy scikit-image
conda install -c conda-forge csbdeep
conda install -c conda-forge stardist
conda install -c conda-forge nd2 # read Nikon image
```

To run the python code for 3D nucleus segmentation:

`python nucleus-segmentation-3D-stardist.py ND2_FILE_PATH`
