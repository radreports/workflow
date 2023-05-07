import numpy as np
from PIL import Image
import pydicom
from pydicom.uid import ExplicitVRLittleEndian


print("processing .........")
dcm_in = "cxr-poc/dicom_in/1_Nodule.dcm"
dcm_out = "cxr-poc/out.dcm"
img_in = "cxr-poc/pred.png"
ds = pydicom.dcmread(dcm_in)

jpg_image = Image.open(img_in)
# jpg_image = jpg_image.convert("L" )
print("jpg_image.mode::",jpg_image.mode)
if jpg_image.mode == 'L':
       
       np_image = np.array(jpg_image.getdata(),dtype=np.uint8)
       ds.Rows = jpg_image.height
       ds.Columns = jpg_image.width
       ds.PhotometricInterpretation = "MONOCHROME1"
       ds.SamplesPerPixel = 1
       ds.BitsStored = 8
       ds.BitsAllocated = 8
       ds.HighBit = 7
       ds.PixelRepresentation = 0
       ds.PixelData = np_image.tobytes()
       ds.save_as('cxr-poc/result_gray.dcm')


if jpg_image.mode == 'RGB':

    # np_image = np.array(jpg_image.getdata(), dtype=np.uint8)[:,:2]
    np_image = np.array(jpg_image.getdata(), dtype=np.uint8)
    # ds.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.Rows = jpg_image.height
    ds.Columns = jpg_image.width
    ds.PhotometricInterpretation = "RGB"
    ds.SamplesPerPixel = 3
    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = np_image.tobytes()
    
    pydicom.encaps.encapsulate(List[np_image.tobytes()])
    # ds.compress(transfer_syntax_uid =  ExplicitVRLittleEndian)
    # ds.PixelData.is_undefined_length = False
    # ds.encaps.encapsulate()

    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.save_as('cxr-poc/result_rgb.dcm')

# if jpg_image.mode == 'RGB':
#     png = Image.open(img_in)
#     png.load() # required for png.split()

#     background = Image.new("RGB", png.size, (255, 255, 255))
#     background.paste(png, mask=png.split()[3]) # 3 is the alpha channel

#     background.save('cxr-poc/foo.jpg', 'JPEG', quality=80)