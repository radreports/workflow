import nibabel as nib
import numpy as np

input_nifti_path = "temp/tmpm6sqr1b9/tmpd0ive1vr/prediction.nii.gz"

nii = nib.load(input_nifti_path)
pred_nrrd_abdoman = nii.get_fdata()
un = np.unique(np.copy(pred_nrrd_abdoman))
data_type = un.dtype
print("unique values of ich:",un)
print("data type  of ich:",data_type)

input_nifti_path = "temp/tmpkj5jhnuw/tmp0xrfbxey/prediction.nii.gz"

nii = nib.load(input_nifti_path)
pred_nrrd_abdoman = nii.get_fdata()
un = np.unique(np.copy(pred_nrrd_abdoman))
data_type = un.dtype
print("unique values of nnunet  ich:",un)
print("data type  of nnunet ich:",data_type)