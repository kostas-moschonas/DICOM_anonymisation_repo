# DICOM Anonymisation

## Overview
This repository provides tools for processing and anonymizing DICOM files for research purposes. It includes functionalities for extracting metadata, anonymizing sensitive information, and maintaining the original directory structure of the DICOM files.

## Features
1. **Metadata Extraction**:
   - Extracts metadata from DICOM files in a directory structure.
   - Filters metadata based on valid MRNs (Medical Record Numbers).
   - Saves the extracted metadata to a CSV file.

2. **Anonymization**:
   - Copies and renames directories using anonymized IDs and formatted dates.
   - Anonymizes sensitive DICOM tags in-place while preserving the directory structure.

## Project Structure
- `main.py`: The main script to run metadata extraction and anonymization.
- `anonymise_dicoms.py`: Contains the `MetadataExtraction` and `Anonymisation` classes for handling metadata and anonymization tasks.
- `keys/`: Directory containing the CSV file mapping MRNs to anonymized IDs.
- `metadata/`: Directory where extracted metadata CSV files are saved.

## Dependencies
The following Python libraries are required:
- `pydicom`
- `pandas`
- `os`
- `shutil`

Install the dependencies using pip:
```bash
pip install pydicom pandas
```
## Usage
### 1. Prepare Input Data:
- Place the DICOM files in the source directory.
- Provide a CSV file in the `keys/` directory with MRNs mapped to anonymized IDs.

### 2. Run the Script:
- Update the user-defined variables in `main.py`:
  - `mrn_dir`: Path to the source directory containing DICOM files.
  - `anon_dir`: Path to the destination directory for anonymized files.
  - `keys_df`: Path to the CSV file with MRN-to-AnonID mappings.
  - `extracted_metadata_path`: Path to save the extracted metadata CSV.

### Output:
- Extracted metadata is saved as a CSV file in the `metadata/` directory.
- Anonymized DICOM files are saved in the destination directory.

## Notes
- IMPORTANT: Ensure the DICOM tag `Patient ID` is the same as in your `keys.csv` file. In my experience, Patient ID could be either MRN or NHS number, it depends how the DICOMs were exported. Use `pydicom.dcmread` to load a representative DICOM file and check. Modify your `keys` csv file accordingly. This won't affect the anonymisation process or the structure of the DICOM data downstream, since the `Patient ID` tag is always anonymised.
- The script will skip files or directories that do not meet the requirements.

## Author
Kostas Moschonas