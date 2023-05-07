from pathlib import Path

import highdicom as hd
import numpy as np
from pydicom.sr.codedict import codes
from pydicom.filereader import dcmread

def process(dicom_in,nifti_in,rt_out):
    series_dir = Path(dicom_in)
    image_files = series_dir.glob('*.dcm')
    image_datasets = [dcmread(str(f)) for f in image_files]

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
        segment_label='first segment',
        segmented_property_category=codes.cid7150.Tissue,
        segmented_property_type=codes.cid7166.ConnectiveTissue,
        algorithm_type=hd.seg.SegmentAlgorithmTypeValues.AUTOMATIC,
        algorithm_identification=algorithm_identification,
        tracking_uid=hd.UID(),
        tracking_id='test segmentation of computed tomography image'
    )

    seg_dataset = hd.seg.Segmentation(
        source_images=image_datasets,
        pixel_array=mask,
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

    print(seg_dataset)

    seg_dataset.save_as("seg.dcm")


