from rt_utils import RTStructBuilder

# import nrrd
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def process(dicom_in,nifti_in,rt_out):
    # input_nifti_path = "liver_in/outfile.nii.gz"



    print("Processing ICH  ...",nifti_in)
    print("dicom dir",dicom_in )
    input_nifti_path = nifti_in
   
    dicom_series_path=dicom_in +"/"
    
    nii = nib.load(input_nifti_path)
    pred_nrrd_ich = nii.get_fdata() 
    print("processing ICH ....")
    brain = np.copy(pred_nrrd_ich)
    
    
    un = np.unique(brain)
    print("ICH predict array::",un)
    countzero_in2 = np.count_nonzero(brain)
    if countzero_in2 == 0:
        
        return "ICH Ngative"
        # 1. Intraparenchymal haemorrhage (IPH);
    # 2. Extra-axial haemorrhage (EAH);
    # 3. Perilesional oedema;
    # 4. Intraventricular haemorrhage (IVH).
    rtstruct = RTStructBuilder.create_new(dicom_series_path)
    try:
        pred_nrrd_iph = np.copy(pred_nrrd_ich)
        pred_nrrd_iph[pred_nrrd_iph != 1] = 0
        pred_nrrd_iph[pred_nrrd_iph != 0] = 1
        iph = np.array(pred_nrrd_iph, dtype=bool)
        iph = np.rot90(iph)
        # iph = np.flipud(iph)
        countzero_in2 = np.count_nonzero(iph)
        if countzero_in2 > 0:
            rtstruct.add_roi(mask=iph,name="Intraparenchymal haemorrhage")
    except Exception as e:
        print("No IPH")

    try:
        pred_nrrd_eah = np.copy(pred_nrrd_ich)
        pred_nrrd_eah[pred_nrrd_eah != 2] = 0
        pred_nrrd_eah[pred_nrrd_eah != 0] = 1
        eah = np.array(pred_nrrd_eah, dtype=bool)
        eah = np.rot90(eah)
        # eah = np.flipud(eah)
        countzero_in2 = np.count_nonzero(eah)
        if countzero_in2 > 0:
            rtstruct.add_roi(mask=eah,name="Extra-axial haemorrhage")

    except Exception as e:
        print("No eah")


    try:
        pred_nrrd_edema = np.copy(pred_nrrd_ich)
        pred_nrrd_edema[pred_nrrd_edema != 3] = 0
        pred_nrrd_edema[pred_nrrd_edema != 0] = 1
        edema = np.array(pred_nrrd_edema, dtype=bool)
        edema = np.rot90(edema)
        # edema = np.flipud(edema)
        countzero_in2 = np.count_nonzero(edema)
        if countzero_in2 > 0:
            rtstruct.add_roi(mask=edema,name="Perilesional Edema")
    except Exception as e:
        print("No edema")


    try:
        pred_nrrd_ivh = np.copy(pred_nrrd_ich)
        pred_nrrd_ivh[pred_nrrd_ivh != 4] = 0
        pred_nrrd_ivh[pred_nrrd_ivh != 0] = 1
        ivh = np.array(pred_nrrd_ivh, dtype=bool)
        ivh = np.rot90(ivh)
        # ivh = np.flipud(ivh)
        countzero_in2 = np.count_nonzero(ivh)
        if countzero_in2 > 0:
            rtstruct.add_roi(mask=ivh,name="Intraventricular haemorrhage")
    except Exception as e:
        print("No IVH")

    rtstruct.save(rt_out+'/rt-struct')
    return "Intracranial Haemmorage"

    
    

