# PowerShell script to unzip all .zip files in a directory
$zippedDir = "E:\ApHCM_Beckys_list\ApHCM\ApHCM"
$unzippedDir = "E:\ApHCM_Beckys_list\ApHCM\unzipped_full_names"

Get-ChildItem -Path $zippedDir -Filter *.zip | ForEach-Object {
    Expand-Archive -Path $_.FullName -DestinationPath $unzippedDir
}
Write-Host "All zipped folders have been unzipped to $unzippedDir."