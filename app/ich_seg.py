import csv
import logging
import numpy as np
import SimpleITK
import pydicom
import pydicom_seg
from pathlib import Path
from palettable.tableau import tableau



classes = {
   
        
       1: "SAH",
       2: "IVHem",
       3: "Ventricle",
       4:  "ICH",
        5: "Aneurysm",
        6:"subdural",
   
    
}

# Set the log level
logging.basicConfig(level=logging.WARN)

# Create logger
logger = logging.getLogger("NIfTI to SEG")

# Get color palette
colormap = tableau.get_map("TrafficLight_9")

# Default CSV delimiter
CSV_DELIMITER = ","


def get_nifti_labels(sitk_image):
    print("Reading NIfTI file to identify ROIs...")
    image_data = SimpleITK.GetArrayFromImage(sitk_image)

    labels = np.trim_zeros(np.unique(image_data))
    for label in labels:
        logger.debug(f"found label n°{int(label)} in image")

    return labels


def generate_metadata(roi_dict, series_description="Segmentation"):
    if roi_dict is not None:
        segment_attributes = [get_segments(roi_dict)]
    else:
        segment_attributes = [[get_segment(1, "Probability Map", colormap.colors[0])]]

    basic_info = {
        "ContentCreatorName": "NIfTI to SEG",
        "ClinicalTrialSeriesID": "Session1",
        "ClinicalTrialTimePointID": "1",
        "SeriesDescription": series_description,
        "SeriesNumber": "300",
        "InstanceNumber": "1",
        "segmentAttributes": segment_attributes,
        "ContentLabel": "SEGMENTATION",
        "ContentDescription": "Image segmentation",
        "ClinicalTrialCoordinatingCenterName": "dcmqi",
        "BodyPartExamined": "",
    }

    return basic_info


def get_segments(roi_dict):
    segments = []
    i = 0
    for label, description in roi_dict.items():
        segments.append(get_segment(label, description, colormap.colors[i % len(colormap.colors)]))
        i += 1

    return segments


def get_segment(label, description, color):
    return {
        "labelID": int(label),
        "SegmentDescription": description,
        "SegmentLabel": description,
        "SegmentAlgorithmType": "AUTOMATIC",
        "SegmentAlgorithmName": "Automatic",
        "SegmentedPropertyCategoryCodeSequence": {
            "CodeValue": "85756007",
            "CodingSchemeDesignator": "SCT",
            "CodeMeaning": "Tissue",
        },
        "SegmentedPropertyTypeCodeSequence": {
            "CodeValue": "113343008",
            "CodingSchemeDesignator": "SCT",
            "CodeMeaning": "Organ",
        },
        "recommendedDisplayRGBValue": color,
    }


def match_orientation(sitk_img_ref, sitk_img_sec, verbose=True):
    orientation_filter = SimpleITK.DICOMOrientImageFilter()
    orientation_ref = orientation_filter.GetOrientationFromDirectionCosines(sitk_img_ref.GetDirection())
    orientation_sec = orientation_filter.GetOrientationFromDirectionCosines(sitk_img_sec.GetDirection())
    if verbose:
        print(f"Reference image has orientation '{orientation_ref}'")
        print(f"Second image has orientation    '{orientation_sec}'")
    if orientation_ref != orientation_sec:
        if verbose:
            print(f"Converting orientation of second image: '{orientation_sec}' --> '{orientation_ref}'")
        orientation_filter.SetDesiredCoordinateOrientation(orientation_ref)
        img_sec_reoriented = orientation_filter.Execute(sitk_img_sec)
        orientation_sec_reoriented = orientation_filter.GetOrientationFromDirectionCosines(
            img_sec_reoriented.GetDirection()
        )
        return img_sec_reoriented
    else:
        return sitk_img_sec


def match_size(sitk_img_ref, sitk_img_sec, verbose=True, interpolator=SimpleITK.sitkNearestNeighbor):
    size_ref = sitk_img_ref.GetSize()
    size_sec = sitk_img_sec.GetSize()
    if verbose:
        print(f"Reference image has size '{size_ref}'")
        print(f"Second image has size    '{size_sec}'")
    if not np.all(size_ref == size_sec):
        if verbose:
            print(f"Resampling second image: '{size_sec}' --> '{size_ref}'")
        resample = SimpleITK.ResampleImageFilter()
        resample.SetReferenceImage(sitk_img_ref)
        resample.SetInterpolator(interpolator)
        sitk_img_sec_resampled = resample.Execute(sitk_img_sec)
        return sitk_img_sec_resampled
    else:
        return sitk_img_sec


def get_dcm_as_sitk(path_to_dcm_dir):
    reader = SimpleITK.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(path_to_dcm_dir)
    reader.SetFileNames(dicom_names)
    image = reader.Execute()
    return image

def get_dicom_paths_from_dir(dicom_dir):
    files = Path(dicom_dir).glob("**/*")
    paths = [str(f) for f in files if f.is_file()]

    return paths
def nifti_to_seg(
    sitk_image,
    dicom_input,
    seg_output,
    roi_dict,
    series_description="Segmentation",
    fractional=False,
    match_orientation_flag=False,
    match_size_flag=False,
    skip_empty_slices=True,
    inplane_cropping=False,
    skip_missing_segment=False,
):
    segmentation: SimpleITK.Image = sitk_image

    if roi_dict is not None and segmentation.GetPixelID() not in [
        SimpleITK.sitkUInt8,
        SimpleITK.sitkUInt16,
        SimpleITK.sitkUInt32,
        SimpleITK.sitkUInt64,
    ]:
        segmentation = cast_to_unsigned(segmentation)

    dicom_series_paths = get_dicom_paths_from_dir(dicom_input)
    source_images = [pydicom.dcmread(img, stop_before_pixels=True) for img in dicom_series_paths]

    metadata = generate_metadata(roi_dict, series_description)
    template = pydicom_seg.template.from_dcmqi_metainfo(metadata)

    if match_orientation_flag or match_size_flag:
        dicom_img = get_dcm_as_sitk(dicom_input)
        if match_orientation_flag:
            segmentation = match_orientation(dicom_img, segmentation, verbose=True)
        if match_size_flag:
            segmentation = match_size(
                dicom_img,
                segmentation,
                interpolator=SimpleITK.sitkNearestNeighbor,
                verbose=True,
            )

    writer_class = pydicom_seg.FractionalWriter if fractional else pydicom_seg.MultiClassWriter

    arguments = {
        "template": template,
        "skip_empty_slices": skip_empty_slices,
        "skip_missing_segment": skip_missing_segment,
    }

    if not fractional:
        arguments["inplane_cropping"] = inplane_cropping

    writer = writer_class(**arguments)
    dcm = writer.write(segmentation, source_images)
    dcm.save_as(seg_output)

    print(f"Successfully wrote output to {seg_output}")


def cast_to_unsigned(segmentation):
    original_pixel_type = segmentation.GetPixelID()

    if original_pixel_type == SimpleITK.sitkInt8:
        new_pixel_type = SimpleITK.sitkUInt8
    elif original_pixel_type == SimpleITK.sitkInt16:
        new_pixel_type = SimpleITK.sitkUInt16
    elif original_pixel_type == SimpleITK.sitkInt32:
        new_pixel_type = SimpleITK.sitkUInt32
    elif original_pixel_type == SimpleITK.sitkInt64:
        new_pixel_type = SimpleITK.sitkUInt64
    else:
        raise ValueError("This segmentation pixel type is not supported!")

    casted_segmentation = SimpleITK.Cast(segmentation, new_pixel_type)

    return casted_segmentation


def is_fractional(sitk_image):
    return sitk_image.GetPixelID() in [SimpleITK.sitkFloat32, SimpleITK.sitkFloat64]


def process(dicom_input_dir, nifti_mask_file, output_dir, label_dict):
    sitk_image = SimpleITK.ReadImage(nifti_mask_file)

    fractional = is_fractional(sitk_image)

    if not fractional:
        labels = get_nifti_labels(sitk_image)
        roi_dict = {label: label_dict[label] for label in labels}
    else:
        roi_dict = None

    nifti_to_seg(
        sitk_image,
        dicom_input_dir,
        output_dir,
        roi_dict,
        series_description="Segmentation",
        fractional=fractional,
        match_orientation_flag=True,
        match_size_flag=False,
        skip_empty_slices=True,
        inplane_cropping=False,
        skip_missing_segment=False,
    )
