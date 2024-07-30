import requests
import json
import datetime

def getImageID(url, study_id):
    print("getImageID ...", url + "/" + study_id)
    resp = requests.get(url + "/"  + study_id)
    imaging = resp.text
    print(imaging)
    imaging = json.loads(imaging)
    series = imaging['series']
    print("series::", series)
    image_id = series[0]
    print("image_id::", image_id["uid"])
    image_id = image_id["uid"]
    return image_id


def process(ehr_base_url, patient_id, seriesID,OAR):
    # Generate the current date and time for the started field
    image_id = getImageID(ehr_base_url, seriesID)
    started = datetime.datetime.now().isoformat()

    # ImagingStudy resource with series information
    imaging_study = {
        "resourceType": "ImagingStudy",
        "status": "available",
        "modality": [
            {
                "system": "http://dicom.nema.org/resources/ontology/DCM",
                "code": "CT"
            }
        ],
        "subject": {
            "reference": patient_id
        },
        "started": started,
        # "reasonCode":"contour",
        # "bodysite": "contour",   
        "reasonCode": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "123456",
                        "display": "Contouring for OAR"
                    }
                ]
            }
        ],
        "description": OAR,
        "series": [
            {
                "uid": image_id,  # Series ID
                "number": 1,
                "modality": {
                    "system": "http://dicom.nema.org/resources/ontology/DCM",
                    "code": "CT"
                },
                "description": "Series 1",
                "numberOfInstances": 3,
                "instance": [
                    {
                        "uid": "1.2.840.113619.2.55.3.604688.1.1.1482132419.604",  # Instance ID
                        "sopClass": {
                            "system": "http://dicom.nema.org/resources/ontology/DCM",
                            "code": "1.2.840.10008.5.1.4.1.1.2"
                        },
                        "number": 1,
                        "title": "CT image 1"
                    },
                    {
                        "uid": "1.2.840.113619.2.55.3.604688.1.1.1482132419.605",
                        "sopClass": {
                            "system": "http://dicom.nema.org/resources/ontology/DCM",
                            "code": "1.2.840.10008.5.1.4.1.1.2"
                        },
                        "number": 2,
                        "title": "CT image 2"
                    }
                ]
            }
        ]
    }

    # Store the ImagingStudy resource on the FHIR server
    headers = {"Content-Type": "application/fhir+json"}
    response = requests.post(ehr_base_url, headers=headers, data=json.dumps(imaging_study))

    if response.status_code == 201:
        print("ImagingStudy resource created successfully")
        return response.json()  # Return the created resource
    else:
        print(f"Failed to create ImagingStudy resource: {response.status_code}")
        print(response.text)
        return None


