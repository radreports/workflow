from rt_utils import RTStructBuilder
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def process(dicom_in, nifti_in, rt_out):
    # Load the NIFTI file
    print("Processing ...", nifti_in)
    print("DICOM dir", dicom_in)
    input_nifti_path = nifti_in
    dicom_series_path = dicom_in + "/"
    nii = nib.load(input_nifti_path)
    pred_nrrd_lung = nii.get_fdata()
    
    # Convert NIfTI data to SimpleITK image
    mask = sitk.GetImageFromArray(pred_nrrd_lung.astype(np.uint8))
    
    # Apply connected component filter to label each nodule
    label_map = sitk.ConnectedComponent(mask)
    label_map = sitk.RelabelComponent(label_map)
    sitk.WriteImage(label_map, 'temp/labeled_nodule_mask.nii.gz')
    # Get unique labels from the labeled mask
    label_stats = sitk.LabelStatisticsImageFilter()
    label_stats.Execute(mask, label_map)
    labels = label_stats.GetLabels()
    print("Labels:", labels)  # Output the labels to see the unique labels
    
    # Create a new RTStruct from the DICOM series
    rtstruct = RTStructBuilder.create_new(dicom_series_path)
    
    # Loop through each unique label to create separate ROIs for each nodule
    for label in labels:
        if label == 0:
            continue  # Skip background
        
        # Create a mask for the current nodule
        nodule_mask = sitk.GetArrayFromImage(sitk.BinaryThreshold(label_map, lowerThreshold=label, upperThreshold=label))
        nodule_mask = np.rot90(nodule_mask)
        nodule_mask = np.array(nodule_mask, dtype=bool)  # Ensure the mask is boolean
        
        count_nonzero = np.count_nonzero(nodule_mask)
        if count_nonzero > 0:
            roi_name = f"Lung Nodule {label}"
            rtstruct.add_roi(mask=nodule_mask, name=roi_name)
    
    rtstruct.save(rt_out + '/rt-struct')
    return "RT struct saved with multiple lung nodules"


