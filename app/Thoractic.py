from rt_utils import RTStructBuilder

# import nrrd
import nibabel as nib
import numpy as np
import SimpleITK as sitk
import os
def process(dicom_in,nifti_in,rt_out):
    print("Processing ...",nifti_in)
    print("dicom dir",dicom_in )
    input_nifti_path = nifti_in
    # dicom_series_path="dicom/"
    dicom_series_path=dicom_in +"/"
    # rt_struct_path ="output/tumor-rt-struct.dcm"
    nii = nib.load(input_nifti_path)
    pred_nrrd_segthor = nii.get_fdata() 
    print( np.shape(pred_nrrd_segthor)[2])
    # rtstruct = RTStructBuilder.create_from(dicom_series_path,rt_struct_path)
    # rtstruct = RTStructBuilder.create_new(dicom_series_path)
    pred_nrrd_esophagus = np.copy(pred_nrrd_segthor)
    pred_nrrd_heart = np.copy(pred_nrrd_segthor)
    pred_nrrd_trachea = np.copy(pred_nrrd_segthor)
    pred_nrrd_aorta = np.copy(pred_nrrd_segthor)

    pred_nrrd_esophagus[pred_nrrd_segthor != 1] = 0
    pred_nrrd_esophagus[pred_nrrd_esophagus != 0] = 1
    
    # zero every segmask other than the heart and make the mask binary (0/1)
    pred_nrrd_heart[pred_nrrd_segthor != 2] = 0
    pred_nrrd_heart[pred_nrrd_heart != 0] = 1
    
    # zero every segmask other than the trachea and make the mask binary (0/1)
    pred_nrrd_trachea[pred_nrrd_segthor != 3] = 0
    pred_nrrd_trachea[pred_nrrd_trachea != 0] = 1
    
    # zero every segmask other than the aorta and make the mask binary (0/1)
    pred_nrrd_aorta[pred_nrrd_segthor != 4] = 0
    pred_nrrd_aorta[pred_nrrd_aorta != 0] = 1

    # pred_nrrd_heart[pred_nrrd_heart != 0] = 1
    heart = np.array(pred_nrrd_heart, dtype=bool)
    aorta = np.array(pred_nrrd_aorta, dtype=bool)
    trachea = np.array(pred_nrrd_trachea, dtype=bool)
    esophagus = np.array(pred_nrrd_esophagus, dtype=bool)

    # tmp = pred_nrrd_heart
    # print(tmp.shape)
    # heart = np.flipud(heart)
    heart = np.rot90(heart, 1, (0, 1)) 
    # heart = np.rot90(heart)
    # heart = np.flipud(heart)
    # heart = np.rot90(heart)

    aorta = np.rot90(aorta, 1, (0, 1)) 
    # aorta = np.rot90(aorta)
    # aorta = np.flipud(aorta)

    trachea = np.rot90(trachea, 1, (0, 1)) 
    # trachea = np.rot90(trachea)
    # trachea = np.flipud(trachea)

    esophagus = np.rot90(esophagus, 1, (0, 1)) 
    # esophagus = np.rot90(esophagus)
    # esophagus = np.flipud(esophagus)
    # if os.path.isfile(rt_struct_path):
    #     rtstruct = RTStructBuilder.create_from(dicom_series_path,rt_struct_path)
    # else:
    #     rtstruct = RTStructBuilder.create_new(dicom_series_path)
    
    # rtstruct = RTStructBuilder.create_new(dicom_series_path)
    rtstruct = RTStructBuilder.create_new(dicom_series_path)
    countzero_in2 = np.count_nonzero(heart)
    if countzero_in2 > 0:
        rtstruct.add_roi(mask=heart,name="Heart")
    
    countzero_in2 = np.count_nonzero(aorta)
    if countzero_in2 > 0:
        rtstruct.add_roi(mask=aorta,name="Aorta")

    countzero_in2 = np.count_nonzero(trachea)
    if countzero_in2 > 0:
        rtstruct.add_roi(mask=trachea,name="Trachea")

    countzero_in2 = np.count_nonzero(esophagus)
    if countzero_in2 > 0:
        rtstruct.add_roi(mask=esophagus,name="Esophagus")

    # in/Lungs/May19/1.3.6.1.4.1.14519.5.2.1.7014.4598.106943890850011666503487579262

    rtstruct.save(rt_out+'/rt-struct')
