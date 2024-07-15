import dicom2nifti
import nibabel as nib
import numpy as np
import SimpleITK as sitk


mypath = "//Volumes/AI-Data/TCIA/LiverTumor/vip/3Dircadb1/3Dircadb1.20/LABELLED_DICOM"
mypath2 = "/Volumes/AI-Data/TCIA/LiverTumor/vip/3Dircadb1/3Dircadb1.1/MASKS_DICOM/artery"
dicom2nifti.dicom_series_to_nifti(mypath, mypath + "/infile_0000.nii.gz")
nii = nib.load(mypath + "/infile_0000.nii.gz")
pred_nrrd_abdoman = nii.get_fdata()
print(pred_nrrd_abdoman.shape)
un = np.unique(np.copy(pred_nrrd_abdoman))
print(un)

# nii = nib.load(mypath2 + "/infile_0000.nii.gz")
# pred_nrrd_abdoman = nii.get_fdata()
# print(pred_nrrd_abdoman.shape)
# un = np.unique(np.copy(pred_nrrd_abdoman))
# print(un)


# # Load the artery segmentation file
# artery_segmentation_path = mypath + "/infile_0000.nii.gz"
# artery_img = nib.load(artery_segmentation_path)
# artery_data = artery_img.get_fdata()

# # Load the portal vein segmentation file
# portal_vein_segmentation_path = mypath2 + "/infile_0000.nii.gz"
# portal_vein_img = nib.load(portal_vein_segmentation_path)
# portal_vein_data = portal_vein_img.get_fdata()

# # Ensure the shapes are the same
# assert artery_data.shape == portal_vein_data.shape, "The segmentation files do not have the same shape."

# # Create a combined segmentation
# combined_data = np.zeros_like(artery_data)

# # Assuming 1 for artery and 2 for portal vein in the combined segmentation
# combined_data[artery_data == 255] = 1
# combined_data[portal_vein_data == 255] = 2

# # Save the combined segmentation as a new NIfTI file
# combined_img = nib.Nifti1Image(combined_data, artery_img.affine, artery_img.header)
# combined_segmentation_path = '/Volumes/AI-Data/TCIA/LiverTumor/vip/3Dircadb1/3Dircadb1.1/MASKS_DICOM/combined_segmentation.nii'
# nib.save(combined_img, combined_segmentation_path)

# print(f"Combined segmentation saved to {combined_segmentation_path}")
