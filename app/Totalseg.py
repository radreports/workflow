import csv
import logging
import numpy as np
import SimpleITK
import pydicom
import pydicom_seg
from pathlib import Path
from palettable.tableau import tableau

amos_classes = {
   
    
    1: "spleen",
    2: "right kidney",
    3: "left kidney",
    4: "gall bladder",
    5: "esophagus",
    6: "liver",
    7: "stomach",
    8: "arota",
    9: "postcava",
    10: "pancreas",
    11: "right adrenal gland",
    12: "left adrenal gland",
    13: "duodenum",
    14: "bladder",
    15: "prostate/uterus"
}

classes = {
        1: "spleen",
        2: "kidney_right",
        3: "kidney_left",
        4: "gallbladder",
        5: "liver",
        6: "stomach",
        7: "pancreas",
        8: "adrenal_gland_right",
        9: "adrenal_gland_left",
        10: "lung_upper_lobe_left",
        11: "lung_lower_lobe_left",
        12: "lung_upper_lobe_right",
        13: "lung_middle_lobe_right",
        14: "lung_lower_lobe_right",
        15: "esophagus",
        16: "trachea",
        17: "thyroid_gland",
        18: "small_bowel",
        19: "duodenum",
        20: "colon",
        21: "urinary_bladder",
        22: "prostate",
        23: "kidney_cyst_left",
        24: "kidney_cyst_right",
        25: "sacrum",
        26: "vertebrae_S1",
        27: "vertebrae_L5",
        28: "vertebrae_L4",
        29: "vertebrae_L3",
        30: "vertebrae_L2",
        31: "vertebrae_L1",
        32: "vertebrae_T12",
        33: "vertebrae_T11",
        34: "vertebrae_T10",
        35: "vertebrae_T9",
        36: "vertebrae_T8",
        37: "vertebrae_T7",
        38: "vertebrae_T6",
        39: "vertebrae_T5",
        40: "vertebrae_T4",
        41: "vertebrae_T3",
        42: "vertebrae_T2",
        43: "vertebrae_T1",
        44: "vertebrae_C7",
        45: "vertebrae_C6",
        46: "vertebrae_C5",
        47: "vertebrae_C4",
        48: "vertebrae_C3",
        49: "vertebrae_C2",
        50: "vertebrae_C1",
        51: "heart",
        52: "aorta",
        53: "pulmonary_vein",
        54: "brachiocephalic_trunk",
        55: "subclavian_artery_right",
        56: "subclavian_artery_left",
        57: "common_carotid_artery_right",
        58: "common_carotid_artery_left",
        59: "brachiocephalic_vein_left",
        60: "brachiocephalic_vein_right",
        61: "atrial_appendage_left",
        62: "superior_vena_cava",
        63: "inferior_vena_cava",
        64: "portal_vein_and_splenic_vein",
        65: "iliac_artery_left",
        66: "iliac_artery_right",
        67: "iliac_vena_left",
        68: "iliac_vena_right",
        69: "humerus_left",
        70: "humerus_right",
        71: "scapula_left",
        72: "scapula_right",
        73: "clavicula_left",
        74: "clavicula_right",
        75: "femur_left",
        76: "femur_right",
        77: "hip_left",
        78: "hip_right",
        79: "spinal_cord",
        80: "gluteus_maximus_left",
        81: "gluteus_maximus_right",
        82: "gluteus_medius_left",
        83: "gluteus_medius_right",
        84: "gluteus_minimus_left",
        85: "gluteus_minimus_right",
        86: "autochthon_left",
        87: "autochthon_right",
        88: "iliopsoas_left",
        89: "iliopsoas_right",
        90: "brain",
        91: "skull",
        92: "rib_left_1",
        93: "rib_left_2",
        94: "rib_left_3",
        95: "rib_left_4",
        96: "rib_left_5",
        97: "rib_left_6",
        98: "rib_left_7",
        99: "rib_left_8",
        100: "rib_left_9",
        101: "rib_left_10",
        102: "rib_left_11",
        103: "rib_left_12",
        104: "rib_right_1",
        105: "rib_right_2",
        106: "rib_right_3",
        107: "rib_right_4",
        108: "rib_right_5",
        109: "rib_right_6",
        110: "rib_right_7",
        111: "rib_right_8",
        112: "rib_right_9",
        113: "rib_right_10",
        114: "rib_right_11",
        115: "rib_right_12",
        116: "sternum",
        117: "costal_cartilages"
    }

# Set the log level
logging.basicConfig(level=logging.WARN)

# Create logger
logger = logging.getLogger("NIfTI to SEG")

# Get color palette
colormap = tableau.get_map("BlueRed_6")

# Default CSV delimiter
CSV_DELIMITER = ","


def get_nifti_labels(sitk_image):
    print("Reading NIfTI file to identify ROIs...")
    image_data = SimpleITK.GetArrayFromImage(sitk_image)

    labels = np.trim_zeros(np.unique(image_data))
    for label in labels:
        logger.debug(f"found label n°{int(label)} in image")
        print(f"found label n°{int(label)} in image")

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
    direction_ref = sitk_img_ref.GetDirection()
    direction_sec = sitk_img_sec.GetDirection()

    # Adjust the reference direction cosines if they have a length of 16 (4x4 matrix)
    if len(direction_ref) == 16:
        direction_ref = direction_ref[:9]

    print(f"Direction cosines of reference image: {direction_ref}")
    print(f"Direction cosines of second image: {direction_sec}")

    if len(direction_ref) != 9 or len(direction_sec) != 9:
        raise ValueError("The direction cosines must be of length 9 (3x3 matrix).")

    orientation_ref = orientation_filter.GetOrientationFromDirectionCosines(direction_ref)
    orientation_sec = orientation_filter.GetOrientationFromDirectionCosines(direction_sec)

    if verbose:
        print(f"Reference image has orientation '{orientation_ref}'")
        print(f"Second image has orientation    '{orientation_sec}'")

    if orientation_ref != orientation_sec:
        if verbose:
            print(f"Converting orientation of second image: '{orientation_sec}' --> '{orientation_ref}'")
        orientation_filter.SetDesiredCoordinateOrientation(orientation_ref)
        img_sec_reoriented = orientation_filter.Execute(sitk_img_sec)
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
    source_images = []
    for img in dicom_series_paths:
        ds = pydicom.dcmread(img, stop_before_pixels=True)
        # Check for the presence of 'ImagePositionPatient' attribute
        if hasattr(ds, 'ImagePositionPatient'):
            source_images.append(ds)

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
    pixel_id = sitk_image.GetPixelID()
    pixel_type = SimpleITK.GetPixelIDValueAsString(pixel_id)
    print(f"Pixel type: {pixel_type}")
    return pixel_id in [SimpleITK.sitkFloat32, SimpleITK.sitkFloat64]


def process(dicom_input_dir, nifti_mask_file, output_dir):
    label_dict = classes
    sitk_image = SimpleITK.ReadImage(nifti_mask_file)

    fractional = is_fractional(sitk_image)
    print(f"Fractional image: {fractional}")

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
