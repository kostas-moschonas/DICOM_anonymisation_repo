"""
DICOM Anonymization Script
def extract_metadata(self) -> pd.DataFrame:
    study_dir_names = []
    mrn, dob, sex, date, time, height, weight = [], [], [], [], [], [], []
    scanner_id, study_instance_uids, file_paths = [], [], []

    for study_dir in next(os.walk(self.root_directory))[1]:
        study_path = os.path.join(self.root_directory, study_dir)
        for root, _, files in os.walk(study_path):
            for file in files:
                if file.lower().endswith((".dcm", ".ima")):
                    filepath = os.path.join(root, file)
                    dicom_metadata = self._extract_metadata_from_dicom(filepath)
                    if dicom_metadata is None:
                        continue

                    study_dir_names.append(study_dir)
                    mrn.append(dicom_metadata['mrn'])
                    dob.append(dicom_metadata['dob'])
                    sex.append(dicom_metadata['sex'])
                    date.append(dicom_metadata['date'])
                    time.append(dicom_metadata['time'])
                    height.append(dicom_metadata['height'])
                    weight.append(dicom_metadata['weight'])
                    scanner_id.append(dicom_metadata['scanner_id'])
                    study_instance_uids.append(dicom_metadata['StudyInstanceUID'])
                    file_paths.append(filepath)

    df = pd.DataFrame({
        'AnonID': [''] * len(study_dir_names),
        'StudyDirName': study_dir_names,
        'mrn': mrn, 'dob': dob, 'sex': sex, 'date': date,
        'time': time, 'StudyInstanceUID': study_instance_uids,
        'height': height, 'weight': weight, 'scanner_id': scanner_id,
        'FilePath': file_paths,
    })
    self.metadata = self._convert_column_formats(df)
    return self.metadata
This script extracts metadata from DICOM files in a specified directory structure,
creates an anonymized copy of the directory, and anonymizes the DICOM files
in place within the copied directory.

Functionality:

- `MetadataExtraction`: Extracts metadata from DICOM files and stores it in a Pandas DataFrame.
- `Anonymisation`:  Handles the creation of the anonymized directory structure and the in-place anonymization of DICOM files.

Usage:

1.  Modify the `mrn_dir` and `anon_dir` variables in the
    `if __name__ == '__main__':` block to point to your source and
    destination directories, respectively.
2.  Provide your own logic for generating and assigning `AnonID` values
    to the DataFrame. The example code provides a very basic placeholder
    that you *must* replace.

Assumptions:

1. The input directory structure is:
    `root_directory/study_directory/subfolder/dicom_file.dcm`
  Where `root_directory` is the `mrn_dir` you specify.
2. DICOM files have the extensions `.dcm` or `.ima`.

Example:

```python
# (Simplified example - see full code for details)
from your_script_name import MetadataExtraction, Anonymisation  # Assuming you save as your_script_name.py

mrn_dir = "cmrs"
anon_dir = "cmrs_anon"

sample_cmr_folder = MetadataExtraction(mrn_dir)
metadata_df = sample_cmr_folder.extract_metadata()
sample_cmr_folder.save_metadata_to_csv()

metadata_df['AnonID'] = ... # REPLACE WITH YOUR ANONYMIZATION ID LOGIC

anonymiser = Anonymisation()
anonymiser.create_and_restructure_anon_dir(mrn_dir, anon_dir, metadata_df)
anonymiser.anonymize_dicom_directory_in_place(anon_dir, metadata_df)

By: Kostas Moschonas
20/03/2025
"""

import pydicom
import pandas as pd
import os
import shutil
from typing import List, Dict

def convert_date_format(date_series: pd.Series) -> pd.Series:
    """Converts a Pandas Series of dates from YYYYMMDD to YYYYMMDD format."""
    return pd.to_datetime(date_series, format='%Y%m%d', errors='coerce').dt.strftime('%Y%m%d')


class MetadataExtraction:
    """
    Extracts metadata from DICOM files in a directory structure.
    """

    def __init__(self, root_directory: str):
        if not os.path.isdir(root_directory):
            raise ValueError(f"Invalid root directory: {root_directory}")
        self.root_directory = root_directory
        self.metadata = None

    def _extract_metadata_from_dicom(self, filepath: str, valid_mrns: set) -> Dict:
                        try:
                            dcm = pydicom.dcmread(filepath)
                            patient_ids = dcm.get('PatientID', 'NA')

                            # Handle multiple PatientIDs
                            if isinstance(patient_ids, list):
                                for patient_id in patient_ids:
                                    if patient_id in valid_mrns:
                                        correct_patient_id = patient_id
                                        break
                                else:
                                    correct_patient_id = 'NA'  # No match found
                            else:
                                correct_patient_id = patient_ids if patient_ids in valid_mrns else 'NA'

                            return {
                                'mrn': correct_patient_id,
                                'dob': dcm.get('PatientBirthDate', 'NA'),
                                'sex': dcm.get('PatientSex', 'NA'),
                                'date': dcm.get('StudyDate', 'NA'),
                                'time': dcm.get('StudyTime', 'NA'),
                                'height': dcm.get('PatientSize', 'NA'),
                                'weight': dcm.get('PatientWeight', 'NA'),
                                'scanner_id': dcm.get('DeviceSerialNumber', 'NA'),
                                'StudyInstanceUID': dcm.get('StudyInstanceUID', 'NA'),
                            }
                        except (pydicom.errors.InvalidDicomError, Exception) as e:
                            print(f"Error reading DICOM {filepath}: {e}")
                            return None

    def extract_metadata(self, valid_mrns: set) -> pd.DataFrame:
                        study_dir_names = []
                        mrn, dob, sex, date, time, height, weight = [], [], [], [], [], [], []
                        scanner_id, study_instance_uids, file_paths = [], [], []

                        for study_dir in next(os.walk(self.root_directory))[1]:
                            study_path = os.path.join(self.root_directory, study_dir)
                            try:
                                # Check for subdirectories
                                sub_dirs = next(os.walk(study_path))[1]
                                if sub_dirs:
                                    # Process the first file in the first subdirectory
                                    first_sub_dir = sub_dirs[0]
                                    first_file = next(os.walk(os.path.join(study_path, first_sub_dir)))[2][0]
                                    filepath = os.path.join(study_path, first_sub_dir, first_file)
                                else:
                                    # Process the first DICOM file directly in the study directory
                                    first_file = next(os.walk(study_path))[2][0]
                                    filepath = os.path.join(study_path, first_file)
                            except (IndexError, StopIteration):
                                print(f"Skipping directory (no files): {study_path}")
                                continue

                            dicom_metadata = self._extract_metadata_from_dicom(filepath, valid_mrns)
                            if dicom_metadata is None:
                                continue

                            study_dir_names.append(study_dir)
                            mrn.append(dicom_metadata['mrn'])
                            dob.append(dicom_metadata['dob'])
                            sex.append(dicom_metadata['sex'])
                            date.append(dicom_metadata['date'])
                            time.append(dicom_metadata['time'])
                            height.append(dicom_metadata['height'])
                            weight.append(dicom_metadata['weight'])
                            scanner_id.append(dicom_metadata['scanner_id'])
                            study_instance_uids.append(dicom_metadata['StudyInstanceUID'])
                            file_paths.append(filepath)

                        df = pd.DataFrame({
                            'AnonID': [''] * len(study_dir_names),
                            'StudyDirName': study_dir_names,
                            'mrn': mrn, 'dob': dob, 'sex': sex, 'date': date,
                            'time': time, 'StudyInstanceUID': study_instance_uids,
                            'height': height, 'weight': weight, 'scanner_id': scanner_id,
                            'FilePath': file_paths,
                        })
                        self.metadata = self._convert_column_formats(df)
                        return self.metadata

    def _convert_column_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        str_cols = ['StudyDirName', 'mrn', 'sex', 'StudyInstanceUID', 'FilePath']
        df[str_cols] = df[str_cols].astype(str)
        date_cols = ['dob', 'date']
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
        float_cols = ['height', 'weight']
        df[float_cols] = df[float_cols].apply(pd.to_numeric, errors='coerce')
        df['scanner_id'] = pd.to_numeric(df['scanner_id'], errors='coerce').astype('Int64')
        df['formatted_date'] = convert_date_format(df['date'])
        return df

    def save_metadata_to_csv(self, filename: str = "metadata_cmr_dicom.csv"):
        if self.metadata is None:
            print("No metadata extracted. Run extract_metadata() first.")
            return
        self.metadata.to_csv(filename, index=False)
        print(f"CSV saved: {filename}")


class Anonymisation:
    """
    Handles anonymization of DICOM files, keeping the original directory structure,
    and in-place DICOM tag modification.
    """

    def copy_directory_and_rename_mainfolders(self, mrn_dir: str, anon_dir: str, df: pd.DataFrame):
        """Copies and renames directories for anonymisation."""

        if not os.path.exists(anon_dir):
            os.makedirs(anon_dir)

        # Copy entire mrn_dir to anon_dir
        for item in os.listdir(mrn_dir):
            s = os.path.join(mrn_dir, item)
            d = os.path.join(anon_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)

        # Iterate and rename
        for _, row in df.iterrows():
            old_dir_name = os.path.basename(str(row['StudyDirName']))
            old_dir_path = os.path.join(anon_dir, old_dir_name)
            new_dir_name = f"{row['AnonID']}_{row['formatted_date']}"
            new_dir_path = os.path.join(anon_dir, new_dir_name)

            if not os.path.exists(old_dir_path):
                print(f"Warning: Directory not found for renaming: {old_dir_path}")
                continue

            try:
                os.rename(old_dir_path, new_dir_path)
            except OSError as e:
                print(f"Error renaming: {e}")


    def anonymise_dicom_tags(self, anon_dir: str, df: pd.DataFrame):
        """Anonymises DICOM files in place within the specified directory."""

        for _, row in df.iterrows():
            study_dir_path = os.path.join(anon_dir, f"{row['AnonID']}_{row['formatted_date']}")

            if not os.path.exists(study_dir_path):
                print(f"Warning: Directory not found: {study_dir_path}")
                continue

            for root, _, files in os.walk(study_dir_path):
                for file in files:
                    if file.lower().endswith((".dcm", ".ima")):
                        dcm_file_path = os.path.join(root, file)
                        try:
                            ds = pydicom.dcmread(dcm_file_path)

                            # Empty specified tags
                            empty_tags = [
                                'PatientName',
                                'PatientBirthDate',
                                'PatientID',
                                'PhysicianOfRecord',
                                'PhysiciansOfRecord',
                                'RequestingPhysician',
                                'PerformingPhysicianName',
                                'OperatorName',
                                'OperatorsName',
                                'InstitutionAddress',
                                'ReferringPhysicianName',
                                'OtherPatientIDs',
                                'ReferencedStudySequence',
                                'StudyID',
                                'PatientTelephoneNumber',
                                'InstitutionName'
                            ]
                            for tag_name in empty_tags:
                                if tag_name in ds:
                                    ds.data_element(tag_name).value = ''

                            # Replace PatientName and PatientID
                            ds.PatientName = str(row['AnonID'])
                            ds.PatientID = str(row['AnonID'])

                            ds.save_as(dcm_file_path)
                            print(f"Anonymized: {dcm_file_path}")

                        except Exception as e:
                            print(f"Error anonymizing {dcm_file_path}: {e}")
                            return False  # Stop on error
        return True
