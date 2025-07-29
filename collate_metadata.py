"""Concise script to collate extracted metadata during the anonymisation process
for use in the analysis pipeline. """

import os
import pandas as pd

folder_name = 'metadata'
name_component = 'mava'

# Get all CSV files in the folder containing the name component
csv_files = [
    os.path.join(folder_name, file_name)
    for file_name in os.listdir(folder_name)
    if file_name.endswith('.csv') and name_component.lower() in file_name.lower()
]

# Read and concatenate all CSV files
combined_data = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_data.to_csv(os.path.join(folder_name, "mavacamten_metadata_collated_20250611.csv"), index=False)