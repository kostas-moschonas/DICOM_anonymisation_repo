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

# --- USER DEFINED VARIABLES ---
# Source directory
mrn_dir = "../mava_research_missing"

# Destination directory (will create folder if it does not exist)
anon_dir = "../Anonymised_research_scans/mava_missing"

# CSV file with AnonID keys
keys_df = pd.read_csv("keys/keys_mava_20250320.csv", dtype=str)

# Name and path of metadata CSV
extracted_metadata_path = "metadata/missing_scans_20250411.csv"

# --- RUNNING CODE ---
# 1. Export metadata from DICOM files before anonymising -------------------
# Extract metadata
## Create a set of valid MRNs from the key file
# Extract metadata
valid_mrns = set(keys_df['mrn'])
sample_cmrs = MetadataExtraction(mrn_dir)
sample_cmrs.extract_metadata(valid_mrns)

# Match AnonID keys
metadata_df = sample_cmrs.metadata
metadata_df['AnonID'] = metadata_df['mrn'].map(keys_df.set_index('mrn')['AnonID'])

# Name and destination of metadata CSV
metadata_df.to_csv(extracted_metadata_path, index=False)

# 2. Anonymise DICOM data -------------------
anonymiser = Anonymisation()
# Copy and rename folders
anonymiser.copy_directory_and_rename_mainfolders(mrn_dir, anon_dir, metadata_df)
# Anonymise DICOM tags in place
anonymiser.anonymise_dicom_tags(anon_dir, metadata_df)
