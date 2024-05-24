@echo off
set input_folder=C:\Users\tamer\OneDrive\Documents\docsAutomation\rawDeliveryDocs
set output_folder=C:\Users\tamer\OneDrive\Documents\docsAutomation\scannedDeliveryDocs

REM Run the executable with the specified input and output folders
main.exe %input_folder% %output_folder%

pause