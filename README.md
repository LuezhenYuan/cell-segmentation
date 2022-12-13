# cell-segmentation
cell-segmentation-mesmer

## Cell segmentation with deepcell (mesmer model)

Install the packages

```
conda create --no-default-packages --name mesmer_image_py3 python=3.9
source activate mesmer_image_py3
conda install -n mesmer_image_py3 numpy jupyter opencv scikit-image
conda install -n mesmer_image_py3 nd2
pip install deepcell

```

python cell-segmentation.py ND2_FILE_PATH MODEL_PATH
