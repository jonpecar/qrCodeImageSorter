from qr_generator import load_text_file
from qr_generator import print_struct_outline
from photo_sorter import sort_directory
from write_pdf import build_data_table, build_pdf_report
import os

IM_PATH = r'C:\Users\Jonat\repos\qrCodeImageSorter\test_images'
IM_PATH_OUT = r'C:\Users\Jonat\repos\qrCodeImageSorter\test_images_out'
TEXT_FILE = r'C:\Users\Jonat\repos\qrCodeImageSorter\demo_list.txt'

def main():
    # print('Loading: ' + TEXT_FILE)
    # data = load_text_file(TEXT_FILE)
    # print('')
    # print('Loaded data:')
    # print_struct_outline(data)
    # build_pdf_report(data, 'test.pdf', False)
    sort_directory(IM_PATH, IM_PATH_OUT)

if __name__ == '__main__':
    main()