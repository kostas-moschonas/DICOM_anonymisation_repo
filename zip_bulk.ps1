# PowerShell script to zip each folder inside a directory
$sourceDir = "E:\research_scans_anonymised\ApHCM_Becky_simple_anonymisation"
$destinationDir = "E:\research_scans_anonymised\ApHCM_Becky_zipped"

# Ensure the destination directory exists
if (-not (Test-Path -Path $destinationDir)) {
    New-Item -ItemType Directory -Path $destinationDir
}

# Get all folders in the source directory
Get-ChildItem -Path $sourceDir -Directory | ForEach-Object {
    $folderName = $_.Name
    $zipPath = Join-Path -Path $destinationDir -ChildPath "$folderName.zip"

    # Create a zip file for the folder
    Compress-Archive -Path $_.FullName -DestinationPath $zipPath
}

Write-Host "All folders have been zipped into $destinationDir."