import nibabel as nib
import numpy as np
import scipy.ndimage
import json
import os

def load_nifti(file_path):
    """Load a NIfTI file."""
    img = nib.load(file_path)
    data = img.get_fdata()
    affine = img.affine
    return data, affine

def save_nifti(data, affine, file_path):
    """Save data to a NIfTI file."""
    img = nib.Nifti1Image(data.astype(np.int32), affine)  # Ensure data type is int32
    nib.save(img, file_path)

def process_lung_nodules(input_path, output_path):
    """Process lung nodules without checking if they are within lung volumes."""
    data, affine = load_nifti(input_path)

    # Assuming lung masks have value 1 and lung nodules have value 2
    lung_mask = (data == 1)
    nodule_mask = (data == 2)

    # Label connected components in the nodule mask
    labeled_nodules, num_features = scipy.ndimage.label(nodule_mask)
    print("Number of features = ", num_features)

    # Iterate over each nodule and assign a unique label
    final_nodule_mask = np.zeros_like(data, dtype=np.int32)
    nodule_count = 0
    classes = {1: "Lungs"}

    for i in range(1, num_features + 1):
        nodule_component = (labeled_nodules == i)
        nodule_count += 1
        classes[2 + nodule_count - 1] = f"Lung Nodule{nodule_count}"
        final_nodule_mask[nodule_component] = 2 + nodule_count - 1

    # Create the final mask with lung volumes and nodules
    final_mask = np.zeros_like(data, dtype=np.int32)
    final_mask[lung_mask] = 1
    final_mask[final_nodule_mask > 0] = final_nodule_mask[final_nodule_mask > 0]

    # Save the result to a new NIfTI file
    save_nifti(final_mask, affine, input_path)
    print(f"Processed lung nodule mask saved to {input_path}")

    # Save the classes to a JSON file
    json_output_path = os.path.join(os.path.dirname(output_path), 'nodules.json')
    with open(json_output_path, 'w') as json_file:
        json.dump({"classes": classes}, json_file, indent=4)
    print(f"Classes saved to {json_output_path}")

def load_json_with_int_keys(file_path):
    """Load data from a JSON file and convert keys to integers."""
    def convert_keys_to_int(d):
        new_dict = {}
        for k, v in d.items():
            try:
                new_key = int(k)
            except ValueError:
                new_key = k
            new_dict[new_key] = v
        return new_dict

    with open(file_path, 'r') as json_file:
        return json.load(json_file, object_hook=convert_keys_to_int)

