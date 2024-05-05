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
from docx import Document

pparams = {
    'imageType': {'Original': {}},
    'setting': {
        'binWidth': 25,
        'resampledPixelSpacing': None,
        'force2D': False
    },
    'featureClass': {
        'shape': None,  # Extract all shape features
        'firstorder': None,  # Extract all first-order features
        'glcm': None,  # Extract all GLCM features
        'glrlm': None,  # Extract all GLRLM features
        'glszm': None  # Extract all GLSZM features
    }
}
extractor = featureextractor.RadiomicsFeatureExtractor(pparams)





# Set up parameters for radiomic feature extraction

def extract_features(image_path, mask_path):
    image = sitk.ReadImage(image_path)
    mask = sitk.ReadImage(mask_path)
    features = extractor.execute(image, mask)
    return features

def create_observation(feature_name, feature_value, patient_id, imaging_study_id):
    observation = Observation(
        status='final',
        code=CodeableConcept(
            coding=[Coding(
                system='http://terminology.hl7.org/CodeSystem/observation-category',
                code=feature_name,
                display='Radiomic Feature'
            )]
        ),
        subject=Reference(
            reference=f'Patient/{patient_id}'
        ),
        encounter=Reference(
            reference=f'ImagingStudy/{imaging_study_id}'
        ),
        valueQuantity=Quantity(
            value=float(feature_value),  # Make sure the value is converted to float
            unit='Unit',
            system='http://unitsofmeasure.org',
            code='1'
        )
    )
    return observation

def generate_report_doc(features):
    doc = Document()
    doc.add_heading('Lung Nodule Analysis Report', 0)
    for key, value in features.items():
        doc.add_paragraph(f'{key}: {value}')
    return doc

# Example usage:
def post_fhir_resource(resource):
    """Post a FHIR resource to the server and return the resource ID."""
    headers = {'Content-Type': 'application/fhir+json'}
    response = requests.post(f'{FHIR_SERVER_URL}/{resource.resource_type}', headers=headers, json=resource.dict())
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()['id']
# FHIR server base URL
def process(FHIR_SERVER_URL,patient_id,imaging_study_id,image_path,mask_path):

    FHIR_SERVER_URL = FHIR_SERVER_URL

    # patient_id = '123'
    # imaging_study_id = '456'
    # image_path = 'path_to_dicom_image.dcm'
    # mask_path = 'path_to_nodule_mask.nii'

    features = extract_features(image_path, mask_path)
    observations = [create_observation(name, value, patient_id, imaging_study_id) for name, value in features.items()]
    observation_ids = [post_fhir_resource(obs) for obs in observations]

    report_doc = generate_report_doc(features)
    report_doc_path = 'Lung_Nodule_Report.docx'
    report_doc.save(report_doc_path)

    # Post the report document as a binary resource
    with open(report_doc_path, 'rb') as f:
        binary = Binary(contentType='application/msword', data=f.read().encode('base64'))
        binary_id = post_fhir_resource(binary)

    # Create and post diagnostic report
    diagnostic_report = DiagnosticReport(
        status='final',
        code=CodeableConcept(
            coding=[Coding(
                system='http://loinc.org',
                code='18748-4',
                display='Radiology Report'
            )]
        ),
        subject=Reference(
            reference=f'Patient/{patient_id}'
        ),
        context=Reference(
            reference=f'ImagingStudy/{imaging_study_id}'
        ),
        result=[Reference(reference=f'Observation/{obs_id}') for obs_id in observation_ids],
        presentedForm=[Reference(reference=f'Binary/{binary_id}')]
    )
    diagnostic_report_id = post_fhir_resource(diagnostic_report)

    print(f'Diagnostic Report ID: {diagnostic_report_id}')
