from pathlib import Path
import nibabel as nib
import highdicom as hd
import numpy as np
from pydicom.sr.codedict import codes
from pydicom.filereader import dcmread

def process(dicom_in,nifti_in,rt_out):
    series_dir = Path(dicom_in)
    image_files = series_dir.glob('*.dcm')
    image_datasets = [dcmread(str(f)) for f in image_files]
    nii = nib.load(nifti_in)
    print("shape = ::", nii.shape)
    pred_nrrd_lung = nii.get_fdata() 
    pred_nrrd_lung = np.transpose(pred_nrrd_lung, (2, 1, 0))
    lung = np.copy(pred_nrrd_lung)
    un = np.unique(lung)
    print(un)
    lung[pred_nrrd_lung != 1] = 0
    lung[lung != 0] = 1
    lung = np.array(lung, dtype=bool)
    # lung = lung[..., ::-1]
    # lung = np.transpose(lung, (2, 1, 0))

    mask = np.zeros(
    shape=(
        len(image_datasets),
        image_datasets[0].Rows,
        image_datasets[0].Columns
    ),
    dtype=bool
    )
    mask[1:-1, 10:-10, 100:-100] = True

    algorithm_identification = hd.AlgorithmIdentificationSequence(
        name='test',
        version='v1.0',
        family=codes.cid7162.ArtificialIntelligence
    )
    description_segment_1 = hd.seg.SegmentDescription(
        segment_number=1,
        segment_label='Lung Nodules',
        segmented_property_category=codes.cid7150.Tissue,
        segmented_property_type=codes.cid7166.ConnectiveTissue,
        algorithm_type=hd.seg.SegmentAlgorithmTypeValues.AUTOMATIC,
        algorithm_identification=algorithm_identification,
        tracking_uid=hd.UID(),
        tracking_id='test segmentation of computed tomography image'
    )

    seg_dataset = hd.seg.Segmentation(
        source_images=image_datasets,
        pixel_array=lung,
        segmentation_type=hd.seg.SegmentationTypeValues.BINARY,
        segment_descriptions=[description_segment_1],
        series_instance_uid=hd.UID(),
        series_number=2,
        sop_instance_uid=hd.UID(),
        instance_number=1,
        manufacturer='Manufacturer',
        manufacturer_model_name='Model',
        software_versions='v1',
        device_serial_number='Device XYZ',
    )

    # print(seg_dataset)
    # print(" original series_instance_uid=hd.UID() ::", hd.UID())
    # print(" reconstructed series_instance_uid=hd.UID() ::", hd.UID() +".1")

    seg_dataset.save_as(rt_out+"/rt-struct.dcm")


