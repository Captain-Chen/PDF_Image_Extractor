import FreeSimpleGUI as sg
from extractor import PDFImageExtractor

from time import time

class PDFImageExtractorUI:
    def __init__(self):
        self.extractor = PDFImageExtractor()
        self.window = self.create_window()
        
    def create_window(self):
        layout = [
            [sg.Text("Choose a PDF to extract images from", key='text_prompt')],
            [sg.Input(readonly=True), sg.FileBrowse('Browse', key='file_path', 
                     file_types=(('PDF', '*.pdf'), ('All types', '*.*')))],
            [sg.Ok('Start', key='start_button'), sg.Exit(key='exit_button')],
            [sg.pin(sg.Text("", key='xref_count', visible=False))],
            [sg.pin(sg.Text("", key='image_count', visible=False))],
            [sg.ProgressBar(100, key='progress_bar', orientation='h',
                          visible=False, size=(34, 1))],
            [sg.pin(sg.Text('', key='results', visible=False))]
        ]
        
        sg.set_options(scaling=1.25)
        return sg.Window('', layout, no_titlebar=True,
                        keep_on_top=True, grab_anywhere=True, resizable=False)
    
    def run(self):
        while True:
          event, values = self.window.read(timeout=1)

          if event == 'exit_button':
              self.display_results("Job was interrupted.")
              raise SystemExit()
          
          if not values.get('file_path'):
              continue
          
          if event == 'start_button':
              self.window['exit_button'].update("Cancel")
              self.process_pdf(values['file_path'])
    
    def process_pdf(self, pdf_path):
        self.reset_ui()
        self.toggle_ui(True)
        try:
          t0 = time()
          image_count = self.extractor.extract_images(pdf_path, progress_callback=self.update_progress)
          t1 = time()
          self.display_results(f"Extracted {image_count} images. Job took {t1 - t0:.2f} seconds")
        except Exception as e:
            self.display_results(f"Error: {str(e)}")
        finally:
            self.toggle_ui(False)

    def update_progress(self, current, total):
        self.window['progress_bar'].update(current+1, total)
        self.window['xref_count'].update(f"Scanning object {current} out of {total}")

    def reset_ui(self):
        self.window['results'].update(visible=False)

    def toggle_ui(self, is_processing):
        self.window['start_button'].update(disabled=is_processing)
        self.window['file_path'].update(disabled=is_processing)
        self.window['progress_bar'].update(visible=is_processing)
        self.window['xref_count'].update(visible=is_processing)

    def display_results(self, message):
        self.window['results'].update(message, visible=True)