import os
import sys
import fitz
import PySimpleGUI as sg
from time import time

EXTRACTED_IMAGES_DIRECTORY = 'extracted_images'

if getattr(sys, 'frozen', False):
    application_path = os.path.abspath('.')
else:
    application_path = os.path.dirname(__file__)
extracted_images_path = os.path.join(application_path, EXTRACTED_IMAGES_DIRECTORY)

layout = [
        [sg.Text("Choose a PDF to extract images from", key='text_prompt')],
        [sg.Input(readonly=True), sg.FileBrowse('Browse', key='file_path', file_types=(('PDF', '*.pdf'), ('All types', '*.*')))],
        [sg.Ok('Start', key='start_button'), sg.Exit(key='exit_button')],
        [sg.pin(sg.Text("", key='xref_count', visible=False))],
        [sg.pin(sg.Text("", key='image_count', visible=False))],
        [sg.ProgressBar(
            100,
            key='progress_bar',
            orientation='h',
            visible=False,
            size=(34, 1),
        )],
        [sg.pin(sg.Text(None, key='results', visible=False))],
    ]
SCALE_FACTOR=1.25
sg.set_options(scaling=SCALE_FACTOR)
window = sg.Window('',
                   layout,
                   no_titlebar=True,
                   keep_on_top=True,
                   grab_anywhere=True,
                   resizable=False)

progress_bar = window['progress_bar']
object_count = window['xref_count']
image_count = window['image_count']
results = window['results']
start_key = window['start_button']
exit_key = window['exit_button']
browse_key = window['file_path']
smasks = set()
valid_formats = {'png', 'pnm', 'pgm', 'ppm', 'pbm', 'pam', 'psd', 'ps', 'jpg', 'jpeg'}

def recover_pix(doc, xref: int, item: dict):
    """
    Returns an image dictionary for a given xref number
    """
    xref_object = doc.xref_object(xref, compressed=True)
    img_ext = item['ext']

    # If the image dictionary has an smask xref then we will need to reconstruct the image using pixel maps
    if (smask := item['smask']):
        pix0 = fitz.Pixmap(item['image']) # pixmap without alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)['image']) # pixmap of the mask

        pix = fitz.Pixmap(pix0) # copy of pix0 with an added alpha channel
        pix.set_alpha(mask.samples) # use the alpha values from mask to write into the alpha channel

        return {
            'ext': 'png',
            'colorspace': pix.colorspace.n,
            'image': pix.tobytes('png')
        }

    # If it does not have an smask xref but it's still an ImageMask we reconstruct the image using a pixel map and return it
    if '/ImageMask' in xref_object:
        pix = fitz.Pixmap(doc, xref)
        return {
            'ext': 'png',
            'colorspace': None,
            'image': pix.tobytes('png')
        }

    # Otherwise we will force convert the image into RGB
    if '/ColorSpace' in xref_object:
        pix0 = fitz.Pixmap(doc, xref) # reconstruct the image using a pixel map. We do not use the byte stream here.
        pix = fitz.Pixmap(fitz.csRGB, pix0) # convert to RGB colorspace
        img_ext = 'jpg' if 'jp' in img_ext else 'png'

        return {
            'ext': img_ext,
            'colorspace': pix.colorspace,
            'image': pix.tobytes(img_ext)
        }

    # If the object doesn't match any of these special cases we process it as is
    return doc.extract_image(xref)

def reset_ui():
    results.update(visible=False)
    start_key.update(disabled=False)
    browse_key.update(disabled=False)
    object_count.update(visible=False)
    image_count.update(visible=False)
    progress_bar.update(visible=False)

def toggle_ui():
    start_key.update(disabled=not start_key.Disabled)
    browse_key.update(disabled=not browse_key.Disabled)
    object_count.update(visible=not object_count.visible)
    progress_bar.update(visible=not progress_bar.visible)

def update_ui(message: str=None):
    results.update(message, visible=True)
    start_key.update(disabled=False)
    browse_key.update(disabled=False)
    exit_key.update('Exit')

def save_file(filepath: str, file_extension: str, file_data: bytes):
    with open(f"{filepath}.{file_extension}", 'wb', encoding=None) as file:
        file.write(file_data)

while True:
    event, values = window.read()
    reset_ui()
    t0 = time()

    if event == 'exit_button':
        raise SystemExit()

    if not (pdf_filename := values.get('file_path')):
        continue

    doc = fitz.open(pdf_filename)
    xref_count = doc.xref_length() # length of objects table
    img_count = 0
    toggle_ui()
    exit_key.update('Cancel')

    for xref in range(1, xref_count): # skip the 1st entry (object 0) which is reserved
        event, values = window.read(timeout=1) # by setting a timeout, we are still able to interact with the UI during image processing
        progress_bar.update(xref+1, xref_count)
        object_count.update(f"Scanning {xref+1} of {xref_count} objects")

        if event == 'exit_button':
            update_ui("Job was interrupted.")
            break

        # If it's not an image we skip processing for this object
        if '/Image' not in doc.xref_object(xref, compressed=True):
            continue

        # Likewise if we have seen this object before and know it's a mask, we skip processing it
        if xref in smasks:
            continue

        # Finally if Document.extract_image(xref) does not return a dictionary then it is not an image, so we skip processing it
        if not (img_dict := doc.extract_image(xref)):
            continue

        img_count += 1
        if not image_count.visible:
            image_count.update(visible=True)
        image_count.update(f"Found {img_count} images to be processed")

        # if the extracted images folder doesn't exist, create it
        if not os.path.exists(extracted_images_path):
            os.mkdir(extracted_images_path)

        # create subfolder with PDF's name to save extracted images into
        base_pdf_filename = os.path.basename(os.path.splitext(pdf_filename)[0])
        subfolder_path = os.path.join(extracted_images_path, base_pdf_filename)
        if not os.path.exists(subfolder_path):
            os.mkdir(subfolder_path)

        # prep the file name with appropriate file extension
        img_filename = os.path.join(subfolder_path, f"img_{xref}")

        img_ext = img_dict['ext']
        img_bytes = img_dict['image']
        smask = img_dict['smask']
        colorspace_n = img_dict['colorspace']
        # See if there is an smask xref, if there is one we add it to the set to avoid reprocessing it later
        if smask > 0:
            smasks.add(smask)
            img_dict = recover_pix(doc, xref, img_dict)
        else:
            if img_ext not in valid_formats:
                img_dict = recover_pix(doc, xref, img_dict)
                img_ext = img_dict['ext']
                img_bytes = img_dict['image']
            elif colorspace_n == fitz.csCMYK.n:
                pix0 = fitz.Pixmap(doc, xref) # reconstruct the image using a pixel map. We do not use the byte stream here.
                pix = fitz.Pixmap(fitz.csRGB, pix0) # convert to RGB colorspace
                img_bytes = pix.tobytes(img_ext) # return the byte data
        save_file(img_filename, img_ext, img_bytes)
    t1 = time()
    if event != 'exit_button':
        update_ui(f"Finished scanning and extracting images. Job took {t1 - t0:.2f} seconds.")