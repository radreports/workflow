import numpy as np
from PIL import Image
import pydicom
from pydicom.uid import ExplicitVRLittleEndian


print("processing .........")
dcm_in = "temp/fe07298fa1a9109de51c57e56a202df3.dcm"

ds = pydicom.dcmread(dcm_in)
print(ds.file_meta)