import pydicom
from pathlib import Path

import highdicom as hd
import numpy as np
from pydicom.filereader import dcmread
from pydicom.sr.codedict import codes
from pydicom.uid import generate_uid
from highdicom.sr.content import FindingSite
from highdicom.sr.templates import Measurement, TrackingIdentifier

def createSR(predictions,original_image,dicom_in,dicom_out):
    print("creating SR report")
    for i in predictions:
        print(i, predictions[i])
    # image_file = Path(dicom_in)
    image_dataset = dcmread(dicom_in)
    print(image_dataset)
    observer_person_context = hd.sr.ObserverContext(
    observer_type=codes.DCM.Person,
    observer_identifying_attributes=hd.sr.PersonObserverIdentifyingAttributes(
        name='DeepMD'
    )
    )
    observer_device_context = hd.sr.ObserverContext(
    observer_type=codes.DCM.Device,
    observer_identifying_attributes=hd.sr.DeviceObserverIdentifyingAttributes(
        uid=hd.UID()
    )
    )
    observation_context = hd.sr.ObservationContext(
        observer_person_context=observer_person_context,
        observer_device_context=observer_device_context,
    )
    referenced_region = hd.sr.ImageRegion3D(
    graphic_type=hd.sr.GraphicTypeValues3D.POLYGON,
    graphic_data=np.array([
        (165.0, 200.0, 1),
        (170.0, 200.0, 1),
        (170.0, 220.0, 1),
        (165.0, 220.0, 1),
        (165.0, 200.0, 1),
    ]),
    frame_of_reference_uid="1.3.6.1.4.1.9328.50.51.10647660542383763"
    # frame_of_reference_uid=image_dataset.FrameOfReferenceUID
    )
    # Describe the anatomic site at which observations were made
    finding_sites = [
        FindingSite(
            anatomic_location=codes.SCT.CervicoThoracicSpine,
            topographical_modifier=codes.SCT.VertebralForamen
        ),
    ]

    # Describe the imaging measurements for the image region defined above
    measurements = [
        Measurement(
            name=codes.SCT.AreaOfDefinedRegion,
            tracking_identifier=hd.sr.TrackingIdentifier(uid=generate_uid()),
            value=1.7,
            unit=codes.UCUM.SquareMillimeter,
            properties=hd.sr.MeasurementProperties(
                normality=hd.sr.CodedConcept(
                    value="17621005",
                    meaning="Normal",
                    scheme_designator="SCT"
                ),
                level_of_significance=codes.SCT.NotSignificant
            )
        )
    ]
    imaging_measurements = [
        hd.sr.PlanarROIMeasurementsAndQualitativeEvaluations(
            tracking_identifier=TrackingIdentifier(
                uid=hd.UID(),
                identifier='Planar ROI Measurements'
            ),
            referenced_region=referenced_region,
            finding_type=codes.SCT.SpinalCord,
            measurements=measurements,
            finding_sites=finding_sites
        )
    ]

    # Create the report content
    measurement_report = hd.sr.MeasurementReport(
        observation_context=observation_context,
        procedure_reported=codes.LN.CTUnspecifiedBodyRegion,
        imaging_measurements=imaging_measurements
    )

    # Create the Structured Report instance
    sr_dataset = hd.sr.Comprehensive3DSR(
        evidence=[image_dataset],
        content=measurement_report[0],
        series_number=1,
        series_instance_uid=hd.UID(),
        sop_instance_uid=hd.UID(),
        instance_number=1,
        manufacturer='DepMD'
    )
    sr_dataset.save_as((dicom_out+'/rt-struct.dcm'))
    print("Completed ...")

    # print(sr_dataset)


