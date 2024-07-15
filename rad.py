import SimpleITK as sitk
from radiomics import featureextractor
import json
import numpy as np

# Paths to the input image and binary mask
image_path = 'temp/tmpwt2nrkda/tmpxxrufrl2/infile_0000.nii.gz'
mask_path = 'temp/tmpwt2nrkda/tmpuhea2a24/prediction.nii.gz'

# Load the CT image and segmentation mask
image = sitk.ReadImage(image_path)
mask = sitk.ReadImage(mask_path)

# Apply connected component filter to label each nodule
label_map = sitk.ConnectedComponent(mask)
label_map = sitk.RelabelComponent(label_map)

# Optionally save the labeled mask
sitk.WriteImage(label_map, 'temp/labeled_nodule_mask.nii.gz')

# Get unique labels from the labeled mask
label_stats = sitk.LabelStatisticsImageFilter()
label_stats.Execute(image, label_map)
labels = label_stats.GetLabels()
print(labels)  # Output the labels to see the unique labels

# Parameters for PyRadiomics
params = {
    'imageType': {'Original': {}},
    'setting': {
        'binWidth': 25,
        'resampledPixelSpacing': None,
        'force2D': False
    },
    'featureClass': {
        'shape': [
            'Elongation', 'Flatness', 'LeastAxisLength', 'MajorAxisLength', 
            'Maximum2DDiameterColumn', 'Maximum2DDiameterRow', 'Maximum2DDiameterSlice', 
            'MeshVolume', 'MinorAxisLength', 'Sphericity', 'SurfaceArea', 
            'SurfaceVolumeRatio', 'VoxelVolume'
        ],
        'firstorder': [
            'Energy', 'Entropy', 'Kurtosis', 'Maximum', 'MeanAbsoluteDeviation', 
            'Mean', 'Median', 'Minimum', 'Range', 'RootMeanSquared', 
            'Skewness', 'TotalEnergy', 'Uniformity', 'Variance'
        ]
    }
}

# Initialize the feature extractor
extractor = featureextractor.RadiomicsFeatureExtractor(params)

# Function to convert NumPy arrays to lists
def convert_to_serializable(result_dict):
    for key, value in result_dict.items():
        if isinstance(value, np.ndarray):
            result_dict[key] = value.tolist()
    return result_dict

# Dictionary to store all features
all_features = {}

# Loop through each label (nodule) and extract features
for label in labels:
    if label == 0:
        continue  # Skip background
    mask_label = sitk.BinaryThreshold(label_map, lowerThreshold=label, upperThreshold=label)
    result = extractor.execute(image, mask_label)
    print(f'Features for nodule {label}:')
    for key, value in result.items():
        print(f'{key}: {value}')
    # Convert NumPy arrays to lists
    result = convert_to_serializable(result)
    
    # Add calculated diameter and surface volume
    try:
        maximum_2d_diameter = max(
            result['original_shape_Maximum2DDiameterColumn'],
            result['original_shape_Maximum2DDiameterRow'],
            result['original_shape_Maximum2DDiameterSlice']
        )
        result['MaximumDiameter'] = maximum_2d_diameter
    except KeyError as e:
        print(f"Warning: {e} not found in the result dictionary for nodule {label}.")
    
    try:
        surface_volume = result['original_shape_SurfaceVolumeRatio']
        result['SurfaceVolume'] = surface_volume
    except KeyError as e:
        print(f"Warning: {e} not found in the result dictionary for nodule {label}.")
    
    # Add to dictionary
    all_features[f'Nodule_{label}'] = result

# Write features to a JSON file
output_file = 'radiomics_features.json'
with open(output_file, 'w') as json_file:
    json.dump(all_features, json_file, indent=4)

print(f'Radiomics features written to {output_file}')
