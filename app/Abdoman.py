from rt_utils import RTStructBuilder

# import nrrd
import nibabel as nib
import numpy as np
import SimpleITK as sitk
# import SimpleITK as sitk
def process(dicom_in,nifti_in,rt_out):
    print("Processing ...",nifti_in)
    print("dicom dir",dicom_in )
    input_nifti_path = nifti_in
    # dicom_series_path="dicom/"
    dicom_series_path=dicom_in +"/"
    nii = nib.load(input_nifti_path)
    pred_nrrd_abdoman = nii.get_fdata()
    print(pred_nrrd_abdoman.shape)
    un = np.unique(np.copy(pred_nrrd_abdoman))
    print(un)

    rtstruct = RTStructBuilder.create_new(dicom_series_path=dicom_series_path)
    organ0 = np.copy(pred_nrrd_abdoman)
    organ1 = np.copy(pred_nrrd_abdoman)
    organ2 = np.copy(pred_nrrd_abdoman)
    organ3 = np.copy(pred_nrrd_abdoman)
    organ4 = np.copy(pred_nrrd_abdoman)
    organ5 = np.copy(pred_nrrd_abdoman)
    organ6 = np.copy(pred_nrrd_abdoman)
    organ7 = np.copy(pred_nrrd_abdoman)
    organ8 = np.copy(pred_nrrd_abdoman)
    organ9 = np.copy(pred_nrrd_abdoman)
    organ10 = np.copy(pred_nrrd_abdoman)
    organ11 = np.copy(pred_nrrd_abdoman)
    organ12 = np.copy(pred_nrrd_abdoman)
    organ13 = np.copy(pred_nrrd_abdoman)
    try:
        organ0[pred_nrrd_abdoman != 1] = 0
        organ0[organ0 != 0] = 1
        organ0 = np.array(organ0, dtype=bool)
        organ0 = np.rot90(organ0)
        rtstruct.add_roi(mask=organ0,name="spleen")
    except Exception as e:
        print("")
    
    try:
        organ1[pred_nrrd_abdoman != 2] = 0
        organ1[organ1 != 0] = 1
        organ1 = np.array(organ1, dtype=bool)
        organ1 = np.rot90(organ1)
        rtstruct.add_roi(mask=organ1,name="right kidney")
    except Exception as e:
        print("")

    try:
        organ2[pred_nrrd_abdoman != 3] = 0
        organ2[organ2 != 0] = 1
        organ2 = np.array(organ2, dtype=bool)
        organ2 = np.rot90(organ2)
        # organ2 = np.flipud(organ2)
        rtstruct.add_roi(mask=organ2,name=" left kidney")
    except Exception as e:
        print("")
    
    try:
        organ3[pred_nrrd_abdoman != 4] = 0
        organ3[organ3 != 0] = 1
        organ3 = np.array(organ3, dtype=bool)
        organ3 = np.rot90(organ3)
        # organ3 = np.flipud(organ3)
        rtstruct.add_roi(mask=organ3,name="gallbladder")
    except Exception as e:
        print("")

    try:    
        organ4[pred_nrrd_abdoman != 5] = 0
        organ4[organ4 != 0] = 1
        organ4 = np.array(organ4, dtype=bool)
        organ4 = np.rot90(organ4)
        # organ4 = np.flipud(organ4)
        rtstruct.add_roi(mask=organ4,name="esophagus")
    except Exception as e:
        print("")

    try:
        organ5[pred_nrrd_abdoman != 6] = 0
        organ5[organ5 != 0] = 1
        organ5 = np.array(organ5, dtype=bool)
        organ5 = np.rot90(organ5)
        # organ5 = np.flipud(organ5)
        rtstruct.add_roi(mask=organ5,name="liver")
    except Exception as e:
        print("")
    
    try:
        organ6[pred_nrrd_abdoman != 7] = 0
        organ6[organ6 != 0] = 1
        organ6 = np.array(organ6, dtype=bool)
        organ6 = np.rot90(organ6)
        # organ6 = np.flipud(organ6)
        rtstruct.add_roi(mask=organ6,name="stomach")
    except Exception as e:
        print("")

    try:    
        organ7[pred_nrrd_abdoman != 8] = 0
        organ6[organ7 != 0] = 1
        organ7 = np.array(organ7, dtype=bool)
        organ7 = np.rot90(organ7)
        # organ7 = np.flipud(organ7)
        rtstruct.add_roi(mask=organ7,name="aorta")
    except Exception as e:
        print("")

    try:
        organ8[pred_nrrd_abdoman != 9] = 0
        organ8[organ8 != 0] = 1
        organ8 = np.array(organ8, dtype=bool)
        organ8 = np.rot90(organ8)
        # organ8 = np.flipud(organ8)
        rtstruct.add_roi(mask=organ8,name="inferior vena cava")
    except Exception as e:
        print("")
    
    try:
        organ9[pred_nrrd_abdoman != 10] = 0
        organ9[organ9 != 0] = 1
        organ9 = np.array(organ9, dtype=bool)
        organ9 = np.rot90(organ9)
        # organ9 = np.flipud(organ9)
        rtstruct.add_roi(mask=organ9,name="portal vein and splenic vein")
    except Exception as e:
        print("")
    
    try:
        organ10[pred_nrrd_abdoman != 11] = 0
        organ10[organ10 != 0] = 1
        organ10 = np.array(organ10, dtype=bool)
        organ10 = np.rot90(organ10)
        # organ10 = np.flipud(organ10)
        rtstruct.add_roi(mask=organ10,name="pancreas")
    except Exception as e:
        print("")
    
    try:
        organ11[pred_nrrd_abdoman != 12] = 0
        organ11[organ11 != 0] = 1
        organ11 = np.array(organ11, dtype=bool)
        organ11 = np.rot90(organ11)
        # organ11 = np.flipud(organ11)
        rtstruct.add_roi(mask=organ11,name="right adrenal gland")
    except Exception as e:
        print("")
    
    try:
        organ12[pred_nrrd_abdoman != 13] = 0
        organ12[organ12 != 0] = 1
        organ12 = np.array(organ12, dtype=bool)
        organ12 = np.rot90(organ12)
        # organ12 = np.flipud(organ12)
        rtstruct.add_roi(mask=organ12,name="left adrenal gland")
    except Exception as e:
        print("")
        
    rtstruct.save(rt_out+'/rt-struct')
    print(rtstruct.get_roi_names())
