# PDF Image Extractor

## What is this?
![PDF Image Extractor](preview.png)
* A simple script using the [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) wrapper library to extract images.
* Has a graphical UI using [PySimpleGUI](https://www.pysimplegui.org/en/latest/call%20reference/).
* Can be built as a standalone executable using [PyInstaller](https://pyinstaller.org/en/stable/).

## Why?
I read a lot of PDFs that often contain beautiful photographs of plants that I want to quickly share with a friend. I could just take a screenshot however this results in an image with lower resolution and blurred details. I could also just directly send the PDF itself however I am often limited by file upload size restrictions. Thus I wanted to see if there was a way to extract the images embedded in the PDF without compromising on image resolution. This program is a result of that investigation.

## How to install and run
1. Clone the project:  
`git clone https://github.com/Captain-Chen/PDF_Image_Extractor.git`
2. Install the dependencies: `python -m pip install -r requirements.txt`
2. Decide whether you want to run the script directly or compile as a standlone executable.
    * To run the script: 
    `python extract_image_from_pdf.py`  
    * To compile as a standalone executable using [PyInstaller](https://pyinstaller.org/en/stable/installation.html):
        * Install PyInstaller: `python -m pip install pyinstaller`
        * Run: `pyinstaller extract_image_from_pdf.py --onefile --windowed && cd dist`
        * Open the `extract_image_from_pdf.exe` inside the `dist` folder. You may run this executable from anywhere on your machine.
3. Browse for the PDF file you want to extract images from.
4. Press `Start` and wait for the process to finish.
5. An `extracted_images` folder will be created in the same location where the application is run. There will be subfolders named after the PDFs containing the extracted images.
6. You may then select another PDF to begin the process again or exit the application.

*Note:* Code may be unoptimized and contain bugs.

### Dependencies
* [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/installation.html) v1.23.5+
* [PySimpleGUI](https://www.pysimplegui.org/en/latest/#install) v4.60.5+
* [PyInstaller](https://pyinstaller.org/en/stable/installation.html) (Optional)