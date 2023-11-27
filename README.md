# PDF Image Extractor

### Dependencies
* [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/installation.html) v1.23.5+
* [PySimpleGUI](https://www.pysimplegui.org/en/latest/#install) v4.60.5+
* [PyInstaller](https://pyinstaller.org/en/stable/installation.html) (Optional)

To compile as a standalone executable using PyInstaller:  
`pyinstaller extract_image_from_pdf.py --onefile --windowed`

## What is this?
![PDF Image Extractor](preview.png)
* A simple script using the [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) wrapper library to extract images.
* Has a graphical UI using [PySimpleGUI](https://www.pysimplegui.org/en/latest/call%20reference/).
* Can be built as a standalone executable using [PyInstaller](https://pyinstaller.org/en/stable/).


*Note:* Code may be unoptimized and contain bugs.
## How to run
1. Clone the project:  
`git clone https://github.com/Captain-Chen/PDF_Image_Extractor.git`  
2. Run the script:  
`python extract_image_from_pdf.py`
3. Browse for the PDF file you want to extract images from.
4. Click Start and wait for the process to finish.
5. An `extracted_images` folder will be created in the same location where the application is run. There will be subfolders named after the PDFs containing the extracted images.
6. You may then select another PDF to begin the process again or exit the application.
