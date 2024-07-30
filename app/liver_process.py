import nibabel as nib
import numpy as np
import os

def load_nifti(file_path):
    """Load a NIfTI file and return the data and affine."""
    img = nib.load(file_path)
    data = img.get_fdata()
    affine = img.affine
    return data, affine

def save_nifti(data, affine, file_path):
    """Save data to a NIfTI file."""
    img = nib.Nifti1Image(data, affine)
    nib.save(img, file_path)

def process(folder_path):
    """Merge two NIfTI files into a single file with specified pixel values."""
    # Define input file paths
    prediction1_path = os.path.join(folder_path, 'predictions1.nii.gz')
    prediction2_path = os.path.join(folder_path, 'predictions2.nii.gz')

    # Load NIfTI files
    liver_data, liver_affine = load_nifti(prediction1_path)
    vessel_tumor_data, vessel_tumor_affine = load_nifti(prediction2_path)

    # Check if affine transformations match
    if not np.array_equal(liver_affine, vessel_tumor_affine):
        raise ValueError("Affine transformations of the input files do not match.")

    # Initialize the final mask with liver segmentation
    final_mask = np.zeros_like(liver_data, dtype=np.int32)
    final_mask[liver_data == 1] = 1  # Liver

    # Add hepatic vessel and liver tumor segmentations
    final_mask[vessel_tumor_data == 1] = 2  # Hepatic vessel
    final_mask[vessel_tumor_data == 2] = 3  # Liver tumor

    # Define output file path
    output_path = os.path.join(folder_path, 'prediction.nii.gz')

    # Save the final mask to a new NIfTI file
    save_nifti(final_mask, liver_affine, output_path)
    print(f"Processed file saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    folder_path = "/path/to/your/folder"
    process(folder_path)
