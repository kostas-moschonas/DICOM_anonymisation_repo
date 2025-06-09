# PowerShell script to zip each folder in a directory individually
$sourceDir = "E:\unzipped_folders"  # Path to the directory containing folders to zip
$destinationDir = "E:\zipped_folders"  # Path to save the zipped files

# Ensure the destination directory exists
if (!(Test-Path -Path $destinationDir)) {
    New-Item -ItemType Directory -Path $destinationDir
}

# Compress each folder in the source directory
Get-ChildItem -Path $sourceDir -Directory | ForEach-Object {
    $folderName = $_.Name
    $zipPath = Join-Path -Path $destinationDir -ChildPath "$folderName.zip"
    Compress-Archive -Path $_.FullName -DestinationPath $zipPath
}

Write-Host "All folders in $sourceDir have been zipped to $destinationDir."