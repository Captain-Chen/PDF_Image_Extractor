import os, sys

import pymupdf

OUTPUT_DIR_NAME = 'extracted_images'

# Check if we are running from within a PyInstaller bundle or from source: https://pyinstaller.org/en/stable/runtime-information.html
if getattr(sys, 'frozen', False):
    application_path = os.path.abspath('.')
else:
    application_path = os.path.dirname(__file__)
extracted_images_path = os.path.join(application_path, OUTPUT_DIR_NAME)

# if the extracted images folder does not exist, create it
if not os.path.exists(extracted_images_path):
    os.mkdir(extracted_images_path)

class PDFImageExtractor:
  def __init__(self, output_dir=OUTPUT_DIR_NAME):
    self.output_dir = output_dir
    self.smasks = set()
    self.valid_formats = {'png', 'pnm', 'pgm', 'ppm', 'pbm', 'pam', 'psd', 'ps', 'jpg', 'jpeg'}

  def is_valid_image(self, doc, xref):
    '''Helper function to determine if an image can be processed'''
    # If it's not an image, we skip processing
    if '/Image' not in doc.xref_object(xref, compressed=True):
      return False
    # If we've already seen this (stencil) object before we skip processing it
    if xref in self.smasks:
      return False
    # If Document.extract_image() does not return a dictionary object then it is probably not an image
    try: 
      doc.extract_image(xref)
    except ValueError:
      return False
    return True

  def extract_images(self, pdf_filename, progress_callback=None):
    doc = pymupdf.open(pdf_filename)
    xref_count = doc.xref_length() # length of objects table
    img_count = 0

    for xref in range(1, xref_count): # the first item is reserved (object 0) and must be skipped over
       if progress_callback:
          progress_callback(xref, xref_count)

       if not self.is_valid_image(doc, xref):
          continue
       
       if (img_obj := self.process_image(doc, xref)):
          img_count += 1
          base_pdf_filename = os.path.basename(os.path.splitext(pdf_filename)[0])
          subfolder_path = os.path.join(extracted_images_path, base_pdf_filename)
          if not os.path.exists(subfolder_path):
             os.mkdir(subfolder_path)

          img_filepath = os.path.join(subfolder_path, f"img_{xref}.{img_obj['ext']}")
          self.save_images(img_filepath, img_obj['image'])
    
    return img_count
        
  def process_image(self, doc, xref):
     """Process the image and handle special cases"""
     img_obj = doc.extract_image(xref)
     
     # Special handling to be done for pseudo-images
     if img_obj['smask'] > 0:
        # We add the stencil mask to the hash set of previously seen ones so we don't end up reprocessing them again
        self.smasks.add(img_obj['smask']) 
        return self.recover_pix(doc, xref, img_obj)
     elif img_obj['ext'] not in self.valid_formats:
        return self.recover_pix(doc, xref, img_obj)
     elif img_obj['colorspace'] == pymupdf.csCMYK.n:
        return self.convert_cmyk_to_rgb(doc, xref, img_obj)
     return img_obj
     
  def recover_pix(self, doc, xref, item):
    """Returns an image dictionary for a given xref number"""
    xref_object = doc.xref_object(xref, compressed=True)
    img_ext = item['ext']

    # If the image object is a stencil mask, we will need to reconstruct the image using pixmaps
    if (smask := item['smask']):
        pix0 = pymupdf.Pixmap(item['image']) # pixmap without alpha channel
        mask = pymupdf.Pixmap(doc.extract_image(smask)['image']) # pixmap of the mask

        pix = pymupdf.Pixmap(pix0) # copy of pix0 with an added alpha channel
        pix.set_alpha(mask.samples) # use the alpha values from mask to write into the alpha channel

        return {
            'ext': 'png',
            'colorspace': pix.colorspace,
            'image': pix.tobytes('png')
        }

    # If it does not have an smask xref but it's still an ImageMask we reconstruct the image using a pixel map and return it
    if '/ImageMask' in xref_object:
        pix = pymupdf.Pixmap(doc, xref)
        return {
            'ext': 'png',
            'colorspace': None,
            'image': pix.tobytes('png')
        }

    # Otherwise we will force convert the image into RGB colorspace
    if '/ColorSpace' in xref_object:
        pix0 = pymupdf.Pixmap(doc, xref) # reconstruct the image using a pixel map. We do not use the byte stream here.
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix0) # convert to RGB colorspace
        img_ext = 'jpg' if 'jp' in img_ext else 'png'

        return {
            'ext': img_ext,
            'colorspace': pix.colorspace,
            'image': pix.tobytes(img_ext)
        }

    # If the object doesn't match any of these special cases we process it as is
    return doc.extract_image(xref)
  
  def convert_cmyk_to_rgb(self, doc, xref, img_obj):
     pix0 = pymupdf.Pixmap(doc, xref)
     pix = pymupdf.Pixmap(pymupdf.csRGB, pix0)

     return {
        'ext': img_obj['ext'],
        'image': pix.tobytes(img_obj['ext']),
        'colorspace': pix.colorspace
     }

  def save_images(self, savepath, file_data: bytes):
    with open(f"{savepath}", 'wb', encoding=None) as file:
      file.write(file_data)