import nibabel as nib
import numpy as np

input_nifti_path = "temp/dataset/case_0001.nii"

nii = nib.load(input_nifti_path)
pred_nrrd_abdoman = nii.get_fdata()
un = np.unique(np.copy(pred_nrrd_abdoman))
print(un)