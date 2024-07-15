import SimpleITK as sitk
from radiomics import featureextractor
import nibabel as nib
import numpy as np
import json
from fhir.resources.observation import Observation
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.diagnosticreport import DiagnosticReport
from rt_utils import RTStructBuilder
from tqdm import tqdm
import requests
import os

liver_classes = {
    1: "Liver",
    2: "Liver tumor"
}

# Define the dictionary for feature units and descriptions
feature_units_and_descriptions = {
    'SurfaceArea': {'unit': 'mm²', 'description': 'Surface area of the tumor mesh'},
    'Energy': {'unit': None, 'description': 'Sum of squared voxel intensities'},
    'Mean': {'unit': None, 'description': 'Average of the voxel intensity values'}
}

params = {
    'imageType': {'Original': {}},
    'setting': {
        'binWidth': 25,
        'resampledPixelSpacing': None,
        'force2D': False
    },
    'featureClass': {
        'shape': ['SurfaceArea'],
        'firstorder': ['Energy', 'Mean']
    }
}

extractor = featureextractor.RadiomicsFeatureExtractor(params)

def extract_features(image_path, mask_path):
    result = extractor.execute(image_path, mask_path)
    features = {name: value for name, value in result.items() if name.split('_')[-1] in feature_units_and_descriptions}
    return features

def create_observation(name, value, patient_id):
    feature_info = feature_units_and_descriptions.get(name.split('_')[-1], {'unit': None, 'description': 'No description provided'})
    observation = Observation(
        resourceType="Observation",
        status='final',
        code=CodeableConcept(coding=[Coding(system='http://example.org/fake-metrics', code=name, display=feature_info['description'])]),
        subject=Reference(reference=f'{patient_id}'),
        valueQuantity={'value': value, 'unit': feature_info['unit']}
    )
    return observation

def load_nifti_as_sitk(path):
    print("Loading NIfTI file using nibabel::load_nifti_as_sitk", path)
    nii = nib.load(path)
    data = nii.get_fdata()
    sitk_image = sitk.GetImageFromArray(np.asanyarray(data))
    spacing = [float(x) for x in nii.header.get_zooms()[:3]]  # Ensure spacing is a list of floats
    origin = [float(x) for x in nii.affine[:3, 3]]  # Ensure origin is a list of floats
    sitk_image.SetSpacing(spacing)
    sitk_image.SetOrigin(origin)
    return sitk_image

def filter_tumors_within_liver(segmented_nifti):
    data = segmented_nifti.get_fdata()
    liver_mask = data == 1
    tumor_mask = data == 2
    
    valid_tumor_mask = tumor_mask & liver_mask
    
    if np.sum(valid_tumor_mask) > 0:
        print("Tumor segments found within liver volume.")
    else:
        print("No tumor segments found within liver volume.")
    
    filtered_data = data.copy()
    filtered_data[~liver_mask & ~valid_tumor_mask] = 0
    
    print("Filtered predicted NIfTI unique values:", np.unique(filtered_data))
    
    return nib.Nifti1Image(filtered_data, segmented_nifti.affine)

def process_rt_structure(dicom_in, nifti_in, rt_out, pacs_url):
    dicom_series_path = dicom_in + "/"
    img_data = nifti_in.get_fdata()
    rtstruct = RTStructBuilder.create_new(dicom_series_path=dicom_series_path)

    for class_idx, class_name in tqdm(liver_classes.items()):
        binary_img = img_data == class_idx
        if binary_img.sum() > 0:
            rtstruct.add_roi(
                mask=binary_img,
                name=class_name
            )
    if os.path.isfile(rt_out + '/rt-struct.dcm'):
        fileobj = open(rt_out + '/rt-struct.dcm', 'rb')
        headers = {"Content-Type": "application/binary"}
        getdata = requests.post(pacs_url + "/instances", data=fileobj, headers=headers)
        print(getdata.text)

    rtstruct.save(rt_out + '/rt-struct')

def post_to_ehr(resource, ehr_url, headers):
    resource_json = resource.json(indent=2)
    response = requests.post(f'{ehr_url}/{resource.resource_type}', headers=headers, data=resource_json)
    response.raise_for_status()
    return response.json()['id']

def main(dicom_path, nifti_path_original, nifti_path_predicted, rt_out, pacs_url, ehr_url, study_id, patient_id):
    headers = {'Content-Type': 'application/fhir+json'}
    nifti_original = load_nifti_as_sitk(nifti_path_original)
    nifti_predicted = load_nifti_as_sitk(nifti_path_predicted)

    print("Original NIfTI file unique values:", np.unique(nib.load(nifti_path_predicted).get_fdata()))

    nifti_predicted_filtered = filter_tumors_within_liver(nib.load(nifti_path_predicted))
    print("Filtering tumors within liver done")
    
    process_rt_structure(dicom_path, nifti_predicted_filtered, rt_out, pacs_url)
    print("RT structure processing done")

    features_liver = extract_features(nifti_path_original, nifti_path_predicted)
    features_tumor = extract_features(nifti_path_original, nifti_path_predicted)

    observations = []
    for name, value in features_liver.items():
        observations.append(create_observation(name, value, patient_id))
    for name, value in features_tumor.items():
        observations.append(create_observation(name, value, patient_id))

    observation_ids = [post_to_ehr(obs, ehr_url, headers) for obs in observations]

    diagnostic_report = DiagnosticReport(
        status='final',
        code=CodeableConcept(
            coding=[Coding(
                system='http://loinc.org',
                code=study_id,
                display='Liver and Tumor Report'
            )]
        ),
        subject=Reference(reference=f'{patient_id}'),
        result=[Reference(reference=f'Observation/{obs_id}') for obs_id in observation_ids]
    )

    diagnostic_report_id = post_to_ehr(diagnostic_report, ehr_url, headers)
    print(f'Diagnostic Report ID: {diagnostic_report_id}')

# Example usage
# nifti_path_original = 'path/to/original/file.nii.gz'
# nifti_path_predicted = 'path/to/predicted/file.nii.gz'
# dicom_path = 'path/to/dicom/folder'
# rt_out = 'path/to/rt/output'
# pacs_url = 'http://pacs.url'
# ehr_url = 'http://ehr.url'
# study_id = 'study-id'
# patient_id = 'patient-id'
# main(nifti_path_original, nifti_path_predicted, dicom_path, rt_out, pacs_url, ehr_url, study_id, patient_id)
