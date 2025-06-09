"""Creates a random key A+number for each PatientID in a folder containing DICOM files.
Each study is zipped.

Author: Kostas Moschonas
Date: 08-06-2025
"""

import os
import pydicom
import csv
import zipfile
import tempfile
import shutil

def create_anon_keys(input_dir, output_csv):
    """
    Iterate through folders or zipped folders containing DICOM files, extract PatientID, and create anonymized keys.
    Save the keys in a CSV file with columns: PatientID, AnonID.
    """
    anon_keys = {}
    counter = 1
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory at the start

    try:
        # Walk through all files in the input directory
        for root, _, files in os.walk(input_dir):
            print(f"Processing directory: {root}")  # Debugging log
            for file in files:
                file_path = os.path.join(root, file)
                print(f"Found file: {file_path}")  # Debugging log

                if file.lower().endswith('.zip'):  # Handle zipped folders
                    print(f"Processing zip file: {file_path}")  # Debugging log
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)  # Extract all contents to the temporary directory
                        zip_patient_id = os.path.splitext(file)[0]  # Extract patient ID from zip file name
                        first_dicom = find_first_dicom(temp_dir, expected_patient_id=zip_patient_id)  # Match PatientID
                        if first_dicom:  # If a DICOM file is found
                            print(f"Found DICOM file in zip: {first_dicom}")  # Debugging log
                            process_dicom_file(first_dicom, anon_keys, counter)
                            counter = len(anon_keys) + 1  # Update counter after processing

                elif file.lower().endswith('.dcm'):  # Handle individual DICOM files
                    print(f"Processing DICOM file: {file_path}")  # Debugging log
                    process_dicom_file(file_path, anon_keys, counter)
                    counter = len(anon_keys) + 1  # Update counter after processing

        # Write the keys to a CSV file
        with open(output_csv, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["PatientID", "AnonID"])  # Write header
            for patient_id, anon_id in anon_keys.items():
                writer.writerow([patient_id, anon_id])

    finally:
        shutil.rmtree(temp_dir)  # Clean up the temporary directory at the end
        print("Temporary directory cleaned up.")  # Debugging log


def find_first_dicom(directory, expected_patient_id=None):
    """
    Recursively search for the first valid DICOM file in a directory.
    If expected_patient_id is provided, ensure the DICOM file matches it.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Attempt to read the file as a DICOM file
                dicom_data = pydicom.dcmread(file_path)
                patient_id = dicom_data.get("PatientID", None)

                # If expected_patient_id is provided, ensure it matches
                if expected_patient_id:
                    if patient_id == expected_patient_id:
                        return file_path
                else:
                    return file_path  # Return the first valid DICOM file
            except:
                continue  # Skip files that are not valid DICOM files
    return None  # Return None if no matching DICOM file is found


def process_dicom_file(dicom_path, anon_keys, counter):
    """
    Process a single DICOM file to extract PatientID and create an anonymized key.
    """
    try:
        dicom_data = pydicom.dcmread(dicom_path)
        patient_id = dicom_data.get("PatientID", None)

        if patient_id:
            print(f"Extracted PatientID: {patient_id} from {dicom_path}")  # Debugging log
            if patient_id not in anon_keys:
                anon_keys[patient_id] = f"A{counter}" # Keys logic
        else:
            print(f"No PatientID found in {dicom_path}")  # Debugging log
    except Exception as e:
        print(f"Error reading file {dicom_path}: {e}")

# usage
input_directory = 'E:/AphCM_Beckys_list/ApHCM/ApHCM'
output_csv_file = 'keys/ApHCM_simple_keys.csv'
create_anon_keys(input_directory, output_csv_file)