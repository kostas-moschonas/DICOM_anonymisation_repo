"""
This script processes and anonymizes DICOM files for research purposes. It includes the following functionalities:

1. Metadata Extraction:
   - Extracts metadata from DICOM files in a directory structure.
   - Filters metadata based on valid MRNs and saves it to a CSV file.

2. Anonymization:
   - Copies and renames directories based on anonymized IDs and formatted dates.
   - Anonymizes sensitive DICOM tags in-place while preserving the directory structure.

Modules:
- `MetadataExtraction`: Handles metadata extraction from DICOM files.
- `Anonymisation`: Manages directory renaming and DICOM tag anonymization.

Author: Kostas Moschonas
Date: 11-04-2025
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

    def _find_all_tags(self, dataset, tag_keyword):
        """
        Recursively find all occurrences of a specified tag in a DICOM dataset.

        Args:
            dataset (pydicom.dataset.Dataset): The DICOM dataset to search.
            tag_keyword (str): The DICOM tag keyword to search for.

        Returns:
            list: A list of all values found for the specified tag.
        """
        values = []
        for elem in dataset:
            if elem.VR == "SQ":  # If the element is a sequence, recurse into it
                for item in elem.value:
                    values.extend(self._find_all_tags(item, tag_keyword))  # Use self._find_all_tags
            elif elem.keyword == tag_keyword:  # Check if the tag matches
                values.append(elem.value)
        return values

    def _extract_metadata_from_dicom(self, filepath: str, valid_mrns: set) -> Dict:
        """
        Extract metadata from a DICOM file, including handling nested PatientID tags.

        Args:
            filepath (str): Path to the DICOM file.
            valid_mrns (set): Set of valid MRNs to match against.

        Returns:
            Dict: Extracted metadata or None if an error occurs.
        """
        try:
            dcm = pydicom.dcmread(filepath)
            patient_ids = self._find_all_tags(dcm, "PatientID")  # Use self._find_all_tags

            # Match the correct MRN
            correct_patient_id = 'NA'
            for patient_id in patient_ids:
                if patient_id in valid_mrns:
                    correct_patient_id = patient_id
                    break

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

    def _anonymize_tags(self, dataset, tag_replacements):
        """
        Recursively anonymize specified tags in a DICOM dataset.

        Args:
            dataset (pydicom.dataset.Dataset): The DICOM dataset to anonymize.
            tag_replacements (dict): A dictionary of tag keywords and their replacement values.
        """
        for elem in dataset:
            if elem.VR == "SQ":  # If the element is a sequence, recurse into it
                for item in elem.value:
                    self._anonymize_tags(item, tag_replacements)  # Use self._anonymize_tags
            elif elem.keyword in tag_replacements:  # Check if the tag matches
                elem.value = tag_replacements[elem.keyword]

    def anonymise_dicom_tags(self, anon_dir: str, df: pd.DataFrame):
        """
        Anonymizes DICOM files in place within the specified directory.

        Args:
            anon_dir (str): Path to the directory containing anonymized DICOM files.
            df (pd.DataFrame): DataFrame containing metadata and anonymization mappings.
        """
        for _, row in df.iterrows():
            study_dir_path = os.path.join(anon_dir, f"{row['AnonID']}_{row['formatted_date']}")

            if not os.path.exists(study_dir_path):
                print(f"Warning: Directory not found: {study_dir_path}")
                continue

            for root, _, files in os.walk(study_dir_path):
                for file in files:
                    dcm_file_path = os.path.join(root, file)
                    try:
                        ds = pydicom.dcmread(dcm_file_path)

                        # Define replacements for anonymization
                        tag_replacements = {
                            'PatientName': str(row['AnonID']),
                            'PatientID': str(row['AnonID']),
                        }

                        # Empty other sensitive tags
                        empty_tags = [
                            'PatientBirthDate', 'PhysicianOfRecord', 'PhysiciansOfRecord',
                            'RequestingPhysician', 'PerformingPhysicianName', 'OperatorName',
                            'OperatorsName', 'InstitutionAddress', 'ReferringPhysicianName',
                            'OtherPatientIDs', 'ReferencedStudySequence', 'StudyID',
                            'PatientTelephoneNumber', 'InstitutionName'
                        ]
                        for tag_name in empty_tags:
                            tag_replacements[tag_name] = ''

                        # Anonymize tags recursively
                        self._anonymize_tags(ds, tag_replacements)

                        ds.save_as(dcm_file_path)
                        print(f"Anonymized: {dcm_file_path}")

                    except Exception as e:
                        print(f"Error anonymizing {dcm_file_path}: {e}")
                        return False  # Stop on error

        return True
