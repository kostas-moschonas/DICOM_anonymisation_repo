import os
import zipfile
import shutil


class ZipHandler:
    """
    Handles unzipping, anonymizing, and re-zipping folders.
    """

    def __init__(self, zip_dir: str, output_dir: str):
        """
        Initializes the ZipHandler.

        Args:
            zip_dir (str): Directory containing zipped folders.
            output_dir (str): Directory to store unzipped and processed folders.
        """
        self.zip_dir = zip_dir
        self.output_dir = output_dir

    def unzip_folders(self):
        """
        Unzips all zip files in the zip_dir to the output_dir.
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for zip_file in os.listdir(self.zip_dir):
            if zip_file.endswith('.zip'):
                zip_path = os.path.join(self.zip_dir, zip_file)
                extract_path = os.path.join(self.output_dir, os.path.splitext(zip_file)[0])

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Unzipped: {zip_file} to {extract_path}")

    def rezip_folders(self):
        """
        Re-zips all folders in the output_dir back into zip files.
        """
        for folder in os.listdir(self.output_dir):
            folder_path = os.path.join(self.output_dir, folder)
            if os.path.isdir(folder_path):
                zip_path = f"{folder_path}.zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, folder_path)
                            zip_ref.write(file_path, arcname)
                print(f"Re-zipped: {folder_path} to {zip_path}")

    def process_zipped_folders(self, anonymizer):
        """
        Unzips, processes (anonymizes), and re-zips folders.

        Args:
            anonymizer (Anonymisation): Instance of the Anonymisation class to process files.
        """
        self.unzip_folders()

        for folder in os.listdir(self.output_dir):
            folder_path = os.path.join(self.output_dir, folder)
            if os.path.isdir(folder_path):
                print(f"Processing folder: {folder_path}")
                # Call the anonymization logic here
                anonymizer.anonymise_dicom_tags(folder_path, anonymizer.metadata)

        self.rezip_folders()