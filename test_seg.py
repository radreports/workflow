from pathlib import Path
import nibabel as nib
import highdicom as hd
import numpy as np
from pydicom.sr.codedict import codes
from pydicom.filereader import dcmread

dicom_in = "temp/tmp2kuo7_dk/tmpjqrojclp"
nifti_in = "temp/tmp2kuo7_dk/tmpubxjn163/prediction.nii.gz"
series_dir = Path(dicom_in)
image_files = series_dir.glob('*.dcm')
image_datasets = [dcmread(str(f)) for f in image_files]
nii = nib.load(nifti_in)
pred_nrrd_lung = nii.get_fdata() 
lung = np.copy(pred_nrrd_lung)
print("shape = ::", lung.shape)
print("shape = ::", lung.shape[0])
print("shape = ::", lung.shape[1])
print("shape = ::", lung.shape[2])

# lung = lung[..., ::-1]
lung = np.transpose(lung, (2, 1, 0))
print("shape = ::", lung.shape)
print("shape = ::", lung.shape[0])
print("shape = ::", lung.shape[1])
print("shape = ::", lung.shape[2])
shape=(
        len(image_datasets),
        image_datasets[0].Rows,
        image_datasets[0].Columns
    )
print("dicom shape::",shape)