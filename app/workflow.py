import os
import shutil
import zipfile
# import tempfile
import requests
import tempfile, pydicom
from PIL import Image
import app.Thoractic as thor
import app.Liver as liver
import app.Liver_seg as liver_seg
import app.Lung as lung
import app.Lung_seg as lung_seg
import app.ich as ich
import app.ich2 as ich2
import app.ich_seg as ich_seg
import app.Kidney as kidney
import app.Abdoman as abdoman
import app.Colon as colon
import app.Pancreas as pancreas
import app.api_helper as helper
from . import dicom_util
import dicom2nifti
from beren import Orthanc
import requests, json
import numpy as np


lungx = "http://104.171.203.36:5000/predict/Task006_Lung"
liverx = "http://104.171.203.36:5000/predict/Task003_Liver"
THOR_X = "http://104.171.203.36:5000/predict/Task055_SegTHOR"
ABD_X = "http://104.171.203.36:5000/predict/Task017_AbdominalOrganSegmentation"
HAN_X = ""
def unarchieve(zipDir,outDir):
    with zipfile.ZipFile(zipDir) as zip_file:
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # skip directories
            if not filename:
                continue
        
            # copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            target = open(os.path.join(outDir, filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)

def getArchieve(seriesID,orthanc,archieveDir):
    
    # print(archieveDir.name)
    r = orthanc.get_study_archive(seriesID)
   
    zipFile = archieveDir + "/my_file.zip"
    
    binary_file = open(zipFile, "wb")
  
    for i in r:
        # temp = temp +i
        binary_file.write(i)
        # print(i)
    binary_file.close()

def inferCXR(image_in,dicom_out,image_out=None):
    print("infering CXR ...",image_in)
    myurl = "http://models.deepmd.io/cxr/predict"
    # http://models.deepmd.io/cxr/download?filepath=static/tmpr9o6mw7a/pred.jpg
    files = os.listdir(image_in)
    for file in files:
        if file.endswith('.dcm'):
            print("reading dicom ...",file)
            ds = pydicom.dcmread(image_in+'/'+file)
            new_image = ds.pixel_array.astype(float)
            new_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0

            new_image = np.uint8(new_image)
            
            new_image = Image.fromarray(new_image)
            new_image.save(image_out+'/image.jpg')
            fileobj = open(image_out+'/image.jpg' , 'rb')
            r = requests.post(myurl,  files={"files[]": ("image.jpg", fileobj)}, verify=False)
            # print("CXR predictions ::",r.text)
            result = json.loads(r.text)
            # print(result["PredictionBoxes"])
            predictions =  result["PredictionBoxes"]
            dicom_util.createSR(predictions,image_out+'/image.jpg',image_in+'/'+file,dicom_out)
            result = ""
            for i in predictions:
                result = result +","+i
                print(i, predictions[i])
            return result

        

               

def inferLits(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = liverx
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferICH(nifti_in,nifti_out):
    print("from inferICH")
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = 'http://models.deepmd.io/ich/predict'
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferLungs(nifti_in,nifti_out):
    print("processing lung task ...")
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = lungx
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferAbdoman(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = ABD_X
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferThor(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = THOR_X
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferColon(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = 'http://models.deepmd.io/colon/predict'
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def downloadNifti(OrthancURL,seriesID,dir_name):
    url = OrthancURL +"/series/"+seriesID+"/nifti?compress"
    print("Donloading nifti ....",url)
    local_filename = dir_name
    r = requests.get(url)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()
    return 


def process(data):
    # seriesID, orthanc,OrthancURL,bodyPart
    bodyPart = data['Task']
    seriesID = data['Series'][0]
    OrthancURL = data['pacs_url']
    api_url = data["api_url"]
    ehr_url = data["ehr_url"]
    study_id = data["ImagingStudy"]
    ParentStudy = data["ParentStudy"]
    imagingStudy_id = data["study_id"]
    patient_id = data["patient_id"]
    service_id = data["service_id"]
    service_id = "ServiceRequest/" +service_id
    Modality = ""
    bodypartExamined = ""

    # pacs_url =  data['pacs_url']
    orthanc = Orthanc(OrthancURL)

    print("starting inference for:",bodyPart)
    if not os.path.exists("./temp"):
        os.makedirs("./temp")

    currentDir = "./temp"
    workingDir = tempfile.mkdtemp(dir=currentDir)
    archieveDir = tempfile.mkdtemp(dir=workingDir)
    dicomIN = tempfile.mkdtemp(dir=workingDir)
    niftiIN  = tempfile.mkdtemp(dir=workingDir)
    niftiout = tempfile.mkdtemp(dir=workingDir)
    rtstructureout = tempfile.mkdtemp(dir=workingDir)
   
    # getArchieve(seriesID,orthanc,archieveDir)
    # //ParentStudy
    getArchieve(ParentStudy,orthanc,archieveDir)
    unarchieve(archieveDir + "/my_file.zip",dicomIN)
    
    # Lung
    inference_findings = "Negative"
    
    # downloadNifti(OrthancURL,seriesID)
    # uploadDicom("./temp/output")
    if bodyPart.lower() == "cxr".lower():
        print("Processinf cxr ...")
        inference_findings =inferCXR(dicomIN,rtstructureout,niftiout)

    if bodyPart.lower() == "ich".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        print("processing ICG ...")
        Modality = "Non contract CT-Head"
        bodypartExamined = "Head"
        inferICH(niftiIN,niftiout)
        inference_findings = ich.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        
        
    if bodyPart.lower() == "thor".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferThor(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "OAR Thoractic"
        thor.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        

    if bodyPart.lower() == "liver".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferLits(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "Abdmomen Liver "
        # inference_findings = "Abdoman OAR "
        inference_findings = liver.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        
    if bodyPart.lower() == "lung".lower():
        # try:
        #     dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        # except Exception as e: 
        #     downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferLungs(niftiIN,niftiout)
        # inferAbdoman(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "Lung Nodules"
        inference_findings = lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        # abdoman.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)

    if bodyPart.lower() == "colon".lower():
        print("Processing colon ...")
        # try:
        #     dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        # except Exception as e: 
        #     downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferColon(niftiIN,niftiout)
        # inferAbdoman(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "Colon "
        inference_findings = colon.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        # abdoman.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)

    if bodyPart.lower() == "Abdoman".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        # inferLungs(niftiIN,niftiout)
        inferAbdoman(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "Abdoman OAR"
        inference_findings =  "Abdoman OAR"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        abdoman.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
            
    if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
        fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
        headers = {"Content-Type":"application/binary",}
        getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
        print(getdata.text)

    # data = {
    #     "study_id":study_id,
    #     "inference_findings":inference_findings
    # }
    # url = "http://localhost:8888/api/v1/studies"
    #  create observation
    headers = {"Content-Type":"application/json"}
    url = ehr_url + "/Observation"
    
    data = helper.createObservation(patient_id,study_id,service_id,Modality,inference_findings,bodypartExamined)
    resp = requests.post(url, data = json.dumps(data),headers = headers)
    print("completed workflow ...",resp.text)
    observation = resp.text
    observation = json.loads(observation)
    observation_id = observation["id"]
    observation_id = "Observation/" + observation_id
    

    #  create diagnosticReport
    url = ehr_url + "/DiagnosticReport"
    data = helper.create_diagnosticReport(patient_id,study_id,Modality,inference_findings,observation_id,seriesID,api_url)
    resp = requests.post(url, data = json.dumps(data),headers = headers)
    print("completed workflow ...",resp.text)

    # url = api_url + "/Notification"
    # data = {
    #     "subject": "Peter Pan",
    #     "result": inference_findings
    # }
    # resp = requests.post(url, data = json.dumps(data),headers = headers)
    print("completed workflow ...",resp.text)