import nibabel as nib
import numpy as np

nii = nib.load("temp/tmpqxies1z2/tmpidgwtyxr/prediction.nii.gz")
pred_nrrd_liver = nii.get_fdata()

liver = np.copy(pred_nrrd_liver)
    
un = np.unique(liver)
print(un)


