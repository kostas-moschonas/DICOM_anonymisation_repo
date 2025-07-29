"""
Main script for extracting metadata and anonymizing DICOM files.

Steps:
1. Extract metadata from DICOM files and save it to a CSV.
2. Copy and rename directories for anonymization.
3. Anonymize sensitive DICOM tags in-place.

Author: Kostas Moschonas
Date: 11-04-2025
"""

from anonymise_dicoms import MetadataExtraction, Anonymisation
from unzip import ZipFolderHandler
import pandas as pd
import os

# --- USER DEFINED VARIABLES ---
# Source directory
mrn_dir = r"E:\ApHCM_main\main_list_NOT_anonymised"

# Destination directory (will create folder if it does not exist)
anon_dir = r"E:\ApHCM_main\main_list"

# CSV file with AnonID keys
keys_df = pd.read_csv("keys/keys_ApHCM.csv", dtype=str)

# Name and path of metadata CSV
extracted_metadata_path = "metadata/ApHCM_all.csv"

# --- RUNNING CODE ---
# IF NEEDED,
zip_handler = ZipFolderHandler(mrn_dir, anon_dir)
zip_handler.process_all_zipped_folders()

# 1. Export metadata from DICOM files before anonymizing -------------------
# Extract metadata
valid_mrns = set(keys_df['mrn'])
metadata_extractor = MetadataExtraction(mrn_dir)
metadata_df = metadata_extractor.extract_metadata(valid_mrns)

# Match AnonID keys
metadata_df['AnonID'] = metadata_df['mrn'].map(keys_df.set_index('mrn')['AnonID'])

# Save metadata to CSV
metadata_df.to_csv(extracted_metadata_path, index=False)
print(f"Metadata saved to {extracted_metadata_path}")

# 2. Anonymize DICOM data -------------------
anonymiser = Anonymisation()

# Copy directory, uncomment if used zip class above and files are already copied
# anonymiser.copy_directory(mrn_dir, anon_dir)

# Rename main folders
anonymiser.rename_mainfolders(anon_dir, metadata_df)

# Anonymize DICOM tags in place
if anonymiser.anonymise_dicom_tags(anon_dir, metadata_df):
    print("Anonymization completed successfully.")
else:
    print("An error occurred during anonymization.")