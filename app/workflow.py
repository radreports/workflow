import os
import shutil
import zipfile
# import tempfile
import requests
import tempfile, pydicom
from PIL import Image
import app.Thoractic as thor
import app.Liver_seg as liver_seg
# import app.Liver_seg2 as liver_seg
import app.Lung as lung
# import app.Lung_RT as lung
import app.Lung_seg2 as lung_seg
import app.Lung_NSCLC_seg as lung_seg_nsclc
import app.breast_mri_seg as breast_mri_seg
import app.Breast_Fibroglandular_seg as breast_fibroglandular_seg

import app.Hepatic_seg as hepatic_seg
import app.ich as ich
import app.ich2 as ich2
import app.ich_seg as ich_seg
import app.Kidney as kidney
import app.Abdoman as abdoman
import app.Colon as colon
import app.Pancreas as pancreas
import app.Totalseg as totalseg
import app.Totalseg_rt as totalseg_rt
import app.api_helper as helper
import app.lung_nodules as lung_nodules
from . import dicom_util
import dicom2nifti
from beren import Orthanc
import requests, json
import numpy as np
import app.ReportGenerator as reportGenerator
import app.process_liver as process_liver
import app.amos_seg as amos_seg
import app.DiagnosticReport_Lungnodules as diagnosticReport
import time

import app.liver_process as liver_process
import app.HaN_seg as haN_seg
import app.HaN_RT as haN_RT
import app.breast_mri_process as breast_mri_process
import app.ImagingStudy as imagingStudy
import app.process_han as process_han

# lungx = "http://104.171.203.4:5000/predict/v2/Task006_Lung"
# lungx = "http://104.171.203.4:5000/predict/Task777_CT_Nodules"
lungx = "http://104.171.203.4:5000/predict/Task775_CT_NSCLC_RG"
# liverx = "http://104.171.203.4:5000/predict/Task003_Liver"
# liverx = "http://104.171.203.4:5000/predict/v2/006"
liverx = "http://104.171.203.4:5000/predict/Task773_Liver"
THOR_X = "http://104.171.203.4:5000/predict/Task055_SegTHOR"
ABD_X = "http://104.171.203.4:5000/predict/Task017_AbdominalOrganSegmentation"
HAN_X = ""
COLON_X = "http://104.171.203.4:5000/predict/Task010_Colon"
HEPATIC = "http://104.171.203.4:5000/predict/Task008_HepaticVessel"
ICH_NNUNET = "http://104.171.203.4:5000/predict/ich"
ICH = "http://104.171.203.4:5000/ich/infer"
# TOTAL_SEG = "http://104.171.203.4:5001/predict/totalseg"
AMOS = "http://104.171.203.4:5000/predict/v2/219"
# Dataset011_Breast
BREAST_MRI = "http://104.171.203.4:5000/predict/v2/011"
FibroglandularBreast= "http://104.171.203.4:5000/predict/v2/009"

PANCREAS = "http://104.171.203.4:5000/pancreas/predict1"
Head_Neck_OAR = "http://104.171.203.4:5000/predict/totalseg/head_glands_cavities"
headneck_bones_vessels = "http://104.171.203.4:5000/predict/totalseg/headneck_bones_vessels"
TOTAL_SEG = "http://104.171.203.4:5000/predict/totalseg/total"


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

def inferAMOS(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = AMOS
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()      

def inferHead_Neck(nifti_in,nifti_out):
    print()
    han1 = nifti_out + "/han1.nii.gz"
    han2 = nifti_out + "/han2.nii.gz"
    han = nifti_out + "/predictions2.nii.gz"
    myurl = Head_Neck_OAR
    myurl2 = headneck_bones_vessels

    infile_path = os.path.join(nifti_in, "infile_0000.nii.gz")

    # First request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl2, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in first request: {r.status_code}")
            print(r.text)
            return
        
        with open(han1, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    time.sleep(5)

    print("Slept for 60 seconds")

    # Second request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in second request: {r.status_code}")
            print(r.text)
            return
        
        with open(han2, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    process_han.process(nifti_out)
            

def inferLits(nifti_in, nifti_out):
    local_filename = nifti_out + "/prediction.nii.gz"
    liver = nifti_out + "/predictions1.nii.gz"
    liver_tumor = nifti_out + "/predictions2.nii.gz"
    myurl = liverx
    myurl2 = HEPATIC

    infile_path = os.path.join(nifti_in, "infile_0000.nii.gz")

    # First request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl2, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in first request: {r.status_code}")
            print(r.text)
            return
        
        with open(liver_tumor, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    time.sleep(5)

    print("Slept for 60 seconds")

    # Second request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in second request: {r.status_code}")
            print(r.text)
            return
        
        with open(liver, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    liver_process.process(nifti_out)


def inferICH(nifti_in,nifti_out):
    print("from inferICH")
    local_filename = nifti_out + "/prediction.nii.gz"
    # myurl = 'http://104.171.203.4:5000/infer'
    myurl = ICH
    myurl2 = ICH_NNUNET
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"file": ("infile_0000.nii.gz", fileobj)}, verify=False)
    # r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

def inferICH_nnunet(nifti_in,nifti_out):
    print("from inferICH")
    local_filename = nifti_out + "/prediction.nii.gz"
    # myurl = 'http://104.171.203.4:5000/infer'
    myurl = ICH_NNUNET
     
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    # r = requests.post(myurl,  files={"file": ("infile_0000.nii.gz", fileobj)}, verify=False)
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

def inferBreastMRI_backup(nifti_in,nifti_out):
    print("processing lung task ...")
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = BREAST_MRI
    # myurl = "http://104.171.202.250:5000/lits/predict"
    fileobj = open(nifti_in + "/infile_0000.nii.gz", 'rb')
    r = requests.post(myurl,  files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
    f = open(local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
    f.close()


def inferBreastMRI(nifti_in, nifti_out):
    local_filename = nifti_out + "/prediction.nii.gz"
    liver = nifti_out + "/predictions1.nii.gz"
    liver_tumor = nifti_out + "/predictions2.nii.gz"
    myurl = FibroglandularBreast
    myurl2 = BREAST_MRI

    infile_path = os.path.join(nifti_in, "infile_0000.nii.gz")

    # First request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl2, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in first request: {r.status_code}")
            print(r.text)
            return
        
        with open(liver_tumor, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    time.sleep(5)

    print("Slept for 5 seconds")

    # Second request
    with open(infile_path, 'rb') as fileobj:
        r = requests.post(myurl, files={"files[]": ("infile_0000.nii.gz", fileobj)}, verify=False)
        if r.status_code != 200:
            print(f"Error in second request: {r.status_code}")
            print(r.text)
            return
        
        with open(liver, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        r.close()

    breast_mri_process.process(nifti_out)


def inferBreastFibro(nifti_in,nifti_out):
    print("processing lung task ...")
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = FibroglandularBreast
    # myurl = BREAST_MRI
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

def inferTotalSeg(nifti_in,nifti_out):
    print()
    local_filename = nifti_out + "/prediction.nii.gz"
    myurl = TOTAL_SEG
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
    myurl = COLON_X
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

        inferICH_nnunet(niftiIN,niftiout)
        ich_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",ich_seg.classes)

        inferICH(niftiIN,niftiout)
        inference_findings = ich.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        
        inference_findings = "Positive: ICH"
        
        
    if bodyPart.lower() == "thor".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferThor(niftiIN,niftiout)
        Modality = " CT-Lungs"
        bodypartExamined = "OAR Thoractic"
        thor.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        
    if bodyPart.lower() == "amos".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferAMOS(niftiIN,niftiout)
        Modality = " CT"
        bodypartExamined = "OAR AMOS"
        abdoman.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        # amos_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",amos_seg.amos_classes)
        # totalseg.processamos(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)

    if bodyPart.lower() == "Head_Neck_OAR".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferHead_Neck(niftiIN,niftiout)
        Modality = " CT"
        bodypartExamined = "OAR Head and Neck"
        # haN_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",haN_seg.classes)
        # haN_RT.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        haN_RT.process(dicomIN,niftiout +"/han1.nii.gz",rtstructureout+ "/rt-struct.dcm")
        haN_RT.process(dicomIN,niftiout +"/han2.nii.gz",rtstructureout+ "/rt-struct.dcm")
        inference_findings = "OAR Head and Neck"

    if bodyPart.lower() == "liver".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferLits(niftiIN,niftiout)
        Modality = " CT-Abdoman"
        bodypartExamined = "Abdmomen Liver "
        # inference_findings = "Abdoman OAR "
        # inference_findings = liver.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        # liver_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",liver_seg.classes)

        inference_findings = hepatic_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",hepatic_seg.classes)
        # inference_findings = "Positive: Liver Tumor"
        
    if bodyPart.lower() == "lung".lower():
        # try:
        #     dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        # except Exception as e: 
        #     downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferLungs(niftiIN,niftiout)
        # inferAbdoman(niftiIN,niftiout)
        Modality = " CT-Lungs"
        bodypartExamined = "Lung Nodules"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)

        # lung_nodules.process_lung_nodules(niftiout +"/prediction.nii.gz",niftiout)
        # data = lung_nodules.load_json_with_int_keys(workingDir + "/nodules.json")
        # json_file_path = workingDir + "/nodules.json"
        # classes = data["classes"]
        # print(classes)

        # lung_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",classes)
        lung_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",lung_seg.classes)
        inference_findings ="Positive: Lung Nodules"
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
        inference_findings =  "OAR Abdoman"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        abdoman.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
     
    if bodyPart.lower() == "totalseg".lower():
        try:
            dicom2nifti.dicom_series_to_nifti(dicomIN, niftiIN + "/infile_0000.nii.gz")
        except Exception as e: 
            downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        # inferLungs(niftiIN,niftiout)
        inferTotalSeg(niftiIN,niftiout)
        Modality = " CT-Total seg"
        bodypartExamined = "Multi Organs"
        inference_findings =  "OAR Multi Organs"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        # totalseg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        totalseg_rt.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)

    
    if bodyPart.lower() == "breast_mri".lower():
        downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferBreastMRI(niftiIN,niftiout)
        # inferAbdoman(niftiIN,niftiout)
        Modality = " Breast MRI"
        bodypartExamined = "Breast MRI"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        inference_findings = breast_mri_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",breast_mri_seg.classes)
        # inference_findings ="Positive: Breast Cancer"

    if bodyPart.lower() == "breast_fibro".lower():
        print("Infering breast_fibro")
        downloadNifti(OrthancURL,seriesID,niftiIN + "/infile_0000.nii.gz")
        inferBreastFibro(niftiIN,niftiout)
        # inferAbdoman(niftiIN,niftiout)
        Modality = " Breast MRI"
        bodypartExamined = "Breast MRI"
        # lung.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout)
        breast_fibroglandular_seg.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm",breast_fibroglandular_seg.classes)
        inference_findings ="Breast fibroglandular"
        
    # if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
    #     fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
    #     headers = {"Content-Type":"application/binary",}
    #     getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
    #     print(getdata.text)

    # data = {
    #     "study_id":study_id,
    #     "inference_findings":inference_findings
    # }
    # url = "http://localhost:8888/api/v1/studies"
    #  create observation
        
    if bodyPart.lower() == "lung".lower() and "positive" in inference_findings.lower():
        print("Going to generate diagnostic Report for Lung nodules")
        # reportGenerator.process(ehr_url,patient_id,study_id,niftiIN + "/infile_0000.nii.gz",niftiout +"/prediction.nii.gz",1,inference_findings)
        diagnosticReport.process(ehr_url,patient_id,study_id,niftiIN + "/infile_0000.nii.gz",niftiout +"/prediction.nii.gz",inference_findings,"CT","Lungs")
        
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)

    elif (bodyPart.lower() == "liver".lower() ):
        print("Going to generate diagnostic Report for Liver Tumor")
        ## process_liver.main(dicomIN,niftiIN + "/infile_0000.nii.gz", niftiout +"/prediction.nii.gz", rtstructureout , OrthancURL, ehr_url,study_id,patient_id)
        ## reportGenerator.process(ehr_url,patient_id,study_id,niftiIN + "/infile_0000.nii.gz",niftiout +"/prediction.nii.gz",2,inference_findings)
        diagnosticReport.process(ehr_url,patient_id,study_id,niftiIN + "/infile_0000.nii.gz",niftiout +"/prediction.nii.gz",inference_findings,"CT","Liver")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)
            if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
                fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
                headers = {"Content-Type":"application/binary",}
                getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
                print(getdata.text)

    elif bodyPart.lower() == "breast_mri".lower():
        print("Going to generate diagnostic Report for Breast MRI")
        diagnosticReport.process(ehr_url,patient_id,study_id,niftiIN + "/infile_0000.nii.gz",niftiout +"/prediction.nii.gz",inference_findings,"MRI","Breast")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'):
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)

    elif(bodyPart.lower() == "Head_Neck_OAR".lower() ):
        print("Going to generate OAR for Head and Neck")
        # haN_RT.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'): 
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)
        oar = "Head and Neck OAR contouring"
        imagingStudy.process(ehr_url+"/ImagingStudy",patient_id,study_id,oar)
    
    elif(bodyPart.lower() == "totalseg".lower() ):
        print("Going to generate OAR for Total Segmentation")
        # haN_RT.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'): 
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)
        oar = "Multi Organs OAR contouring"
        imagingStudy.process(ehr_url+"/ImagingStudy",patient_id,study_id,oar)

    elif(bodyPart.lower() == "thor".lower() ):
        print("Going to generate OAR for Thoractic")
        # haN_RT.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'): 
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)
        oar = "Thoractic OAR contouring"
        imagingStudy.process(ehr_url+"/ImagingStudy",patient_id,study_id,oar)


    elif bodyPart.lower() == "Abdoman".lower():
        print("Going to generate OAR for Abdoman")
        # haN_RT.process(dicomIN,niftiout +"/prediction.nii.gz",rtstructureout+ "/rt-struct.dcm")
        if os.path.isfile(rtstructureout + '/rt-struct.dcm'): 
            fileobj = open(rtstructureout + '/rt-struct.dcm', 'rb')
            headers = {"Content-Type":"application/binary",}
            getdata = requests.post(OrthancURL+"/instances", data=fileobj,headers=headers )
            print(getdata.text)
        oar = "Abdoman OAR contouring"
        imagingStudy.process(ehr_url+"/ImagingStudy",patient_id,study_id,oar)

    else:

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
        print("completed workflow ...",resp.text)
        
        # 
    # url = api_url + "/Notification"
    # data = {
    #     "subject": "Peter Pan",
    #     "result": inference_findings
    # }
    # resp = requests.post(url, data = json.dumps(data),headers = headers)
    