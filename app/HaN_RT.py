
from rt_utils import RTStructBuilder
import nibabel as nib
import numpy as np
import SimpleITK as sitk
from tqdm import tqdm
import os
# classes = {
#     1: "eye_left",
#     2: "eye_right",
#     3: "eye_lens_left",
#     4: "eye_lens_right",
#     5: "optic_nerve_left",
#     6: "optic_nerve_right",
#     7: "parotid_gland_left",
#     8: "parotid_gland_right",
#     9: "submandibular_gland_right",
#     10: "submandibular_gland_left",
#     11: "nasopharynx",
#     12: "oropharynx",
#     13: "hypopharynx",
#     14: "nasal_cavity_right",
#     15: "nasal_cavity_left",
#     16: "auditory_canal_right",
#     17: "auditory_canal_left",
#     18: "soft_palate",
#     19: "hard_palate",
#     20: "larynx_air",
#     21: "thyroid_cartilage",
#     22: "hyoid",
#     23: "cricoid_cartilage",
#     24: "zygomatic_arch_right",
#     25: "zygomatic_arch_left",
#     26: "styloid_process_right",
#     27: "styloid_process_left",
#     28: "internal_carotid_artery_right",
#     29: "internal_carotid_artery_left",
#     30: "internal_jugular_vein_right",
#     31: "internal_jugular_vein_left"
# }


classes1 = {
    1: "eye_left",
    2: "eye_right",
    3: "eye_lens_left",
    4: "eye_lens_right",
    5: "optic_nerve_left",
    6: "optic_nerve_right",
    7: "parotid_gland_left",
    8: "parotid_gland_right",
    9: "submandibular_gland_right",
    10: "submandibular_gland_left",
    11: "nasopharynx",
    12: "oropharynx",
    13: "hypopharynx",
    14: "nasal_cavity_right",
    15: "nasal_cavity_left",
    16: "auditory_canal_right",
    17: "auditory_canal_left",
    18: "soft_palate",
    19: "hard_palate"
}

classes2 = {
    
    1: "larynx_air",
    2: "thyroid_cartilage",
    3: "hyoid",
    4: "cricoid_cartilage",
    5: "zygomatic_arch_right",
    6: "zygomatic_arch_left",
    7: "styloid_process_right",
    8: "styloid_process_left",
    9: "internal_carotid_artery_right",
    10: "internal_carotid_artery_left",
    11: "internal_jugular_vein_right",
    12: "internal_jugular_vein_left"
}
def process(dicom_in,nifti_in,rt_out):
    """
    dcm_reference_file: a directory with dcm slices ??
    """
    classes = classes1
    if os.path.isfile(rt_out ):
        classes = classes2
        rtstruct = RTStructBuilder.create_from(
        dicom_series_path=dicom_in+"/", 
        rt_struct_path=rt_out
)
    else:
        classes = classes1
        rtstruct = RTStructBuilder.create_new(dicom_series_path=dicom_in+"/")

    
    input_nifti_path = nifti_in
    # dicom_series_path="dicom/"
    dicom_series_path=dicom_in +"/"
    # rt_struct_path ="output/tumor-rt-struct.dcm"
    nii = nib.load(input_nifti_path)
    img_data = nii.get_fdata() 
    # create new RT Struct - requires original DICOM
    # rtstruct = RTStructBuilder.create_new(dicom_series_path=dicom_series_path)

    # add mask to RT Struct
    for class_idx, class_name in tqdm(classes.items()):
        print(f"Processing class {class_name} with index {class_idx}")
        binary_img = img_data == class_idx
        if binary_img.sum() > 0:  # only save none-empty images

            # rotate nii to match DICOM orientation
            binary_img = np.rot90(binary_img, 1, (0, 1))  # rotate segmentation in-plane

            # add segmentation to RT Struct
            rtstruct.add_roi(
                mask=binary_img,  # has to be a binary numpy array
                name=class_name
            )

    rtstruct.save(rt_out)
    return "Head and Neck Contours "
