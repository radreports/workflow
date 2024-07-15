import SimpleITK as sitk
from radiomics import featureextractor

import pydicom
import requests
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.binary import Binary
from fhir.resources.quantity import Quantity

import numpy as np
from decimal import Decimal
import base64
import json
import nibabel as nib

# Define the dictionary for feature units and descriptions
feature_units_and_descriptions = {
    'Elongation': {'unit': None, 'description': 'Ratio of the two largest principal components in the ROI'},
    'Flatness': {'unit': None, 'description': 'Ratio of the largest to smallest principal components in the ROI'},
    'MajorAxisLength': {'unit': 'mm', 'description': 'The largest axis length of the ROI-enclosing ellipsoid'},
    'MinorAxisLength': {'unit': 'mm', 'description': 'The second-largest axis length of the ROI-enclosing ellipsoid'},
    'Maximum3DDiameter': {'unit': 'mm', 'description': 'Largest pairwise Euclidean distance between surface mesh vertices'},
    'Sphericity': {'unit': None, 'description': 'Measure of the roundness of the tumor, relative to a sphere'},
    'SurfaceArea': {'unit': 'mm²', 'description': 'Surface area of the tumor mesh'},
    'Energy': {'unit': None, 'description': 'Sum of squared voxel intensities'},
    'Entropy': {'unit': None, 'description': 'Measure of randomness in voxel intensity distribution'},
    'Kurtosis': {'unit': None, 'description': 'Peakedness of the voxel intensity distribution'},
    'Mean': {'unit': None, 'description': 'Average of the voxel intensity values'},
    'Skewness': {'unit': None, 'description': 'Asymmetry of the voxel intensity distribution'},
    'Contrast': {'unit': None, 'description': 'Measure of the local intensity variation'},
    'Correlation': {'unit': None, 'description': 'Degree of linear dependency of gray levels in the ROI'}
    # Add more features if needed
}

# Ensure this dictionary is defined at a global level or within the same function scope where it's being used

params = {
    'imageType': {'Original': {}},
    'setting': {
        'binWidth': 25,
        'resampledPixelSpacing': None,
        'force2D': False
    },
    'featureClass': {
        'shape': ['Elongation', 'Flatness', 'MajorAxisLength', 'MinorAxisLength', 'Maximum3DDiameter', 'Sphericity', 'SurfaceArea'],
        'firstorder': ['Energy', 'Entropy', 'Kurtosis', 'Mean', 'Skewness'],
        'glcm': ['Contrast', 'Correlation']
    }
}

extractor = featureextractor.RadiomicsFeatureExtractor(params)

def extract_features(image_path, mask_path, label_id):
    label_id = int(label_id)  # Ensure label_id is an integer
    result = extractor.execute(image_path, mask_path, label=label_id)
    # Filter results to include only those features specified and supported in the dictionary
    features = {name: value for name, value in result.items() if name.split('_')[-1] in feature_units_and_descriptions}
    return features

def create_observation(name, value, patient_id, imaging_study_id):
    feature_info = feature_units_and_descriptions.get(name.split('_')[-1], {'unit': None, 'description': 'No description provided'})
    observation = Observation(
        status='final',  # Assuming all observations are considered 'final' when created
        code=CodeableConcept(coding=[Coding(system='http://example.org/fake-metrics', code=name, display=feature_info['description'])]),
        subject=Reference(reference=f'/{patient_id}'),
        valueQuantity=Quantity(value=value, unit=feature_info['unit'])
    )
    return observation

def getImageID(url, study_id):
    print("getImageID ...", url + "/" + study_id)
    resp = requests.get(url + "/" + "ImagingStudy/" + study_id)
    imaging = resp.text
    print(imaging)
    imaging = json.loads(imaging)
    series = imaging['series']
    print("series::", series)
    image_id = series[0]
    print("image_id::", image_id["uid"])
    image_id = image_id["uid"]
    return image_id

def nifti_to_sitk(nifti_file_path):
    # Load NIfTI file using nibabel
    nii = nib.load(nifti_file_path)
    data = nii.get_fdata()

    # Convert numpy array to SimpleITK Image
    sitk_image = sitk.GetImageFromArray(np.asanyarray(data))
    sitk_image.SetSpacing(nii.header.get_zooms()[:3])
    sitk_image.SetOrigin(nii.affine[:3, 3])
    return sitk_image

def convert_to_binary_mask(sitk_mask, positive_label):
    """Convert a mask to a binary format where only the specified `positive_label` is 1, others are 0."""
    # Convert the image to a numpy array
    mask_array = sitk.GetArrayFromImage(sitk_mask)
    # Create binary mask
    binary_mask_array = (mask_array == positive_label).astype(int)
    # Convert back to SimpleITK image
    binary_mask_sitk = sitk.GetImageFromArray(binary_mask_array)
    binary_mask_sitk.CopyInformation(sitk_mask)
    return binary_mask_sitk

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float for JSON serialization
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')  # Convert bytes to base64 string
        return super(DecimalEncoder, self).default(obj)

def load_nifti_as_sitk(path):
    """Load a NIfTI file as a SimpleITK Image."""
    return sitk.ReadImage(path)

def generate_report_doc(features):
    doc = Document()
    doc.add_heading('Lung Nodule Analysis Report', 0)
    for key, value in features.items():
        doc.add_paragraph(f'{key}: {value}')
    return doc

def post_fhir_resource(resource, FHIR_SERVER_URL, headers):
    """Post a FHIR resource to the server and return the resource ID."""
    resource_json = json.dumps(resource.dict(), cls=DecimalEncoder)
    try:
        response = requests.post(f'{FHIR_SERVER_URL}/{resource.resource_type}', headers=headers, data=resource_json)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print("Response Status Code:", response.status_code)
        print("Response JSON:", response.json())

        # Now check if 'id' is in the response and handle if it's not
        response_data = response.json()
        if 'id' in response_data:
            return response_data['id']
        else:
            raise ValueError("No 'id' found in response, check error details above.")
    except requests.exceptions.HTTPError as error:
        print("Failed to post resource:", error.response.status_code)
        print("Response:", error.response.text)  # Log the error response
        raise

def process(FHIR_SERVER_URL, patient_id, imaging_study_id, image_path, mask_path, inference_findings):
    image_id = getImageID(FHIR_SERVER_URL, imaging_study_id)
    mask = load_nifti_as_sitk(mask_path)
    labels = sitk.GetArrayViewFromImage(mask)

    unique_labels = np.unique(labels)
    unique_labels = unique_labels[unique_labels != 0]  # Remove background label

    observations = []
    for label in unique_labels:
        binary_mask = convert_to_binary_mask(mask, label)
        binary_mask_array = sitk.GetArrayFromImage(binary_mask)
        if np.sum(binary_mask_array) <= 1:
            continue  # Ignore nodules with only 1 pixel

        features = extract_features(image_path, mask_path, label)
        observations.extend([create_observation(name, value, patient_id, imaging_study_id) for name, value in features.items()])

    headers = {'Content-Type': 'application/fhir+json'}
    observation_ids = [post_fhir_resource(obs, FHIR_SERVER_URL, headers) for obs in observations]

    diagnostic_report = DiagnosticReport(
        status='final',
        code=CodeableConcept(
            coding=[Coding(
                system='http://loinc.org',
                code=image_id,  # LOINC code for 'Radiology Report'
                display='Radiology Report'
            )]
        ),
        subject=Reference(reference=f'/{patient_id}'),
        conclusion=inference_findings,
        conclusionCode=[CodeableConcept(
            coding=[Coding(
                system='http://snomed.info/sct',  # Example, use SNOMED CT if appropriate
                code=image_id,  # Example, use a specific SNOMED CT code relevant to the findings
                display=inference_findings
            )]
        )],
        result=[Reference(reference=f'Observation/{obs_id}') for obs_id in observation_ids]
    )

    diagnostic_report_id = post_fhir_resource(diagnostic_report, FHIR_SERVER_URL, headers)
    print(f'Diagnostic Report ID: {diagnostic_report_id}')
