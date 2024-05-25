@echo off
REM Set the input and output folders
set input_folder=C:\Users\tamer\OneDrive\Documents\docsAutomation\rawDeliveryDocs
set output_folder=C:\Users\tamer\OneDrive\Documents\docsAutomation\scannedDeliveryDocs

REM Set the path to the Tesseract executable
set TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

REM Run the executable with the specified input and output folders and Tesseract path
main.exe %input_folder% %output_folder% "%TESSERACT_PATH%"

pause
