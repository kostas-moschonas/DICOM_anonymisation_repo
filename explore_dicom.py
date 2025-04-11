"""Testing script"""

import pydicom

dcm = pydicom.dcmread("../research_scans_anonymised/MHCM04_20250108/MR.1.3.12.2.1107.5.2.18.42110.2025010817561822793652018")

def find_all_patient_ids(dataset, tag="PatientID"):
    """
    Recursively find all occurrences of a specified tag in a DICOM dataset.

    Args:
        dataset (pydicom.dataset.Dataset): The DICOM dataset to search.
        tag (str): The DICOM tag to search for (default is "PatientID").

    Returns:
        list: A list of all values found for the specified tag.
    """
    patient_ids = []

    for elem in dataset:
        if elem.VR == "SQ":  # If the element is a sequence, recurse into it
            for item in elem.value:
                patient_ids.extend(find_all_patient_ids(item, tag))
        elif elem.keyword == tag:  # Check if the tag matches
            patient_ids.append(elem.value)

    return patient_ids

# Example usage
all_patient_ids = find_all_patient_ids(dcm)
print("All Patient IDs found:", all_patient_ids)