import os
import zipfile

class ZipFolderHandler:
    def __init__(self, source_dir, destination_dir):
        self.source_dir = source_dir
        self.destination_dir = destination_dir

    def process_all_zipped_folders(self):
        # Iterate through all files in the source directory
        for file_name in os.listdir(self.source_dir):
            file_path = os.path.join(self.source_dir, file_name)
            if zipfile.is_zipfile(file_path):
                self._process_single_zip(file_name)

    def _process_single_zip(self, zip_name):
        source_zip_path = os.path.join(self.source_dir, zip_name)
        dest_folder_name = os.path.splitext(zip_name)[0]  # Remove .zip extension
        dest_folder_path = os.path.join(self.destination_dir, dest_folder_name)

        # Create destination folder if it doesn't exist
        os.makedirs(dest_folder_path, exist_ok=True)

        # Extract the zip file into the destination folder
        with zipfile.ZipFile(source_zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder_path)

        print(f"Extracted {zip_name} to {dest_folder_path}")