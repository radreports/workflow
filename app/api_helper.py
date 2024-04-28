
from datetime import datetime
import requests,json

def getDate():
    now = datetime.now() # current date and time

    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    time = now.strftime("%H:%M:%S")
    date_time = now.strftime("%y-%m-%d")
    # "2012-12-01T12:00:00+01:00"
    print("date and time:",date_time)
    return year +"-" + month + "-"+day

def getImageID(url,study_id):
    print("getImageID ...",url + "/" + study_id)
    resp = requests.get(url + "/" + "ImagingStudy/"+study_id)
    imaging = resp.text
    print(imaging)
    imaging = json.loads(imaging)
    series = imaging['series']
    print("series::",series)
    image_id = series[0]
    print("image_id::",image_id["uid"])
    image_id = image_id["uid"]
    return image_id

def get_patient(url, patient_id):
    resp = requests.get(url + "/" + patient_id)


def create_diagnosticReport(patient_id,study_id,Modality,findings,observation_id,seriesID,url):
    print("create_diagnosticReport",study_id)
    image_id = ""
    try:
        image_id = getImageID(url,study_id)
    except Exception as e:
        print(e)
    dr = {
        "resourceType" : "DiagnosticReport",
        "result" : [
                {
                    "reference" : observation_id
                }
            ],
        
        "text" : {
            "status" : "generated",
            "div" : "<div xmlns=\"http://www.w3.org/1999/xhtml\"><h2><span title=\"Codes: {http://snomed.info/sct 429858000}\">CT of head-neck</span> (<span title=\"Codes: {http://snomed.info/sct 394914008}, {http://terminology.hl7.org/CodeSystem/v2-0074 RAD}\">Radiology</span>) </h2><table class=\"grid\"><tr><td>Subject</td><td><b>Roel(OFFICIAL)</b> male, DoB: 1960-03-13 ( BSN:\u00a0123456789\u00a0(use:\u00a0OFFICIAL))</td></tr><tr><td>When For</td><td>2012-12-01T12:00:00+01:00</td></tr><tr><td>Reported</td><td>2012-12-01T12:00:00+01:00</td></tr></table><p><b>Report Details</b></p><div><p>CT brains: large tumor sphenoid/clivus.</p>\n</div><p><b>Coded Conclusions :</b></p><ul><li><span title=\"Codes: {http://snomed.info/sct 188340000}\">Malignant tumor of craniopharyngeal duct</span></li></ul></div>"
        },
        
        "status" : "Partial",
        "category" : [{
            "coding" : [{
            "system" : "http://snomed.info/sct",
            "code" : "394914008",
            "display" : "Radiology"
            },
            {
            "system" : "http://terminology.hl7.org/CodeSystem/v2-0074",
            "code" : "RAD"
            }]
        }],
        "code" : {
            "coding" : [{
            "system" : "http://snomed.info/sct",
            "code" : "429858000",
            "display" : Modality
            }],
            "text" : Modality
        },
        "subject" : {
            "reference" :patient_id,
            
        },
        "study" : [
                {
                    "reference" : "ImagingStudy/"+study_id
                }
            ],
        "effectiveDateTime" : getDate(),
        "issued" : getDate(),
        
        "conclusion" : findings,
        "conclusionCode" : [{
            "coding" : [{
            "system" : "http://snomed.info/sct",
            "code" : image_id,
            "display" : findings
            }]
        }],
        "note": [ {
                "text": image_id
              } ]
        }
    print("Generated DR",dr)
    return dr

def createObservation(patient_id,study_id,service_id,Modality,findings,body_site):

    observation = {
            "resourceType" : "Observation",
            "basedon":[
                {
                    "reference" : study_id
                },
                {
                    "reference" : service_id
                },

            ],
            "text" : {
                "status" : "generated",
                "div" : "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Generated Narrative: Observation</b><a name=\"bmd\"> </a></p><div style=\"display: inline-block; background-color: #d9e0e7; padding: 6px; margin: 4px; border: 1px solid #8da1b4; border-radius: 5px; line-height: 60%\"><p style=\"margin-bottom: 0px\">Resource Observation &quot;bmd&quot; </p></div><p><b>status</b>: final</p><p><b>code</b>: BMD - Left Femur <span style=\"background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki\"> (<a href=\"https://loinc.org/\">LOINC</a>#24701-5 &quot;Femur DXA Bone density&quot;)</span></p><p><b>subject</b>: <a href=\"patient-example-b.html\">Patient/pat2</a> &quot;Duck DONALD&quot;</p><p><b>performer</b>: <span title=\"       well, actually. this isn't the patient, but it'll do for now       \"><a href=\"organization-example-lab.html\">Organization/1832473e-2fe0-452d-abe9-3cdb9879522f: Acme Imaging Diagnostics</a> &quot;Clinical Lab&quot;</span></p><p><b>value</b>: 0.887 g/cm²<span style=\"background: LightGoldenRodYellow\"> (Details: UCUM code g/cm-2 = 'g/cm-2')</span></p><p><b>bodySite</b>: Left Femur <span style=\"background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki\"> (<a href=\"https://browser.ihtsdotools.org/\">SNOMED CT</a>#71341001:272741003=7771000)</span></p></div>"
            },
            "status" : "final",
            "code" : {
                "coding" : [{
                "system" : "http://loinc.org",
                "code" : "24701-5",
                "display" : findings
                }],
                "text" : findings
            },
            "subject" : {
                "reference" : patient_id
            },
          
            
            "bodySite" : {
                "coding" : [{
                "system" : "http://snomed.info/sct",
                "code" : "71341001:272741003=7771000"
                }],
                "text" : body_site
            }
        }
    
    return observation