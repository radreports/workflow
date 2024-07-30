import nibabel as nib
import numpy as np

# Define labels for han1 and han2
def process(input):
    labels_han1 = {
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

    labels_han2 = {
        0: "background",
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

    # Load NIfTI files
    han1_img = nib.load(input +'/han1.nii.gz')
    han2_img = nib.load(input +'/han2.nii.gz')

    han1_data = han1_img.get_fdata()
    han2_data = han2_img.get_fdata()

    # Define offset for the second set of labels to avoid overlap
    label_offset = max(labels_han1.keys()) + 1

    # Update han2 labels to avoid overlap
    han2_data_offset = han2_data.copy()
    for key in labels_han2:
        if key != 0:  # Assuming 0 is background and remains the same
            han2_data_offset[han2_data == key] = key + label_offset

    # Merge the two NIfTI files
    merged_data = np.maximum(han1_data, han2_data_offset)

    # Create a new NIfTI image
    merged_img = nib.Nifti1Image(merged_data, han1_img.affine, han1_img.header)

    # Save the merged image
    nib.save(merged_img, input +"/prediction.nii.gz")

    # Combine the labels
    merged_labels = labels_han1.copy()
    for key, value in labels_han2.items():
        if key != 0:  # Assuming 0 is background and remains the same
            merged_labels[key + label_offset] = value

    # Print merged labels
    print("Merged Labels:", merged_labels)
