from rt_utils import RTStructBuilder

# import nrrd
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def process(dicom_in,nifti_in,rt_out):
    # input_nifti_path = "liver_in/outfile.nii.gz"
    print("Processing ...",nifti_in)
    print("dicom dir",dicom_in )
    input_nifti_path = nifti_in
    # dicom_series_path="dicom/"
    dicom_series_path=dicom_in +"/"
    # rt_struct_path ="output/thor-rt-struct.dcm"
    nii = nib.load(input_nifti_path)
    pred_nrrd_lung = nii.get_fdata() 
    print("processing lung tumor ....")
    # print( np.shape(pred_nrrd_lung)[2])
    # rtstruct = RTStructBuilder.create_from(dicom_series_path,rt_struct_path)
    rtstruct = RTStructBuilder.create_new(dicom_series_path)
    lung = np.copy(pred_nrrd_lung)
    
    un = np.unique(lung)
    print(un)
    

    lung[pred_nrrd_lung != 1] = 0
    lung[lung != 0] = 1
    
    lung = np.array(lung, dtype=bool)

    lung = np.rot90(lung)
    # lung = np.flipud(lung)
    # heart = np.rot90(heart)

    
    countzero_in2 = np.count_nonzero(lung)
    if countzero_in2 > 0:
        rtstruct.add_roi(mask=lung,name="Lung Nodes")
        rtstruct.save(rt_out+'/rt-struct')
        return "Lung Nodules"

    return "Negative"
    # rtstruct.add_roi(mask=tumor,name="Lung tumor ")
    