from rt_utils import RTStructBuilder

# import nrrd
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def process():
    input_nifti_path = "liver_in/outfile.nii.gz"
    dicom_series_path="dicom/"
    rt_struct_path ="output/thor-rt-struct.dcm"
    nii = nib.load(input_nifti_path)
    pred_nrrd_liver = nii.get_fdata() 
    print( "processing Kidneys ....")
    # rtstruct = RTStructBuilder.create_from(dicom_series_path,rt_struct_path)
    rtstruct = RTStructBuilder.create_new(dicom_series_path)
    liver = np.copy(pred_nrrd_liver)
    tumor = np.copy(pred_nrrd_liver)
    
    un = np.unique(liver)
    print(un)
    
    # un = np.unique(np.copy(pred_nrrd_liver))
    # print(un)

    liver[pred_nrrd_liver != 1] = 0
    liver[liver != 0] = 1
    
    tumor[pred_nrrd_liver != 2] = 0
    tumor[tumor != 0] = 1

    
    # pred_nrrd_heart[pred_nrrd_heart != 0] = 1
    liver = np.array(liver, dtype=bool)

    liver = np.rot90(liver)
    liver = np.flipud(liver)
    # heart = np.rot90(heart)
    tumor = np.array(tumor, dtype=bool)

    tumor = np.rot90(tumor)
    tumor = np.flipud(tumor)


    
    

    rtstruct.add_roi(mask=liver,name="Kidney ")
    countzero_in2 = np.count_nonzero(tumor)
    if countzero_in2 > 0 :
        rtstruct.add_roi(mask=tumor,name="Kidney tumor ")
    rtstruct.save('output/tumor-rt-struct')