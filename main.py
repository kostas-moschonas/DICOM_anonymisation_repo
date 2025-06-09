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
import pandas as pd
import os

# --- USER DEFINED VARIABLES ---
# Source directory
mrn_dir = "E:/ApHCM_Beckys_list/ApHCM/unzipped_full_names"

# Destination directory (will create folder if it does not exist)
anon_dir = "E:/research_scans_anonymised/ApHCM_Becky_simple_anonymisation"

# CSV file with AnonID keys
keys_df = pd.read_csv("keys/ApHCM_simple_keys.csv", dtype=str)

# Name and path of metadata CSV
extracted_metadata_path = "metadata/mava_anonymised_ApHCM_simple_keys.csv"

# --- RUNNING CODE ---
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

# Copy and rename folders
anonymiser.copy_directory_and_rename_mainfolders(mrn_dir, anon_dir, metadata_df)

# Anonymize DICOM tags in place
if anonymiser.anonymise_dicom_tags(anon_dir, metadata_df):
    print("Anonymization completed successfully.")
else:
    print("An error occurred during anonymization.")